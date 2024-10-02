from utils.test_tools import fetch_documents
from retrievers.llama_index.pg_query import index,pg_retriever_query

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