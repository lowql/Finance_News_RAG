from utils.path_manager import get_news_content_file
from llama_index.core import Document

def display_prompt_dict(prompts_dict):
    for k, p in prompts_dict.items():
        text_md = f"**Prompt Key**: {k}\n" f"**Text:** \n```"
        print(text_md)
        print(p.get_template(),'```\n\n')

def display_nodes(nodes):
    for node in nodes:
        print(node)
    
        

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

def fetch_document_as_df():
    import pandas as pd
    df = pd.read_csv(get_news_content_file(6125),encoding='utf8')
    return df
    