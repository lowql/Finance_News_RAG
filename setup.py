from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
def get_embed_model():
    from llama_index.embeddings.ollama import OllamaEmbedding
    ollama_embedding = OllamaEmbedding(
        model_name="yi",
        base_url="http://localhost:11434",
        ollama_additional_kwargs={"mirostat": 0}
    )
    return ollama_embedding

def get_llm():
    from llama_index.llms.ollama import Ollama
    llm = Ollama(model='yi:latest',request_timeout=360)
    return llm

from config.db_config import Neo4j_USER,Neo4j_PWD,Neo4j_URI
def get_graph_store():
    from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
    return Neo4jPropertyGraphStore(
        username=Neo4j_USER,
        password=Neo4j_PWD,
        url=Neo4j_URI,
    )

def get_vector_store(**kwargs):
    """ 
    :params retrieval_query(str): 
    :params node_label(str):  setup for Node label name i.e. MERGE(n:\<_node_label_\>)
    :params index_name(str): setup for vector index
    :params text_node_property(str): setup for fulltext index
    """
    print(kwargs)
    # print(kwargs.get("index_name", "vector"))
    return Neo4jVectorStore(
            username=Neo4j_USER,
            password=Neo4j_PWD,
            url=Neo4j_URI,
            embedding_dimension=4096,
            node_label= kwargs.get("node_label","LlamaChunk"),
            index_name=kwargs.get("index_name", "news_vector"), # 無論怎樣設定都是 vector ，源碼看似沒問題，也可能是我功力不夠
            keyword_index_name=kwargs.get("keyword_index_name", "keyword"),
            text_node_property= kwargs.get("text_node_property", "content"),
            hybrid_search=kwargs.get("hybrid_search", False),
            retrieval_query=kwargs.get("retrieval_query","")
        )
    
def get_synthesize():
    from llama_index.core.schema import NodeWithScore
    from llama_index.core.data_structs import Node
    from llama_index.core.response_synthesizers import ResponseMode
    from llama_index.core import get_response_synthesizer
    from llama_index.core.settings import Settings
    Settings.llm = get_llm()

    response_synthesizer = get_response_synthesizer(
        response_mode=ResponseMode.COMPACT
    )

    response = response_synthesizer.synthesize(
        "query text", nodes=[NodeWithScore(node=Node(text="text"), score=1.0)]
    )
   
    return response

if __name__ == '__main__':
    get_vector_store(index_name="new_vector")