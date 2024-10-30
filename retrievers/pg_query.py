from llama_index.core import get_response_synthesizer
from llama_index.core import Settings
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import NodeWithScore,QueryBundle,TextNode,MetadataMode
from setup import get_embed_model,get_llm,get_reranker,Transformations
from utils.get import get_prompt_template
from retrievers.custom_retriever import CustomNeo4jRetriever
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core import SummaryIndex
from typing import List,Optional
Settings.llm = get_llm()
Settings.embed_model = get_embed_model()

class MetadataNodePostprocessor(BaseNodePostprocessor):
    def _postprocess_nodes(
        self, nodes: List[NodeWithScore], query_bundle: Optional[QueryBundle]
    ) -> List[NodeWithScore]:
        new_nodes = []
        for n in nodes:
            # print(n.metadata)
            if n.metadata.get("time") is not None:
                time = n.metadata["time"]
                time_str = f"\n事件發生日期:  {str(time)}"
                base_node = TextNode(text=time_str+n.text)
            else:
                base_node = TextNode(text=n.text)
           
            new_nodes.append(NodeWithScore(node=base_node,score=n.score))
        return new_nodes


def query_response(retriever,query_txt,response_mode="no_text",streaming=True):    
    rerank_top_n = 3
    rerank = get_reranker(rerank_top_n)
    synth = get_response_synthesizer(
        streaming=streaming,
        text_qa_template=get_prompt_template("text_qa_template.jinja"),
        refine_template=get_prompt_template("refine_template.jinja"),
        response_mode=response_mode)
    query_engine = RetrieverQueryEngine.from_args(
        retriever,
        response_synthesizer=synth,
        node_postprocessors=[
            rerank,
            MetadataNodePostprocessor(),
            SimilarityPostprocessor(similarity_cutoff=0.6)
            ]
        )
    streaming_response = query_engine.query(query_txt)
    print("="*25,f"使用ReRank後的 top_{rerank_top_n} 參考資料",'='*25)
    [print(node) for node in streaming_response.source_nodes]
    print("="*25,"輸出",'='*25)
    return streaming_response

def query_from_neo4j(query_txt,response_mode="no_text"):
    retriever = CustomNeo4jRetriever().get_retriever()
    streaming_response = query_response(retriever=retriever,
                          query_txt=query_txt,
                          response_mode=response_mode,
                          streaming=True
                          )
    return streaming_response
    
def summary_news(documents,query_txt="",streaming=False):
    transformations = Transformations()
    pipeline = IngestionPipeline(
            transformations= [transformations.get_custom_extractor()],
        )
    documents = pipeline.run(documents=documents,num_workers=4)
    [print(node.get_content(metadata_mode=MetadataMode.LLM)) for node in documents]
    print(f"len of documents {len(documents)}")
    rerank = get_reranker(3)
    summary_index = SummaryIndex(nodes=documents)
    query_engine = summary_index.as_query_engine(streaming=streaming, node_postprocessors=[rerank,SimilarityPostprocessor(similarity_cutoff=0.01)])
    query_engine.update_prompts({
        "response_synthesizer:text_qa_template":get_prompt_template("text_qa_template.jinja"),
        "response_synthesizer:refine_template":get_prompt_template("refine_template.jinja"),
        })
    # [print(f"===\n**Prompt Key**: {k}\n" f"**Text:** \n{p.get_template()}\n====\n") for k, p in query_engine.get_prompts().items()]
    streaming_response = query_engine.query(query_txt)
    [print(node) for node in streaming_response.source_nodes]
    return streaming_response
    
    
if __name__ == '__main__':
    from pipeline.news import News
    news = News(6125)
    documents = news.fetch_documnets()
    summary_news(documents=documents[:2],response_mode="refine")
    
