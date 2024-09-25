from pydantic import BaseModel
from typing import Optional, List

from llama_index.llms.ollama import Ollama
llm = Ollama(model='yi',request_timeout=360)

from llama_index.embeddings.ollama import OllamaEmbedding
embed_model = OllamaEmbedding(
    model_name="yi",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0}
)

class Entities(BaseModel):
    """List of named entities in the text such as names of people, organizations, concepts, and locations"""
    names: Optional[List[str]]


prompt_template_entities = """
Extract all named entities such as names of people, organizations, concepts, and locations
from the following text:
{text}
"""

from typing import Any, Optional

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.retrievers import CustomPGRetriever, VectorContextRetriever
from llama_index.core.vector_stores.types import VectorStore
from llama_index.program.openai import OpenAIPydanticProgram



class MyCustomRetriever(CustomPGRetriever):
    """Custom retriever with entity detection."""
    def init(
        self,
        ## vector context retriever params
        embed_model: Optional[BaseEmbedding] = None,
        vector_store: Optional[VectorStore] = None,
        similarity_top_k: int = 4,
        path_depth: int = 1,
        include_text: bool = True,
        **kwargs: Any,
    ) -> None:
        """Uses any kwargs passed in from class constructor."""
        self.entity_extraction = OpenAIPydanticProgram.from_defaults(
            output_cls=Entities, prompt_template_str=prompt_template_entities
        )
        self.vector_retriever = VectorContextRetriever(
            self.graph_store,
            include_text=self.include_text,
            embed_model=embed_model,
            similarity_top_k=similarity_top_k,
            path_depth=path_depth,
        )

    def custom_retrieve(self, query_str: str) -> str:
        """Define custom retriever with entity detection.

        Could return `str`, `TextNode`, `NodeWithScore`, or a list of those.
        """
        entities = self.entity_extraction(text=query_str).names
        result_nodes = []
        if entities:
            print(f"Detected entities: {entities}")
            for entity in entities:
                result_nodes.extend(self.vector_retriever.retrieve(entity))
        else:
            result_nodes.extend(self.vector_retriever.retrieve(query_str))
        final_text = "\n\n".join(
            [n.get_content(metadata_mode="llm") for n in result_nodes]
        )
        return final_text
    
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from config.db_config import Neo4j_USER,Neo4j_PWD,Neo4j_URI
graph_store = Neo4jPropertyGraphStore(
        username=Neo4j_USER,
        password=Neo4j_PWD,
        url=Neo4j_URI,
    )
from llama_index.core import PropertyGraphIndex
index = PropertyGraphIndex.from_existing(
    property_graph_store=graph_store,
    use_async = False,
)
custom_sub_retriever = MyCustomRetriever(
    index.property_graph_store,
    include_text=True,
    vector_store=index.vector_store,
    embed_model=embed_model
)

from llama_index.core.query_engine import RetrieverQueryEngine
query_engine = RetrieverQueryEngine.from_args(
    index.as_retriever(sub_retrievers=[custom_sub_retriever]), llm=llm
)

response = query_engine.query(
    "What do you know about Maliek Collins or Darragh O’Brien?"
)
print(str(response))