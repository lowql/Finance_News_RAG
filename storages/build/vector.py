from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext,Settings
from setup import get_vector_store,get_embed_model,get_llm
Settings.llm = get_llm()
Settings.embed_model = get_embed_model()

from pipeline.utils import show_documents
def build_CypherMapper():
    from pipeline.cypher_template import CypherTemplate
    neo4j_vector = get_vector_store(node_label="CypherMapper")
    documents = CypherTemplate.fetch_documents()
    show_documents(documents)
    neo4j_vector.node_label = "CypherMapper"
    storage_context = StorageContext.from_defaults(vector_store=neo4j_vector)
    VectorStoreIndex.from_documents(documents[:2], storage_context=storage_context)

def build_News(code):
    vector_store = get_vector_store(node_label="新聞")
    from pipeline.news import News
    pipe = News(code)
    documents = pipe.fetch_documnets()[:2]
    # BUG: Noe4j 的 vector store 機制限制比較多，無法直接處理 ingestion pipline 產生的 nested maps structure 
   
    pipe.put_news_to_vector_store(documents=documents,vector_store=vector_store)
    """
        shell# . Neo4j doesn't allow nested maps like this, which is why you're getting the error.
        vector store 無法儲存 kg_dynamic_extractor 的資料因為是嵌套結構需要額外使用
        property graph store 額外處裡
    """
    
if __name__ == '__main__':
    
    from retrievers.vector_query import VectorIndex
    vector_index = VectorIndex(node_label='News',keyword_index_name='keyword',text_node_property="content")
    vector_store = vector_index.get_vector_store()
    nodes =  vector_index.retrieve("統一集團")
    
    for node in nodes:
        print(node)
        print('='*50,"get content",'='*50)

# query_engine = index.as_query_engine()
# response = query_engine.query("廣運有哪些競爭對手")
# print(response)