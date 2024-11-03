import pandas as pd
from dataset.utils import fetch_news
from llama_index.core.schema import Document
from setup import Transformations
from setup import get_embed_model
from llama_index.core.ingestion import IngestionPipeline
def build_document(news_info):
    document =Document(
           text=news_info["text"],
           metadata={
            'headline':news_info["metadata"]['headline'],
            'author':news_info["metadata"]['author'],
            'time':news_info["metadata"]['time']
            },
           metadata_seperator="\n",
           metadata_template="{key} : {value} ",
           text_template="新聞的基本資訊:\n {metadata_str}\n\n 新聞內文:\n {content}",
           )
    return document
class News:
    def __init__(self,code):
        self.code = code
        self.name = self.get_company_name()
        self.df = fetch_news(code)
        self.documents = self.df['content'].tolist()
        self.meta_headline =  self.df['headline'].tolist()
        self.meta_author =  self.df['author'].tolist()
        self.meta_time =  self.df['time'].tolist()
    def fetch_content(self):
        contents = [
         {"stock_id":self.code,"title":headline,'content':content,"date":time,"source":author} 
         for (headline,time,content,author) in zip(self.meta_headline,self.meta_time,self.documents,self.meta_author)
        ]
        return contents
    def ingestion(self,documents,transformations,vector_store=None):
        """ 
            IngestionPipeline 可以直接搭配 vector store 建立 embedding Nodes
        """ 
        pipeline = IngestionPipeline(
            transformations= transformations,
            vector_store=vector_store
        )
        nodes = pipeline.run(documents=documents,num_workers=4)
        return nodes
        
        
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
    def fetch_announcement_news_chunk(self,documents):
        """ 
        原本預計使用IngestionPipeline 可以保留更多彈性但無論如何都會發生以下錯誤
        BUG FAILED tests/dataset_workflow/test_extractor.py::test_dynamicPathExtractor - httpx.ReadTimeout
        """
        transformation = Transformations()
        announcement_news = []
        for document in documents:
            if "【公告】" in document.metadata['headline']:
                announcement_news.append(document)
                

        #根據實作經驗 公告的資訊經過 embedding 會混淆資料的提取，所以忽略embedder，使用fulltext index 會相比 vector index 更加實際
        #TODO
        announcement_news_nodes = self.ingestion(documents=announcement_news,
                                                transformations=[
                                                    transformation.get_custom_extractor(),
                                                    transformation.get_sentence_splitter()
                                                    ]
                                                )
        print(f"len of announcement_news_nodes is {len(announcement_news_nodes)}")
        return announcement_news_nodes
    def put_news_to_vector_store(self,documents,vector_store):
        """ 
            BUG 狀態無法卡在最後，因為資料是嵌套形式無法直接將資料存入Neo4j 
        """
        from setup import Transformations
        transformation = Transformations()
        embedder = get_embed_model()
        announcement_news = []
        normal_news = []
        for document in documents:
            if "【公告】" in document.metadata['headline']:
                announcement_news.append(document)
            else: 
                normal_news.append(document)


        normal_news_nodes = self.ingestion(documents=normal_news,
                                            transformations=[
                                                transformation.get_sentence_splitter(),
                                                embedder],
                                            vector_store=vector_store)
        print(f"{self.code} len of normal_news_nodes is {len(normal_news_nodes)}")
        vector_store.client.close()
    def fetch_news_company_tuple(self):
        from llama_index.core.graph_stores.types import EntityNode, Relation
        company_name = self.get_company_name()
        company_entity = EntityNode(label="公司",name=company_name,properties={"code":self.code})
       
        news_entities = []
        for idx, document in enumerate(self.documents):
            news_entities.append(EntityNode(label="新聞",
                                name=self.meta_headline[idx],
                                properties={
                                    "author":self.meta_author[idx],
                                    "time":self.meta_time[idx],
                                    "content":document
                                }))
            
        """ TODO 命名實體識別技術
        雖然目前的邏輯是寫死成只有提及一間公司
        但實際情況應該要使用命名實體識別技術，提取更多潛在關聯公司
        """
        relations = []
        for entity in news_entities:
            relations.append(Relation(
                label="提及",
                source_id=entity.id,
                target_id=company_entity.id, # 對應提及公司
            ))
                
            
        entities = [company_entity] + news_entities
        return entities,relations
    def fetch_documents(self):
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