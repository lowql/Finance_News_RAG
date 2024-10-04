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

def get_vector_store(mode,retrieval_query=""):
    """ 
    :params mode: base, normal, hybrid, custom
    :params retrieval_query: only 【custom】 mode need
    """
    from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
    from config.db_config import VECTOR_DIM,VECTOR_INDEX_NAME,TEXT_NODE_PROPERTY
    vector_store_config = {
        "username": Neo4j_USER,
        "password": Neo4j_PWD,
        "url": Neo4j_URI,
        "embed_dim": VECTOR_DIM,
        "index_name": VECTOR_INDEX_NAME,
        "text_node_property": TEXT_NODE_PROPERTY
    }
    if mode == 'base':
        print("Create base neo4j vector store")
        return Neo4jVectorStore(
            username=vector_store_config['username'],
            password=vector_store_config['password'],
            url=vector_store_config['url'],
            embedding_dimension=vector_store_config['embed_dim'],
            index_name="vector", # vector text index name in Neo4j.
            keyword_index_name="keyword", # fulltext index name in Neo4j.
            node_label="CypherMapper",
            embedding_node_property="embedding",
            text_node_property="content",
            distance_strategy="cosine"
        )
    if mode == 'normal':
        return Neo4jVectorStore(
            username=vector_store_config['username'],
            password=vector_store_config['password'],
            url=vector_store_config['url'],
            embedding_dimension=vector_store_config['embed_dim'],
            
            index_name=vector_store_config['index_name'],
            text_node_property=vector_store_config['text_node_property']
        )
    if mode == 'hybrid':
        return  Neo4jVectorStore(
            username=vector_store_config['username'],
            password=vector_store_config['password'],
            url=vector_store_config['url'],
            embedding_dimension=vector_store_config['embed_dim'],
            
            hybrid_search=True
        )
        
    if mode == 'custom':
        return Neo4jVectorStore(
            username=vector_store_config['username'],
            password=vector_store_config['password'],
            url=vector_store_config['url'],
            embedding_dimension=vector_store_config['embed_dim'],
            
            retrieval_query=retrieval_query
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
    print(get_graph_store())