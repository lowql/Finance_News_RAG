import chromadb

# Initialize the ChromaDB client

# HACK:  非持久性儲存設定
client = chromadb.Client()
# Test if the service is up and running
print(client.heartbeat())

# TODO: 研究collection layer的metadata
news = client.create_collection("news",metadata={"hnsw:space": "cosine"})
print(news)

exist_collection = client.get_or_create_collection("news")
print(exist_collection)

absence_collection = client.get_or_create_collection("feature_news")
print(absence_collection)