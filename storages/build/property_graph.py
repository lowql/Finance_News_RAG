from llama_index.core import PropertyGraphIndex
from pipeline.news import News
from llama_index.core import Settings
from setup import get_embed_model,get_llm,get_graph_store,Transformations
Settings.llm = get_llm()
Settings.embed_model = get_embed_model()


class AutoBuildPropertyGraph:
    def __init__(self):
        self.graph_store = get_graph_store()
    def build_News_KG_use_dynamicPathExtractor(self,code):
        dynamic_extractor = Transformations().get_kg_dynamic_extractor()
        news = News(code)
        documants = news.fetch_documnets()
        doc_len = len(documants)
        for idx,document in enumerate(documants):
            try:
                PropertyGraphIndex.from_documents(
                    [document],
                    llm=get_llm(),
                    property_graph_store=self.graph_store,
                    kg_extractors=[dynamic_extractor],
                    embed_kg_nodes=False,
                    show_progress=True,
                )
                print(f"{idx}/{doc_len} :: success extract news")
            except Exception as e:
                print(f"{idx}/{doc_len}:: {e}")

from pipeline import utils
from typing import Literal
class ManualBuildPropertyGraph:
    def __init__(self):
        self.graph_store = get_graph_store()
        self.entities = Literal["公司", "新聞"]
        self.relations = Literal["提及"]
        self.validation_schema = {
            "公司": ["供應商","競爭者","客戶","轉投資","被投資","策略聯盟"],
            "新聞": ["提及","gen_by_llm"],
        }
    def news_mention_company(self,code):
        from pipeline.news import News
        news_pipe = News(code)
        entities,relations = news_pipe.fetch_news_company_tuple()
        print(f"build ({code}) news property graph")
        print(f"len of entities :: {len(entities)}")
        print(f"len of relations :: {len(relations)}")
        # utils.show_EntityNodes(entities)
        # utils.show_Relations(relations)
        self.graph_store.upsert_nodes(entities)
        self.graph_store.upsert_relations(relations)
        return self.graph_store.close()
    
    def company_rel_company(self,code):
        """ 添加公司互動
            code,name,suppliers,customers,competitor,strategic_alliance,invested 
        """
        from pipeline.company import CompanyInteractive 
        interactive = CompanyInteractive(code)
        print(f"build {code} relation property graph")
        entities,relations = interactive.fetch_rel_company_tuple()
        print(f"build ({code}) news property graph")
        print(f"len of entities :: {len(entities)}")
        print(f"len of relations :: {len(relations)}")
        # utils.show_EntityNodes(entities)
        # utils.show_Relations(relations)
        self.graph_store.upsert_nodes(entities)
        self.graph_store.upsert_relations(relations)
        self.graph_store.close()
        
    def remove_all(self):
        cmd = input("do you want to clean all graph? (y|n) : ")
        if cmd == 'n':
            return
        cypher = "MATCH (n) DETACH DELETE n"
        self.graph_store.structured_query(cypher)
        return self.graph_store.close()
    
if __name__ == "__main__":
    builder = ManualBuildPropertyGraph()
    from pipeline import utils
    codes = utils.get_codes()
    [builder.news_mention_company(code) for code in codes]