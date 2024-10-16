""" 
company interactive
"""
import pandas as pd
import ast
dataset_path = './dataset/base/company_relations.csv'
zh_map = {
    'suppliers':"供應商",
    'competitor':"競爭者",
    'customers':"客戶",
    'reinvestment':"轉投資",
    'invested':"被投資",
    'strategic_alliance':"策略聯盟",
}
class CompanyInteractive:
    
    def __init__(self,code):
        self.code = code
        self.df = pd.read_csv(dataset_path,index_col='code')
        self.relations = self.df.columns[1:]
        self.zh_map = zh_map
        self.relation_info = self.df.loc[int(code)]
    def get_source_company_name(self):
        return self.relation_info['name'][:-6]
    def get_source_company_code(self):
        return int(self.relation_info['name'][-5:-1])
    def get_rel_companys(self,rel):
        return ast.literal_eval(self.relation_info[rel])
    def fetch_rel_company_tuple(self):
        from llama_index.core.graph_stores.types import EntityNode, Relation
        source_entities = []
        source_entities.append(EntityNode(label="公司",
                                name=self.get_source_company_name(),
                                properties={
                                    "code":self.get_source_company_code()
                                }))
        target_entities = []
        relations = []
        for rel in self.relations:
            print('loading rel: ',zh_map[rel])
            rel_companys = self.get_rel_companys(rel)
            for idx, rel_company in enumerate(rel_companys):
                target_entities.append(EntityNode(label="公司",name=rel_company))
                relations.append(Relation(
                  label=zh_map[rel],
                  source_id=source_entities[0].id,
                  target_id=target_entities[idx].id,
                ))
        entities = source_entities + target_entities
        return entities,relations
        