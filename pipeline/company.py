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
    def fetch_documents():
        pass
        