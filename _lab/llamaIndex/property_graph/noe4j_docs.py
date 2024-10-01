import nest_asyncio
# httpx.ReadTimeout
# sys:1: RuntimeWarning: coroutine 'SchemaLLMPathExtractor._aextract' was never awaited
nest_asyncio.apply()
from llama_index.core import Settings

username = "neo4j"
password = "stockinfo"
url = "bolt://127.0.0.1:7687"
embed_dim = 4096

# embed_model = OpenAIEmbedding(embed_batch_size=42)
from llama_index.embeddings.ollama import OllamaEmbedding
ollama_embedding = OllamaEmbedding(
    model_name="yi",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0}
)
# AttributeError: 'OpenAIEmbedding' object has no attribute '__pydantic_private__'. Did you mean: '__pydantic_complete__'?
Settings.embed_model = ollama_embedding

from llama_index.llms.ollama import Ollama
llm = Ollama(model='yi',request_timeout=360)
Settings.llm = llm


from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
vector_store = Neo4jVectorStore(
    username, 
    password, 
    url, 
    embed_dim,
    index_name="news_index",
    node_label="News",
    # retrieval_query=
)

from llama_index.core import Document
documents = []
with open('./utils/news_crawler/YahooStock/yahoo_news.csv','r',encoding='utf8') as csvfile:
    import csv
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        documents.append(Document(
            text=row['content'],
            metadata={'author':row['author'],'headline':row['headline']},
            metadata_seperator="\n",
            metadata_template="{key} [ {value} ] ",
            text_template="Metadata:\n {metadata_str}\n-----\nContent: {content}",
            ))

from llama_index.core import VectorStoreIndex
index = VectorStoreIndex.from_documents       
def build_vectorindex():
    from llama_index.core import StorageContext
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
    index = VectorStoreIndex.from_documents(
        documents[:3], storage_context=storage_context,
        max_triplets_per_chunk=2,
    )

from llama_index.core import PropertyGraphIndex
index = PropertyGraphIndex.from_documents

from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
graph_store = Neo4jPropertyGraphStore(
    username=username,
    password=password,
    url="bolt://localhost:7687",
)
def build_property_graph_index():
    from llama_index.core.indices.property_graph import SimpleLLMPathExtractor
    from llama_index.core.indices.property_graph import SchemaLLMPathExtractor
    from typing import Literal
    # best practice to use upper-case
    entities = Literal["Company", "News","Items"]
    relations = Literal["有", "研發", "使用", "提及", "影響","有關"]

    # define which entities can have which relations
    validation_schema = {
        "Company": ["研發", "使用"],
        "News": ["影響"],
        "Items": ["有關"],
    }
    max_knowledge_triplets = 10
    neo4j_prompt = (
                "以下提供了一些文本。根據這段文本，提取最多 "
                "{max_knowledge_triplets} "
                "knowledge triplets in the form of (subject, predicate, object). Avoid stopwords.\n"
                "---------------------\n"
                "Example:"
                "Text: 公司A是公司B的客戶"
                "Triplets:\n(公司A, 客戶, 公司B)\n"
                "Text: 公司A的解決方案使用公司B的x技術.\n"
                "Triplets:\n"
                "(公司A, 提供, 解決方案)\n"
                "(公司A, 使用, 公司B的技術)\n"
                "(公司B, 提供, x技術)\n"
                "僅使用正體中文產生輸出"
            )
    neo4j_prompt = neo4j_prompt.format(max_knowledge_triplets=max_knowledge_triplets)
    kg_schema_extractor = SchemaLLMPathExtractor(
        llm=llm,
        strict=True,  # Set to False to showcase why it's not going to be the same as DynamicLLMPathExtractor
        possible_entities=entities,  # USE DEFAULT ENTITIES (PERSON, ORGANIZATION... etc)
        possible_relations=relations,  # USE DEFAULT RELATIONSHIPS
        kg_validation_schema=validation_schema,
        extract_prompt=neo4j_prompt,
        possible_relation_props=[
            "額外備註關係"
        ],  # Set to `None` to skip property generation
        possible_entity_props=[
            "額外備註"
        ],  # Set to `None` to skip property generation
        num_workers=10,
    )

    from llama_index.core.indices.property_graph import DynamicLLMPathExtractor
    """ 
    neo4j.exceptions.ClientError: 
    {code: Neo.ClientError.Procedure.ProcedureCallFailed} 
    {message: Failed to invoke procedure `apoc.create.addLabels`: Caused by: org.neo4j.internal.kernel.api.exceptions.schema.IllegalTokenNameException: '' is not a valid token name. Token names cannot be empty or contain any null-bytes.}
    """
    kg_dynamic_extractor = DynamicLLMPathExtractor(
                llm=llm,
                max_triplets_per_chunk=5,
                num_workers=4,
                allowed_entity_types=["Company", "News","Items"],
                # allowed_relation_types=["有", "研發", "使用", "提及", "影響","有關"],
            )

    # Extract graph from documents


    index = PropertyGraphIndex.from_documents(
        documents[:3],
        use_async = False,
        kg_extractors=[
            # SimpleLLMPathExtractor(llm=llm),
            # kg_extractor,
            kg_dynamic_extractor
        ],
        property_graph_store=graph_store,
        show_progress=True,
            
    )

def display_prompt_dict(prompts_dict):
    for k, p in prompts_dict.items():
        text_md = f"Prompt Key: {k}\n Text:\n"
        print(text_md)
        print(p.get_template(),"\n\n")
if __name__ == '__main__':
    
    # build_vectorindex()
    # build_property_graph_index()
    # load from existing graph/vector store
    index = PropertyGraphIndex.from_existing(
        property_graph_store=graph_store, 
        vector_store=vector_store, 
        embed_kg_nodes=True,
        use_async = False,# httpx.ReadTimeout
    )
    # Define retriever
    retriever = index.as_retriever(
        include_text=False,  # include source text in returned nodes, default True
    )

    # # Question answering
    from llama_index.core import get_response_synthesizer
    
    from llama_index.core import PromptTemplate
    text_qa_template = """
    你現在是資深的市場消息分析師，請根據以下內容使用繁體中文，回覆問題
    請確保你的專業性，回答請根據以下提供的資訊內容
    ```md
    {context_str}
    ```
    Query: {query_str}
    Answer:
    """
    text_qa_template = PromptTemplate(text_qa_template)
    refine_template = """
    以下是原始的內容: {query_str}
    以下是既有回復: {existing_answer}
    請根據以下的額外資訊進一步優化回復內容:
    ```md
    {context_msg}
    ```
    請根據以上內容重新整理出更專業的回覆，如果重新整理的內容不理想，使用原有的內容。
    重新整理的回復:
    """
    refine_template = PromptTemplate(refine_template)
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
    display_prompt_dict(query_engine.get_prompts())
    response = query_engine.query("請介紹廣運")
    response.print_response_stream()
    print("格式化引文:", response.get_formatted_sources())  # 获取格式化的引文
    # print(response.source_nodes)
    for node in response.source_nodes:
        print(f"Node ID: {node.node_id}")
        print(f"Content: {node.get_content()}")
            
    print(len(response.source_nodes))
