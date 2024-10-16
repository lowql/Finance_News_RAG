# tests\dataset_workflow\test_pipline.py
from pipeline import utils
from pipeline.news import News
news = News(6125)
documents = news.fetch_documnets()[0:2]
announcement_news = []
normal_news = []
print(len(documents))
print(documents)
for document in documents:
    if "【公告】" in document.metadata['headline']:
        announcement_news.append(document)
    else: 
        normal_news.append(document)
print(f"len of normal news {len(normal_news)}")
print(f"len of announcement news {len(announcement_news)}")
def test_announcement_news_ingestion():
    from setup import Transformations,get_embed_model,get_vector_store
    embedder = get_embed_model()
    transformation = Transformations()
    announcement_news_nodes = news.ingestion(documents=announcement_news,
                    transformations=[
                        transformation.get_custom_extractor(),
                        transformation.get_sentence_splitter(),
                        embedder
                    ],
                    vector_store=get_vector_store(node_label="新聞"))
    print('='*50)
    for doc in documents:
        print(doc)
        print(doc.metadata)
    print('%'*50)
    for node in announcement_news_nodes:
        print(node)
        print(node.metadata)
    print(len(announcement_news_nodes))
   
def test_normal_news_ingestion():
    from setup import Transformations,get_embed_model,get_vector_store
    embedder = get_embed_model()
    transformation = Transformations()
    announcement_news_nodes = news.ingestion(documents=announcement_news,
                    transformations=[
                        transformation.get_custom_extractor(),
                        transformation.get_sentence_splitter(),
                        embedder
                    ],
                    vector_store=get_vector_store(node_label="新聞"))
    print('='*50)
    for doc in documents:
        print(doc)
        print(doc.metadata)
    print('%'*50)
    for node in announcement_news_nodes:
        print(node)
        print(node.metadata)
    print(len(announcement_news_nodes))
   