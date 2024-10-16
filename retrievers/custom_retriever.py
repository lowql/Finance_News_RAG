from llama_index.core.indices.property_graph import (
    LLMSynonymRetriever,
    VectorContextRetriever
)
from typing import Any, List,Optional
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.vector_stores import VectorStoreQuery
from setup import get_llm,get_property_graph_index_from_existing,get_embed_model,get_vector_store

SYNONYM_EXPAND_TEMPLATE = (
    "給定一些初始查詢，提取其中的關鍵字，並且產生總共最多 {max_keywords} 個同義詞或相關關鍵字，"
    "考慮通用表達方法的情況\n"
    "提供所有用 '^' 符號分隔的同義詞/關鍵字：'keyword1^keyword2^...'\n"
    "注意，結果應該是一行，用‘^’符號分隔。"
    "----\n"
    "查詢：{query_str}\n"
    "----\n"
    "關鍵字："
)
def parse_fn(output: str) -> list[str]:
    print("output","="*50)
    print(output)
    print("matches","="*50)
    matches = output.strip().split("^")
    print(matches)
    print("="*50)
    # capitalize to normalize with ingestion
    return [x.strip().capitalize() for x in matches if x.strip()]
index = get_property_graph_index_from_existing()
synonym_retriever = LLMSynonymRetriever(
    index.property_graph_store,
    llm=get_llm(),
    # include source chunk text with retrieved paths
    include_text=False,
    synonym_prompt=SYNONYM_EXPAND_TEMPLATE,
    output_parsing_fn=parse_fn,
    max_keywords=5,
    # the depth of relations to follow after node retrieval
    path_depth=1,
)

###################################################
class CustomVectorRetriever(BaseRetriever):
    def __init__(self):
        self._vector_store = get_vector_store(node_label="新聞")
        self._query_mode = "default"
        self._embed_model = get_embed_model()
        self._similarity_top_k = 5
        super().__init__()
    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve."""
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

        return nodes_with_scores

vector_retriever = CustomVectorRetriever()
retriever = index.as_retriever(sub_retrievers=[vector_retriever,synonym_retriever])

query_text = "統一集團近年的獲利趨勢"
nodes = retriever.retrieve(query_text)
[print(node) for node in nodes]

####
from llama_index.core.query_engine import RetrieverQueryEngine

query_engine = RetrieverQueryEngine.from_args(retriever)
response = query_engine.query(query_text)
print(str(response))
