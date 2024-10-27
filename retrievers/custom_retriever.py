from llama_index.core.indices.property_graph import (
    LLMSynonymRetriever,
)
import re
from typing import Any, List,Optional
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore,TextNode
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.vector_stores import VectorStoreQuery
from setup import get_graph_store,get_llm,get_property_graph_index_from_existing,get_embed_model,get_vector_store

class CustomFullTextRetriever(BaseRetriever):
    def __init__(self):
        self.graph_store = get_graph_store()
        self._similarity_top_n = 3
        super().__init__()
    def get_company_interaction_cypher(self,query_bundle: QueryBundle):
        call = f'CALL db.index.fulltext.queryNodes("keyword", {query_bundle.query_str}) YIELD node, score\n'
        rule = """
        WHERE node.info IS NOT NULL\n
        WITH collect({node: node, score: score}) as results\n
        WITH results, max(results[0].score) as maxScore\n
        UNWIND results as result\n
        WITH result.node as node, result.score as score, maxScore\n
        WHERE score > maxScore-0.4\n
        """
        return_rule = "RETURN node.info as content, score"
        return call + rule + return_rule
    def get_normal_search_cypher(self,query_bundle: QueryBundle):
        call = f'CALL db.index.fulltext.queryNodes("keyword", {query_bundle.query_str}) YIELD node, score\n'
        rule = f'where node.content is not null\n'
        return_rule = f'RETURN score,node.content as content,node.time as time limit {self._similarity_top_n}'
        
        return call + rule + return_rule
    def check_cypher(self,cypher:str):
        print('='*50)
        print(cypher)
        print('='*50)
    def _retrieve(self,query_bundle: QueryBundle) -> List[NodeWithScore]:

        normal_search_cypher = self.get_normal_search_cypher(query_bundle=query_bundle)
        self.check_cypher(normal_search_cypher)
        normal_raw_nodes = self.graph_store.structured_query(normal_search_cypher)
        
        company_interaction_cypher = self.get_company_interaction_cypher(query_bundle=query_bundle)
        self.check_cypher(company_interaction_cypher)
        company_interaction_raw_nodes = self.graph_store.structured_query(company_interaction_cypher)
        
        raw_nodes = company_interaction_raw_nodes[:3] + normal_raw_nodes
        nodes_with_scores = []
        for node in raw_nodes:
            content = TextNode(text=f'事實發生日期:{node.get("time")}\n{node["content"]}')
            nodes_with_scores.append(NodeWithScore(node=content, score=node["score"]))
        print("="*10,"node from fulltext retriever","="*10)
        [print(n) for n in nodes_with_scores]
        print("="*25)
        return nodes_with_scores

class CustomVectorRetriever(BaseRetriever):
    def __init__(self):
        self._vector_store = get_vector_store(node_label="__Node__")
        self._query_mode = "default"
        self._embed_model = get_embed_model()
        self._similarity_top_k = 2
        super().__init__()
    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve."""
        print("="*10,"node from vector retriever","="*10)
        if query_bundle.embedding is None:
            query_embedding = self._embed_model.get_query_embedding(
                query_bundle.query_str
            )
        else:
            query_embedding = query_bundle.embedding

        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=self._similarity_top_k,
            mode=self._query_mode,
        )
        query_result = self._vector_store.query(vector_store_query)

        nodes_with_scores = []
        for index, node in enumerate(query_result.nodes):
            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
            nodes_with_scores.append(NodeWithScore(node=node, score=score))

        
        [print(n) for n in nodes_with_scores]
        print("="*25)
        return nodes_with_scores

SYNONYM_EXPAND_TEMPLATE = (
    "你現在只是工具處理特定任務，給定一些初始查詢，提取其中的關鍵字，並且產生總共最多 {max_keywords} 個同義詞或相關關鍵字，"
    "考慮通用表達方法的情況\n"
    "提供所有用 '^' 符號分隔的同義詞/關鍵字：'keyword1^keyword2^...'"
    "注意，結果必須是只有一行，並且用 ^ 符號分隔。"
    "輸出格式請直接參照範例: 關鍵字1^關鍵字2^關鍵字3^.... ，除此之外不要有任何回覆"
    "----\n"
    "查詢：{query_str}\n"
    "----\n"
    "關鍵字："
)
class CustomNeo4jRetriever:
    def __init__(self):
        self.index = get_property_graph_index_from_existing()
        self.synonym_retriever = self._get_llm_synonym_retriever()
        self.vector_retriever = CustomVectorRetriever()
        self.fulltext_retriever = CustomFullTextRetriever()
    def _parse_fn(self,output: str) -> list[str]:
        print("="*25,"LLMSynonymRetriever output","="*25)
        print(output)
        try:
            output = re.findall(".*。",output)[0]
        except:
            return []
        matches = output.strip(" 。").split("^")
        print(matches)
        print("="*50)
        # capitalize to normalize with ingestion
        return [x.strip() for x in matches if x.strip()]
    def _get_llm_synonym_retriever(self):
        return LLMSynonymRetriever(
            self.index.property_graph_store,
            llm=get_llm(),
            # include source chunk text with retrieved paths
            include_text=False,
            synonym_prompt=SYNONYM_EXPAND_TEMPLATE,
            output_parsing_fn=self._parse_fn,
            max_keywords=5,
            # the depth of relations to follow after node retrieval
            path_depth=1,
        )
    
    def get_retriever(self):
        return self.index.as_retriever(sub_retrievers=[self.fulltext_retriever,self.vector_retriever,self.synonym_retriever])
    

if __name__ == "__main__":
    query_text = "統一集團近年的獲利趨勢"
    
    fulltext_retriever = CustomFullTextRetriever()
    cypher = fulltext_retriever.get_company_interaction_cypher(query_bundle=QueryBundle(query_str=query_text))
    print(cypher)
    cypher = fulltext_retriever.get_normal_search_cypher(query_bundle=QueryBundle(query_str=query_text))
    print(cypher)
    # retriever = CustomRetriever().get_retriever()
    # nodes = retriever.retrieve(query_text)
    # [print(node) for node in nodes]

    # from llama_index.core.query_engine import RetrieverQueryEngine

    # query_engine = RetrieverQueryEngine.from_args(retriever)
    # response = query_engine.query(query_text)
    # print(str(response))
