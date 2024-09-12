from llama_index.core import Document
documents = []
with open('./utils/news_crawler/YahooStock/yahoo_news.csv','r',encoding='utf8') as csvfile:
    import csv
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        documents.append(Document(
            text=row['content'],
            metadata={'author':row['author'],'headline':row['headline']},
            metadata_seperator="\n",
            metadata_template="{key} [ {value} ] ",
            text_template="Metadata:\n {metadata_str}\n-----\nContent: {content}",
            ))
        
from llama_index.core import Settings

from llama_index.embeddings.ollama import OllamaEmbedding
ollama_embedding = OllamaEmbedding(
    model_name="yi",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0}
)
Settings.embed_model = ollama_embedding

from llama_index.llms.ollama import Ollama
llm = Ollama(model='yi',request_timeout=360)
Settings.llm = llm

if __name__ == "__main__":
    from storages.build.property_graph import BuildPropertyGraph
    property_graph_index = BuildPropertyGraph()
    property_graph_index._dynamic_llm_extractor()
    property_graph_index.build_index_from_documents(documents=documents)
    property_graph_index.test_query_engine()