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

def get_graph_store():
    from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
    from config.db_config import Neo4j_USER,Neo4j_PWD,Neo4j_URI
    return Neo4jPropertyGraphStore(
        username=Neo4j_USER,
        password=Neo4j_PWD,
        url=Neo4j_URI,
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
    print(get_synthesize())