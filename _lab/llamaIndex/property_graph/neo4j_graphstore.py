
from llama_index.core import SimpleDirectoryReader
from llama_index.core import PropertyGraphIndex
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

from llama_index.llms.ollama import Ollama
llm = Ollama(model='yi')
from llama_index.core import Settings
Settings.llm = llm
Settings.chunk_size = 2048
Settings.chunk_overlap = 20
from llama_index.embeddings.ollama import OllamaEmbedding
ollama_embedding = OllamaEmbedding(
    model_name="llama2",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0},
)



""" if no opne neo4j desktop
neo4j.exceptions.ServiceUnavailable: Couldn't connect to localhost:7687 (resolved to ()):
Failed to establish connection to ResolvedIPv6Address(('::1', 7687, 0, 0)) (reason [WinError 10061] 無法連線，因為目標電腦拒絕連線。)
Failed to establish connection to ResolvedIPv4Address(('127.0.0.1', 7687)) (reason [WinError 10061] 無法連線，因為目標電腦拒絕連線。)
"""
""" AuthError
neo4j.exceptions.AuthError: {code: Neo.ClientError.Security.Unauthorized} {message: The client is unauthorized due to authentication failure.}
"""
graph_store = Neo4jPropertyGraphStore(
    username="neo4j",
    password="company#1",
    url="bolt://localhost:7687",
)

from llama_index.core import Document
documents = []
with open('./utils/news_crawler/YahooStock/yahoo_news.csv','r',encoding='utf8') as csvfile:
    import csv
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        documents.append(Document(text=row['content'],metadata={'author':row['author'],'headline':row['headline']}))
    
    
print(len(documents))
""" 
# Extract graph from documents
index = PropertyGraphIndex.from_documents(
    documents,
    embed_model=ollama_embedding,
    kg_extractors=[
        SchemaLLMPathExtractor(llm=llm)
    ],
    property_graph_store=graph_store,
    show_progress=True,
)

# Define retriever
retriever = index.as_retriever(
    include_text=False,  # include source text in returned nodes, default True
)
results = retriever.retrieve("What happened at Interleaf and Viaweb?")
for record in results:
    print(record.text)

# Question answering
query_engine = index.as_query_engine(include_text=True)
response = query_engine.query("What happened at Interleaf and Viaweb?")
print(str(response)) """