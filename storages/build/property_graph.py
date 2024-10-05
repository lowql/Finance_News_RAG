from llama_index.core import PropertyGraphIndex
from typing import Literal
from llama_index.core import Settings
from setup import get_embed_model,get_llm,get_graph_store
Settings.llm = get_llm()
Settings.embed_model = get_embed_model()
graph_store = get_graph_store()
from utils.path_manager import get_llama_index_template
from jinja2 import Template
class AutoBuildPropertyGraph:
    
    def __init__(self):
        self.graph_store = get_graph_store()
        self.entities = Literal["Company", "News","Items"]
        self.relations = Literal["有", "研發", "使用", "提及", "影響","有關"]
        self.max_knowledge_triplets = 3
        # self.neo4j_prompt 
        self.kg_extract_templete = ""
        self.text_qa_template = ""
        self.refine_template = ""
        self.dynamic_extract_template = ""
        self.index = PropertyGraphIndex.from_documents
    def set_prompt_template(self):
        with open(get_llama_index_template('refine'), 'r',encoding='utf8') as template_file:
            template = Template(template_file.read())
            self.refine_template = template.render()
        with open(get_llama_index_template('text_qa'), 'r',encoding='utf8') as template_file:
            template = Template(template_file.read())
            self.text_qa_template = template.render
        with open(get_llama_index_template('kg_extract'), 'r',encoding='utf8') as template_file:
            template = Template(template_file.read())
            max_knowledge_triplets = 3
            self.kg_extract_templete = template.render(max_knowledge_triplets=max_knowledge_triplets)           
        with open(get_llama_index_template('dynamic_extract'), 'r',encoding='utf8') as template_file:
            template = Template(template_file.read())
            self.dynamic_extract_template = template.render()   
    def _dynamic_llm_extractor(self,extract_prompt):
        from llama_index.core.indices.property_graph import DynamicLLMPathExtractor
        kg_dynamic_extractor = DynamicLLMPathExtractor(
                    max_triplets_per_chunk=5,
                    num_workers=4,
                    extract_prompt=extract_prompt,
                    allowed_entity_types=["公司", "新聞","總結"],
                )
        return kg_dynamic_extractor
    def build_index_from_documents(self,documents):
        DYNAMIC_EXTRACT_TMPL = self.dynamic_extract_template
        kg_extractor = self._dynamic_llm_extractor(extract_prompt=DYNAMIC_EXTRACT_TMPL)
        index = PropertyGraphIndex.from_documents(
            documents,
            use_async = False,
            kg_extractors=[
                kg_extractor,
            ],
            property_graph_store=self.graph_store,
            show_progress=True,  
        )
        return index

    
class ManualBuildPropertyGraph:
    """ 
    公告 : Notice
    盤中速報 : breakingNewsAlert
    焦點股 : HotStock
    營收 : revenue
    《傳產》: tradestate
    《產業》: industry
    《台北股市》: taipeiStockMarket
    《櫃買市場券商買超前30名 3-1》: Top_BrokerBuy
    《光電股》: opticsStock
    《熱門族群》: popularSegments
    """
    def __init__(self):
        self.graph_store = graph_store
        self.entities = Literal["公司", "新聞"]
        self.relations = Literal["提及"]
        self.validation_schema = {
            "公司": [""],
            "新聞": ["提及"],
        }
    def news_mention_company(self,code):
        from pipeline.news import News
        news_pipe = News(code)
        nodes = news_pipe.fetch_textnodes()
        name = news_pipe.get_company_name()
        print(f"build {name}({code}) news property graph")
        print(f"len of nodes :: {len(nodes)}")
        cypher = """
         MERGE (c:公司 {name: $name, code:$code})
         MERGE (n:新聞 {headline: $headline, author:$author, time:$time, content:$content})
         MERGE (n)-[r:提及]->(c)
        """
        for node in nodes:
            param = {
                'code': code, # 公司
                'name': name, # 公司
                'headline':node.metadata['headline'],
                'author':node.metadata['author'],
                'time':node.metadata['time'],
                'content':node.text
            }
            self.graph_store.structured_query(cypher,param_map=param)
        return self.graph_store.close()
    
    def company_rel_company(self,code):
        """ 添加公司互動
            code,name,suppliers,customers,competitor,strategic_alliance,invested 
        """
        from pipeline.company import CompanyInteractive 
        interactive = CompanyInteractive(code)
        print(f"build {code} relation property graph")
        pre_cypher = """
            MERGE (c1:公司 {name: $c1_name, code:$c1_code})
            MERGE (c2:公司 {name: $c2_name})
        """
        relations = interactive.relations
        zh_map = interactive.zh_map
        for rel in relations:
            rel_companys = interactive.get_rel_companys(rel)
            print('loading rel: ',zh_map[rel])
            cypher = pre_cypher + f"MERGE (c1)-[r:{zh_map[rel]}]->(c2)"
            for rel_company in rel_companys:
                params = {
                    'c1_name': interactive.get_source_company_name(),
                    'c1_code': interactive.get_source_company_code(),
                    'c2_name': rel_company
                }
                print(params)
                self.graph_store.structured_query(cypher,param_map=params)
        self.graph_store.close()
        
    def remove_all(self):
        cmd = input("do you want to clean all graph? (y|n) : ")
        if cmd == 'n':
            return
        cypher = "MATCH (n) DETACH DELETE n"
        self.graph_store.structured_query(cypher)
        return self.graph_store.close()
        