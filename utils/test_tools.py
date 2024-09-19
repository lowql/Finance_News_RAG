from utils.path_manager import get_news_content_file
from llama_index.core import Document

def fetch_documents():
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
    return documents