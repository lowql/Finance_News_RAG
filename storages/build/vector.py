from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext,Settings
from setup import get_vector_store,get_embed_model,get_llm
Settings.llm = get_llm()
Settings.embed_model = get_embed_model()

from pipeline.cypher_template import CypherTemplate

def build_CypherMapper():
    neo4j_vector = get_vector_store(node_label="CypherMapper")
    documents = CypherTemplate.fetch_documents()
    CypherTemplate.show_documents(documents)
    # neo4j_vector.node_label = "CypherMapper"
    # storage_context = StorageContext.from_defaults(vector_store=neo4j_vector)
    # VectorStoreIndex.from_documents(documents[:2], storage_context=storage_context)

def build_News():
    neo4j_vector = get_vector_store(node_label="新聞")
    neo4j_vector.node_label = "新聞"
    from pipeline.news import News
    pipe = News(6125)
    documents = pipe.fetch_documnets()
    # show_documents(documents)
    storage_context = StorageContext.from_defaults(vector_store=neo4j_vector)
    VectorStoreIndex.from_documents(documents[:2], storage_context=storage_context)
if __name__ == '__main__':
    build_CypherMapper()
# query_engine = index.as_query_engine()
# response = query_engine.query("廣運有哪些競爭對手")
# print(response)