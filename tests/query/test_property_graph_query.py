from utils.test_tools import fetch_documents
from llama_index.llms.ollama import Ollama
from retrievers.llama_index.pg_query import pg_query,graph_store,index,pg_retriever_query

def build_kg_not_clean(neo4j_connection):
    documents = fetch_documents()
    driver = neo4j_connection
    driver.set_prompt_template()
    index = driver.build_index_from_documents(documents=documents)
    return driver,index

def test_structured_query_1():
    graph_store.structured_query("""
        CREATE VECTOR INDEX entity IF NOT EXISTS
        FOR (m:`__Entity__`)
        ON m.embedding
        OPTIONS {indexConfig: {
            `vector.dimensions`:4096,
            `vector.similarity_function`: 'cosine'
        }}
    """)
    graph_store.close()
def test_structured_query_2():
    similarity_threshold = 0.9
    word_edit_distance = 5
    data = graph_store.structured_query("""
        MATCH (e:__Entity__)
        CALL {
        WITH e
        CALL db.index.vector.queryNodes('entity', 10, e.embedding)
        YIELD node, score
        WITH node, score
        WHERE score > toFLoat($cutoff)
            AND (toLower(node.name) CONTAINS toLower(e.name) OR toLower(e.name) CONTAINS toLower(node.name)
                OR apoc.text.distance(toLower(node.name), toLower(e.name)) < $distance)
            AND labels(e) = labels(node)
        WITH node, score
        ORDER BY node.name
        RETURN collect(node) AS nodes
        }
        WITH distinct nodes
        WHERE size(nodes) > 1
        WITH collect([n in nodes | n.name]) AS results
        UNWIND range(0, size(results)-1, 1) as index
        WITH results, index, results[index] as result
        WITH apoc.coll.sort(reduce(acc = result, index2 IN range(0, size(results)-1, 1) |
                CASE WHEN index <> index2 AND
                    size(apoc.coll.intersection(acc, results[index2])) > 0
                    THEN apoc.coll.union(acc, results[index2])
                    ELSE acc
                END
        )) as combinedResult
        WITH distinct(combinedResult) as combinedResult
        // extra filtering
        WITH collect(combinedResult) as allCombinedResults
        UNWIND range(0, size(allCombinedResults)-1, 1) as combinedResultIndex
        WITH allCombinedResults[combinedResultIndex] as combinedResult, combinedResultIndex, allCombinedResults
        WHERE NOT any(x IN range(0,size(allCombinedResults)-1,1) 
            WHERE x <> combinedResultIndex
            AND apoc.coll.containsAll(allCombinedResults[x], combinedResult)
        )
        RETURN combinedResult  
    """, param_map={'cutoff': similarity_threshold, 'distance': word_edit_distance})
    for row in data:
        print(row)
    graph_store.close()   


def test_PropertyGraphIndex():
    query_engine = index.as_query_engine()
    response = query_engine.query("廣運供應商?")
    print(response)
    
import pytest
questions = [
    "廣運的競爭對手?", 
    "廣運的合作夥伴?",
    "廣運跟黃仁勳有關係嗎?",
    "廣運的股東會議發生的哪些事情?"
]
@pytest.mark.parametrize("query_txt", questions)
def test_retriever_pg(query_txt):
    print('-------------------------------',query_txt,'-------------------------------')
    from llama_index.core.response_synthesizers import ResponseMode
    pg_retriever_query(
        query_txt=query_txt,
        response_mode=ResponseMode.NO_TEXT
    )
    
# python -m pytest .\tests\query\test_property_graph_query.py::test_knowledgeGraphQueryEngine
def test_knowledgeGraphQueryEngine():
    from llama_index.core.query_engine import KnowledgeGraphQueryEngine
    from llama_index.core import StorageContext
    from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
    from config.db_config import Neo4j_USER,Neo4j_PWD,Neo4j_URI
    graph_store = Neo4jPropertyGraphStore(
            username=Neo4j_USER,
            password=Neo4j_PWD,
            url=Neo4j_URI,
        )
    storage_context =StorageContext.from_defaults(graph_store=graph_store)
    from llama_index.core.indices.service_context import ServiceContext
    
    """ 
    The LLMPredictor object is no longer intended to be used by users. 
    Instead, you can setup an LLM directly and pass it into the Settings or the interface using the LLM. 
    The LLM class itself has similar attributes and methods as the LLMPredictor.
    """
    service_context = ServiceContext.from_defaults(llm=llm,embed_model=ollama_embedding)
    
    # https://github.com/run-llama/llama_index/issues/13741
    from llama_index.core.prompts.base import PromptTemplate, PromptType
    # Define your custom prompt templates or use existing ones
    graph_query_synthesis_prompt = PromptTemplate(
        "Your graph query synthesis prompt template here",
        prompt_type=PromptType.QUESTION_ANSWER,
    )
    query_engine = KnowledgeGraphQueryEngine(
        service_context=service_context,
        storage_context=storage_context,
        graph_query_synthesis_prompt=graph_query_synthesis_prompt,
        llm=llm,
        verbose=True,
    )
    """ It is recommended to use the PropertyGraphIndex and associated retrievers instead.) -- Deprecated since version 0.10.53.  """  
    

    # AttributeError: 'Neo4jPropertyGraphStore' object has no attribute 'query'
    response = query_engine.query(
        "Tell me about Peter Quill?",
    )
    # graph_query = query_engine.generate_query(
    #     "Tell me about Peter Quill?",
    # )
    print('response: \n',response)

# TODO: 執行時間太久，需要可以切換是否進行本次測試的功能!!!
def test_build_not_clean(neo4j_connection):
    driver,index = build_kg_not_clean(neo4j_connection)
    retriever = index.as_retriever(include_text=False)
    from llama_index.core import PromptTemplate
    text_qa_template = PromptTemplate(driver.text_qa_template)
    refine_template = PromptTemplate(driver.refine_template)
    from llama_index.core import get_response_synthesizer
    synth = get_response_synthesizer(response_mode="refine",streaming=True,refine_template=refine_template,text_qa_template=text_qa_template)
    from llama_index.core.query_engine import RetrieverQueryEngine
        
    from llama_index.core.postprocessor import SimilarityPostprocessor
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer = synth,
        node_postprocessors=[
            SimilarityPostprocessor(similarity_cutoff=0.7)  # 设置相似度阈值
        ]
    )
    query_engine.from_args(
        retriever=retriever,
        response_mode= 'compact',
        verbose=False,
        
    )
    response = query_engine.query("請介紹廣運")
    response.print_response_stream()
    
    for node in response.source_nodes:
        print(f"Content: {node.get_content()}")
            
    print(len(response.source_nodes))
    
def test_template(neo4j_connection):
    driver = neo4j_connection
    driver.set_prompt_template()
    print("\nbelow is kg extract template\n")
    print(f"data type is: {type(driver.kg_extract_templete)}")
    print(driver.kg_extract_templete)
    print("\nbelow is refine template\n")
    print(f"data type is: {type(driver.refine_template)}")
    print(driver.refine_template)
    print("\nbelow is text qa template\n")
    print(f"data type is: {type(driver.text_qa_template)}")
    print(driver.text_qa_template)
    
if __name__ == '__main__':
    test_PropertyGraphIndex()