from llama_index.core import VectorStoreIndex,Settings
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from setup import get_vector_store,get_embed_model

Settings.embed_model = get_embed_model()
class VectorIndex:
    # Query the index
    def __init__(self,**kwargs) -> None:
        """ 
        # Load existing vector index
        VectorIndex(index_name=index_name,text_node_property=text_node_property)
        
        # Customizing responses
        VectorIndex(retrieval_query=retrieval_query)
        """
        self.vector_store:Neo4jVectorStore = self.choose_vector_store(kwargs=kwargs)
    def get_vector_store(self):
        return self.vector_store
    def choose_vector_store(self,kwargs):
        if 'retrieval_query' not in kwargs:
            return get_vector_store(
                node_label=kwargs['node_label'],
                hybrid_search=kwargs.get('hybrid_search',False),
                # for query
                index_name=kwargs.get('index_name','vector'),
                text_node_property=kwargs['text_node_property']
                )
        else:
            return get_vector_store(
                retrieval_query=kwargs['retrieval_query']
                )
    def query(self,query_text):
        """ 
        You can customize the retrieved information from the knowledge graph using the retrieval_query parameter.

        The retrieval query must return the following four columns:

            text:str - The text of the returned document
            score:str - similarity score
            id:str - node id
            metadata: Dict - dictionary with additional metadata (must contain _node_type and _node_content keys)

        """
        index = VectorStoreIndex.from_vector_store(self.vector_store).as_query_engine()
        return index.query(query_text)
    
    def retrieve(self,query_text):
        index = VectorStoreIndex.from_vector_store(self.vector_store).as_retriever()
        return index.retrieve(query_text)

# Example usage
if __name__ == "__main__":
    vector_index = VectorIndex(node_label="新聞",text_node_property="content")
    
    nodes =  vector_index.retrieve("統一集團")
    
    for node in nodes:
        print(node)
        print('='*50,"get content",'='*50)
    
    # retrieval_cypher_query = (
    #         "RETURN 'Interleaf hired Tomaz' AS text, score, node.id AS id, "
    #         "{author: 'Tomaz', _node_type:node._node_type, _node_content:node._node_content} AS metadata"
    #     )
    # vector_index = VectorIndex(retrieval_query=retrieval_cypher_query)
    # retrieve_existing_index
    """ Check if the vector index exists in the Neo4j database and returns its embedding dimension.
    node_label: str = "Chunk",
    index_name: str = "vector",
    embedding_node_property: str = "embedding",
    """
    
    # retrieve_existing_fts_index
    """ Check if the fulltext index exists in the Neo4j database. 
    node_label: str = "Chunk",
    keyword_index_name: str = "keyword",
    text_node_property: str = "text",
    """
