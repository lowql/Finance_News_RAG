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
    neo4j_vector = get_vector_store(node_label="新聞",
                                    index_name="news",
                                    hybrid_search="True",
                                    keyword_index_name="news_content",
                                    text_node_property="content")
    from pipeline.news import News
    pipe = News(code)
    documents = pipe.fetch_documnets()[:2]
    show_documents(documents)
    storage_context = StorageContext.from_defaults(vector_store=neo4j_vector)
    print(f"len of News documents {len(documents)} ")
    VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    
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