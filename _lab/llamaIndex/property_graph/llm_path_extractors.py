# Comparing LLM Path Extractors for Knowledge Graph Construction

import pyvis
#python -m _lab.llamaIndex.property_graph.llm_path_extractors
from llama_index.core import Document, PropertyGraphIndex
from llama_index.core.indices.property_graph import (
    SimpleLLMPathExtractor,
    SchemaLLMPathExtractor,
    DynamicLLMPathExtractor,
)
from llama_index.llms.openai import OpenAI
from typing import Literal

from llama_index.llms.ollama import Ollama
llm = Ollama(model='yi')
from llama_index.core import Settings
Settings.llm = llm
Settings.chunk_size = 2048
Settings.chunk_overlap = 20


query = "Nvidia與廣運是什麼關係?"
# utils\news_crawler\YahooStock\yahoo_news.csv
news = ""
with open('./utils/news_crawler/YahooStock/yahoo_news.csv','r',encoding='utf8') as csvfile:
    import csv
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        news = row['content']
    
    
print(news)

max_knowledge_triplets = 10
neo4j_prompt = ("以下提供了一些文本。根據這段文本，提取最多 "
            "{max_knowledge_triplets} "
            "knowledge triplets in the form of (subject, predicate, object). Avoid stopwords.\n"
            "---------------------\n"
            "Example:"
            "Text: 公司A是公司B的客戶"
            "Triplets:\n(公司A, 客戶, 公司B)\n"
            "Text: 公司A的解決方案使用公司B的x技術.\n"
            "Triplets:\n"
            "(公司A, 提供, 解決方案)\n"
            "(公司A, 使用, 公司B的技術)\n"
            "(公司B, 提供, x技術)\n"
            "---------------------\n"
            "Text: {text}\n"
            "Triplets:\n"
        )
noe4j_prompt = neo4j_prompt.format(max_knowledge_triplets=max_knowledge_triplets)
""" Readme
1. setting path extractor
2. document_extract
3. get_triples() | save()
"""
class PathExtractor():
    def __init__(self) -> None:
        simple_index = PropertyGraphIndex.from_documents
        kg_extractor = None
        
        
    def _SimpleLLMPathExtractor(self):
        self.kg_extractor = SimpleLLMPathExtractor(
            llm=llm, max_paths_per_chunk=20, num_workers=4,extract_prompt = neo4j_prompt
        )
    
    def _ImplicitPathExtractor(self):
        from llama_index.core.indices.property_graph import ImplicitPathExtractor
        self.kg_extractor = ImplicitPathExtractor()
        
    """ NotImplementedError: achat_with_tools is not supported by default. """
    def _SchemaLLMPathExtractor(self):
        # recommended uppercase, underscore separated
        # TODO: feat:: storages\noe4j_storage 建構 schema 
        entities = Literal["Company","News"]
        relations = Literal["提供", "展示", "使用"]
        schema = {
            "Company": ["展示", "提供", "使用"],
            "News": ["作者", "日期"],
        }

        self.kg_extractor = SchemaLLMPathExtractor(
            llm=llm,
            possible_entities=entities,
            possible_relations=relations,
            kg_validation_schema=schema,
            strict=True,  # if false, will allow triples outside of the schema
        )
    def _DynamicLLMPathExtractor(self):
        self.kg_extractor = DynamicLLMPathExtractor(
            llm=llm,
            max_triplets_per_chunk=20,
            num_workers=4,
            allowed_entity_types=["POLITICIAN", "POLITICAL_PARTY"],
            allowed_relation_types=["PRESIDENT_OF", "MEMBER_OF"],
        )
        
    def document_extract(self,text):
        # TODO: 文本分割 pre_processing
        document = Document(text=text)
        self.simple_index = PropertyGraphIndex.from_documents(
            [document],
            llm=llm,
            embed_kg_nodes=False,
            kg_extractors=[self.kg_extractor],
            show_progress=True,
        )
    def save(self,filename):
        # OSError: [Errno 22] Invalid argument: '.\\財報是什麼?.html'
        valid_filename = filename.replace('?', '')
        self.simple_index.property_graph_store.save_networkx_graph(
            name=f".\{valid_filename}.html"
        )
        print("save successful")

    def get_triplets(self):
        triplets = self.simple_index.property_graph_store.get_triplets(
            entity_names=["廣運", "輝達"]
        )[:1]

        print(triplets)

if __name__  == '__main__':
    extractor = PathExtractor()
    
    extractor._SimpleLLMPathExtractor()
    extractor.document_extract(news)
    extractor.get_triplets()
    # extractor.save("simple_extractor")
    
    extractor._DynamicLLMPathExtractor()
    extractor.document_extract(news)
    extractor.get_triplets()
    # extractor.save("dynamic_extractor")
    
    extractor._ImplicitPathExtractor()
    extractor.document_extract(news)
    # extractor.save("_ImplicitPathExtractor")
    
    # import csv
    # with open('./dataset/base/CompanyQA.csv',encoding='utf8') as file:
    #     csv_file = csv.reader(file) 
        
        # for lines in csv_file:
        #     print(lines[0])
        #     gen_property_graph(lines[0],lines[0])
        
# TODO: 調整 prompt 限制生成 現有的 Graph schema 

# TODO: 從 GraphDB 查詢現有的 Graph schema


""" 
[ EntityNode(label='entity', embedding=None, properties={'triplet_source_id': '5b623228-c5d1-40c8-a6ca-bbed9bc7442a'}, name='廣運'), 
  Relation(label='在', source_id='廣運', target_id='台北國際電腦展展示', properties={'triplet_source_id': '5b623228-c5d1-40c8-a6ca-bbed9bc7442a'}), 
  EntityNode(label='entity', embedding=None, properties={'triplet_source_id': '5b623228-c5d1-40c8-a6ca-bbed9bc7442a'}, name='台北國際電腦展展示'), 
] 
"""

