from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError
from config import db_config
import pandas as pd
from typing import List, Dict, Any

BASE_ENTITY_LABEL = "__Entity__"

# python -m storages.graph_storage
class Neo4jStorage:
    def __init__(self, uri, auth):
        
        self.dataset_path = './dataset/base/company_relations.csv'
        try:
            self.driver = GraphDatabase.driver(uri, auth=auth)
        except:
            print("please open noe4j desktop")
    def check_connection(self):
        from neo4j.exceptions import ServiceUnavailable
        try:
            driver = self.driver
            with driver.session() as session:
                result = session.run("RETURN 'Connection successful!' AS message")
                print(result.single()["message"])
            driver.close()
            return True
        except ServiceUnavailable:
            print("連接失敗: 無法連接到Neo4j數據庫。請嘗試開啟 Neo4j Desktop")
            return False
        except Exception as e:
            print(f"發生錯誤: {str(e)}")
            return False
    
    # HACK:  分割串列工具
    def split_string(value):
        if value:
            return value.split('|')
        return []
    def run(self, query: str, parameters: Dict[str, Any]=None):
        with self.driver.session() as session:
            try:
                session.run(query, parameters)
            except CypherSyntaxError as e:
                raise ValueError(
                    f"Generated Cypher Statement is not valid\n{e}"
                )
    # [ ] Add KG Triplet
    def add_triplet(self,subj,obj,rel)->None:
        prepared_statement = f"""
            MERGE (n1:`{BASE_ENTITY_LABEL.replace("_", "")}` {{id:$subj}})
            MERGE (n2:`{BASE_ENTITY_LABEL.replace("_", "")}` {{id:$obj}})
            MERGE (n1)-[:{rel.replace(" ", "_").upper()}]->(n2)
        """
        print(prepared_statement)
        params = {
            "subj":subj,
            "obj":obj
        }
        # Execute the query within a database session
        self.run(prepared_statement,parameters=params)
        
    def add_company(self,code):
        prepared_statement = """
        MERGE (n:Company {code: $code})
        SET
        n.code = $code, n.name = $name
        """
        # HACK: 資料應該存放在 dataset/base/...
        df = pd.read_csv(self.dataset_path)
        # 將 code 列轉換為整數型（如果尚未轉換）
        df['code'] = df['code'].astype(int)
        
        # 選擇 code 為 2421 的行
        try:
            df = df[df['code'] == code].iloc[0] 
        except:
            print("Something else went wrong") 
            
        params = {
            "code": int(df["code"]),  # 轉換為整數
            "name": df["name"]
        }
        self.run(prepared_statement,params)
    
    def add_companies(self,codes):
        # HACK: 理論上來說重新建構CYPHER速度會更快
        [self.add_company(code) for code in codes]
            
 
    def add_company_interactive(self,code):
        """ 
            添加公司互動 from dataset_path
            code,name,suppliers,customers,competitor,strategic_alliance,invested 
            6125,廣運   ,....
        """
        prepared_statement = """
        MERGE (c1:Company {name: $c1_name, code:$c1_code})
        MERGE (c2:Company {name: $c2_name})
        """
        
        df = pd.read_csv(self.dataset_path,index_col='code')
        
        relation_info = df.loc[6125]
        params = {}
        params['c1_name'] = relation_info['name'][:2]
        params['c1_code'] = int(relation_info['name'][3:-1])
        
        import ast
        for rel in df.columns[1:]:
            items = ast.literal_eval(relation_info[rel])
            print('loading rel: ',rel)
            cypher = prepared_statement
            cypher += f"MERGE (c1)-[r:{rel}]->(c2)"
            for item in items:
                params['c2_name'] = item
                print(params)
                self.run(cypher,parameters=params)
    def remove_node_property():
        """ MATCH (n)
        WITH n, keys(n) AS props
        UNWIND props AS prop
        WITH n, prop
        WHERE prop IN ['key1', 'key2', 'key3']  // 替换为你想要移除的属性列表
        CALL apoc.remove.property(n, prop) YIELD node
        RETURN count(*) AS removedNodeProperties; """
    def remove_rel_property():
        """
        MATCH ()-[r]->()
        WITH r, keys(r) AS props
        UNWIND props AS prop
        WITH r, prop
        WHERE prop IN ['key1', 'key2', 'key3']  // 替换为你想要移除的属性列表
        CALL apoc.remove.property(r, prop) YIELD rel
        RETURN count(*) AS removedRelationshipProperties;
        """
        
    def remove_all(self):
        prepared_statement = "MATCH (n) DETACH DELETE n"
        self.run(prepared_statement)
            
        
if __name__ == '__main__':
    driver = Neo4jStorage(db_config.Neo4j_URI, db_config.Neo4j_AUTH)
    
    if driver.check_connection():
        driver.add_company_interactive(6125)
        # driver.remove_all()
    # # driver.add_triplet("Class_A","Class_B","__rel__")