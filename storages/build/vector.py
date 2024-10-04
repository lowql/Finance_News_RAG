from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext,Settings
from setup import get_vector_store,get_embed_model,get_llm
Settings.llm = get_llm()
Settings.embed_model = get_embed_model()

neo4j_vector = get_vector_store(mode='base')

def fetch_documents():
    documents = []
    from llama_index.core import Document
    # prompt,cypher_query,ideal_response
    with open('./dataset/cypher/CypherQuery_example.csv','r',encoding='utf8') as csvfile:
        import csv
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            documents.append(Document(
                    text=row['cypher_query'],
                    metadata={'user_query':row['prompt']},
                    metadata_seperator="\n",
                    metadata_template="{key} : {value} ",
                    text_template="使用者提問:\n {metadata_str}\n\n對應的cypher回覆:\n {content}",
                ))
    return documents

def show_documents(documents):
    """ 
    檢查 documents 的內實際內容
    """
    from llama_index.core.schema import MetadataMode
    for doc in documents:
        print(doc.get_content(MetadataMode.LLM))
        print("="*100)

def build_CypherMapper():
    documents = fetch_documents()
    neo4j_vector.node_label = "CypherMapper"
    storage_context = StorageContext.from_defaults(vector_store=neo4j_vector)
    VectorStoreIndex.from_documents(documents[:2], storage_context=storage_context)

def build_News():
    neo4j_vector.node_label = "新聞"
    from pipeline.news import Pipeline
    pipe = Pipeline(6125)
    documents = pipe.news_documents()
    # show_documents(documents)
    storage_context = StorageContext.from_defaults(vector_store=neo4j_vector)
    VectorStoreIndex.from_documents(documents[:2], storage_context=storage_context)
build_News()
# query_engine = index.as_query_engine()
# response = query_engine.query("廣運有哪些競爭對手")
# print(response)