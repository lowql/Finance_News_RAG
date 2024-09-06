# Property Graph Construction with Predefined Schemas
from llama_index.core.graph_stores.types import EntityNode, ChunkNode, Relation
from typing import Literal

# best practice to use upper-case
entities = Literal["Company", "News"]
relations = Literal["IMPACT", "SUPPLIERS", "COMPETITOR", "CUSTOMERS", "REINVESTMENT","INVESTED","STRATEGIC_ALLIANCE"]

# [x] Define: Company Schema
# define which entities can have which relations
validation_schema = {
    "Company": ["SUPPLIERS", "COMPETITOR", "CUSTOMERS", "REINVESTMENT","INVESTED","STRATEGIC_ALLIANCE"],
    "News": ["IMPACT"],
}
validation_schema = [
    ("Company","SUPPLIERS","Company"),
    ("Company","COMPETITOR","Company"),
    ("Company","CUSTOMERS","Company"),
    ("Company","REINVESTMENT","Company"),
    ("Company","INVESTED","Company"),
    ("Company","STRATEGIC_ALLIANCE","Company"),
    ("News","IMPACT","Company")
]

"""An index for a property graph.

    Args:
        nodes (Optional[Sequence[BaseNode]]):
            A list of nodes to insert into the index.
        llm (Optional[BaseLLM]):
            The language model to use for extracting triplets. Defaults to `Settings.llm`.
        kg_extractors (Optional[List[TransformComponent]]):
            A list of transformations to apply to the nodes to extract triplets.
            Defaults to `[SimpleLLMPathExtractor(llm=llm), ImplicitEdgeExtractor()]`.
        property_graph_store (Optional[PropertyGraphStore]):
            The property graph store to use. If not provided, a new `SimplePropertyGraphStore` will be created.
        vector_store (Optional[BasePydanticVectorStore]):
            The vector store index to use, if the graph store does not support vector queries.
        embed_model (Optional[EmbedType]):
            The embedding model to use for embedding nodes.
            If not provided, `Settings.embed_model` will be used if `embed_kg_nodes=True`.
        embed_kg_nodes (bool):
            Whether to embed the KG nodes. Defaults to `True`.
        transformations (Optional[List[TransformComponent]]):
            A list of transformations to apply to the nodes before inserting them into the index.
            These are applied prior to the `kg_extractors`.
        storage_context (Optional[StorageContext]):
            The storage context to use.
        show_progress (bool):
            Whether to show progress bars for transformations. Defaults to `False`.
    """
from llama_index.core import PropertyGraphIndex


""" Querying """


from llama_index.core.indices.property_graph import (
    LLMSynonymRetriever,
    VectorContextRetriever,
)

from llama_index.llms.ollama import Ollama

from llama_index.embeddings.ollama import OllamaEmbedding
ollama_embedding = OllamaEmbedding(
    model_name="llama2",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0},
)
"""
graph_store (PropertyGraphStore):
            The graph store to retrieve data from.
"""
index = PropertyGraphIndex.from_documents(
    documents,
    kg_extractors=[kg_extractor],
    embed_model=ollama_embedding
    property_graph_store=graph_store, 
    vector_store=vec_store,
    show_progress=True,
)
llm_synonym = LLMSynonymRetriever(
    index.property_graph_store,
    llm=Ollama(model="llama3", request_timeout=3600),
    include_text=False,
)
vector_context = VectorContextRetriever(
    index.property_graph_store,
    embed_model=ollama_embedding,
    include_text=False,
)

retriever = index.as_retriever(
    sub_retrievers=[
        llm_synonym,
        vector_context,
    ]
)

nodes = retriever.retrieve("What happened at Interleaf?")
for node in nodes:
    print(node.text)
    
query_engine = index.as_query_engine(
    sub_retrievers=[
        llm_synonym,
        vector_context,
    ],
    llm=Ollama(model="llama3", request_timeout=3600),
)

response = query_engine.query("What happened at Interleaf?")
print(str(response))

#=================================
# Property Graph Index

""" 
    PropertyGraphIndex.from_documents() - we loaded documents into an index
    
    Parsing nodes - the index parsed the documents into nodes
    Extracting paths from text - the nodes were passed to an LLM, and the LLM was prompted to generate knowledge graph triples (i.e. paths)
    Extracting implicit paths - each node.relationships property was used to infer implicit paths
    Generating embeddings - embeddings were generated for each text node and graph node (hence this happens twice)
"""
index = PropertyGraphIndex.from_documents(
    documents,
    llm=OpenAI(model="gpt-3.5-turbo", temperature=0.3),
    embed_model=OpenAIEmbedding(model_name="text-embedding-3-small"),
    show_progress=True,
)

""" 
Lets explore what we created! For debugging purposes, 
the default SimplePropertyGraphStore includes a helper to save a networkx representation of the graph to an html file.
"""
index.property_graph_store.save_networkx_graph(name="./kg.html")

""" 
Customizing Low-Level Construction
"""
from llama_index.core.indices.property_graph import (
    ImplicitPathExtractor,
    SimpleLLMPathExtractor,
)

index = PropertyGraphIndex.from_documents(
    documents,
    embed_model=OpenAIEmbedding(model_name="text-embedding-3-small"),
    kg_extractors=[
        ImplicitPathExtractor(),
        SimpleLLMPathExtractor(
            llm=OpenAI(model="gpt-3.5-turbo", temperature=0.3),
            num_workers=4,
            max_paths_per_chunk=10,
        ),
    ],
    show_progress=True,
)

""" 
Querying
"""
retriever = index.as_retriever(
    include_text=False,  # include source text, default True
)

nodes = retriever.retrieve("What happened at Interleaf and Viaweb?")

for node in nodes:
    print(node.text)
    
query_engine = index.as_query_engine(
    include_text=True,
)

response = query_engine.query("What happened at Interleaf and Viaweb?")

print(str(response))

"""
storage
"""
index.storage_context.persist(persist_dir="./storage")

from llama_index.core import StorageContext, load_index_from_storage

index = load_index_from_storage(
    StorageContext.from_defaults(persist_dir="./storage")
)