import pandas as pd
from dataset.utils import fetch_news

class News:
    def __init__(self,code):
        self.code = code
        self.name = self.get_company_name()
        self.df = fetch_news(code)
        self.documents = self.df['content'].tolist()
        self.meta_headline =  self.df['headline'].tolist()
        self.meta_author =  self.df['author'].tolist()
        self.meta_time =  self.df['time'].tolist()
    def get_company_name(self):
        from utils.path_manager import get_company_relations
        relation_path = get_company_relations()
        relation_codes = pd.read_csv(relation_path,usecols=['code','name'])
        code_to_name = dict(zip(relation_codes['code'], relation_codes['name']))
        name = code_to_name.get(int(self.code), "本公司還未上市，抑或是資料庫查無此資料")
        return name
    def fetch_textnodes(self):
        from llama_index.core.schema import TextNode
        nodes = []
        for idx, document in enumerate(self.documents):
            node = TextNode(
                text=document,
                metadata={
                'headline':self.meta_headline[idx],
                'author':self.meta_author[idx],
                'time':self.meta_time[idx]
                })
            nodes.append(node)
        return nodes
    def fetch_documnets(self):
        from llama_index.core.schema import Document
        documents = []
        for idx, content in enumerate(self.documents):
            documents.append(Document(
                    text=content,
                    metadata={
                        'headline':self.meta_headline[idx],
                        'author':self.meta_author[idx],
                        'time':self.meta_time[idx]
                    },
                    metadata_seperator="\n",
                    metadata_template="{key} : {value} ",
                    text_template="新聞的基本資訊:\n {metadata_str}\n\n 新聞內文:\n {content}",
                ))
        return documents