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
        self.validation_schema = {
            "Company": ["研發", "使用"],
            "News": ["影響"],
            "Items": ["有關"],
        }
        self.max_knowledge_triplets = 3
        # self.neo4j_prompt 
        self.kg_extract_templete = ""
        self.text_qa_template = ""
        self.refine_template = ""
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
    def _schema_llm_extractor(self):
        from llama_index.core.indices.property_graph import SchemaLLMPathExtractor
        neo4j_prompt = neo4j_prompt.format(max_knowledge_triplets=self.max_knowledge_triplets)
        kg_schema_extractor = SchemaLLMPathExtractor(
            strict=False,  # Set to False to showcase why it's not going to be the same as DynamicLLMPathExtractor
            possible_entities=self.entities,  # USE DEFAULT ENTITIES (PERSON, ORGANIZATION... etc)
            possible_relations=self.relations,  # USE DEFAULT RELATIONSHIPS
            kg_validation_schema=self.validation_schema,
            extract_prompt=neo4j_prompt,
            possible_relation_props=[
                "額外備註關係"
            ],  # Set to `None` to skip property generation
            possible_entity_props=[
                "額外備註"
            ],  # Set to `None` to skip property generation
            num_workers=10,
        )
        return kg_schema_extractor
    def _dynamic_llm_extractor(self,extract_prompt):
        from llama_index.core.indices.property_graph import DynamicLLMPathExtractor
        kg_dynamic_extractor = DynamicLLMPathExtractor(
                    max_triplets_per_chunk=5,
                    num_workers=4,
                    extract_prompt=extract_prompt,
                    allowed_entity_types=["Company", "News","Items"],
                )
        return kg_dynamic_extractor
    def build_index_from_documents(self,documents):
        DYNAMIC_EXTRACT_TMPL = ""
        with open(get_llama_index_template('dynamic_extract'), 'r',encoding='utf8') as template_file:
            template = Template(template_file.read())
            DYNAMIC_EXTRACT_TMPL = template.render()
    
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
    
import pandas as pd
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
        from pipeline.news import Pipeline
        pipe = Pipeline(code)
        nodes = pipe.news_nodes()
        from utils.path_manager import get_company_relations
        relation_path = get_company_relations()
        relation_codes = pd.read_csv(relation_path,usecols=['code','name'])
        code_to_name = dict(zip(relation_codes['code'], relation_codes['name']))
        name = code_to_name.get(code, "本公司還未上市，抑或是資料庫查無此資料")
        print(f"len of nodes {len(nodes)}")
        for node in nodes:
            cypher = """
             MERGE (c:公司 {name: $name, code:$code})
             MERGE (n:新聞 {headline: $headline, author:$author, time:$time, content:$content})
             MERGE (n)-[r:提及]->(c)
            """
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
        pre_cypher = """
            MERGE (c1:公司 {name: $c1_name, code:$c1_code})
            MERGE (c2:公司 {name: $c2_name})
        """
        dataset_path = './dataset/base/company_relations.csv'
        df = pd.read_csv(dataset_path,index_col='code')
        
        relation_info = df.loc[code]
        params = {}
        params['c1_name'] = relation_info['name'][:2]
        params['c1_code'] = int(relation_info['name'][3:-1])
        
        import ast
        zh_map = {
            'suppliers':"供應商",
            'competitor':"競爭者",
            'customers':"客戶",
            'reinvestment':"轉投資",
            'invested':"被投資",
            'strategic_alliance':"策略聯盟",
        }
        
        for rel in df.columns[1:]:
            items = ast.literal_eval(relation_info[rel])
            print('loading rel: ',zh_map[rel])
            cypher = pre_cypher + f"MERGE (c1)-[r:{zh_map[rel]}]->(c2)"
            for item in items:
                params['c2_name'] = item
                print(params)
                self.graph_store.structured_query(cypher,param_map=params)
        self.graph_store.close()
        
    def remove_all(self):
        cmd = input("y|n")
        if cmd == 'n':
            return
        cypher = "MATCH (n) DETACH DELETE n"
        self.graph_store.structured_query(cypher)
        return self.graph_store.close()
        
    def extract_Notice():
        print(df[df['title'].str.contains(pat = '【.*】', regex = True)].loc[:,['date','title']],'\n')
    # print(df[df['title'].str.contains(pat = '盤中速報', regex = True)].loc[:,['date','title']],'\n')
    # print(df[df['title'].str.contains(pat = '焦點股', regex = True)].loc[:,['date','title']],'\n')
    # print(df[df['title'].str.contains(pat = '熱門股', regex = True)].loc[:,['date','title']],'\n')
    # print(df[df['title'].str.contains(pat = '營收', regex = True)].loc[:,['date','title']],'\n')
    # print(df[df['title'].str.contains(pat = '《.*》', regex = True)].loc[:,['date','title']],'\n')
        
# 1. "\n請保持上下文關係不變的狀態下，以JSON表示\n"
# 2. 請條列出公司的利多消息
# 3. 簡要說明各公司持有的技術，並標註持有技術的公司([公司名稱]::(持有技術))