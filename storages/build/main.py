from llama_index.core import Document
from utils.path_manager import get_news_content_file
documents = []
with open(get_news_content_file(6125),'r',encoding='utf8') as csvfile:
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
from setup import get_embed_model,get_llm
Settings.llm = get_llm()
Settings.embed_model = get_embed_model()

if __name__ == "__main__":
    from storages.build.property_graph import BuildPropertyGraph
    property_graph_index = BuildPropertyGraph()
    property_graph_index.build_index_from_documents(documents=documents[:3])