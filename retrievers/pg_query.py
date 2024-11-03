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
import nest_asyncio
from setup import setup_logging
nest_asyncio.apply()
logger = setup_logging()
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
    rerank = get_reranker()
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
            # SimilarityPostprocessor(similarity_cutoff=0.3)
            ]
        )
    response = query_engine.query(query_txt)
    
    logger.info(f"使用ReRank後的 top_3 參考資料")
    [logger.info(f"\n{node}\n") for node in response.source_nodes]
    
    return response

def query_from_neo4j(query_txt,response_mode="refine"):
    retriever = CustomNeo4jRetriever().get_retriever()
    response = query_response(retriever=retriever,
                          query_txt=query_txt,
                          response_mode=response_mode,
                          streaming=False
                          )
    logger.info(f"response.source_nodes")
    for node in response.source_nodes:
        logger.info(f"\n{node}\n")
    return response
    
def summary_news(documents,query_txt="",streaming=False):
    transformations = Transformations()
    pipeline = IngestionPipeline(
            transformations= [transformations.get_custom_extractor()],
        )
    documents = pipeline.run(documents=documents,num_workers=10)
    [print(node.get_content(metadata_mode=MetadataMode.LLM)) for node in documents]
    print(f"len of documents {len(documents)}")
    rerank = get_reranker()
    summary_index = SummaryIndex(nodes=documents)
    query_engine = summary_index.as_query_engine(streaming=streaming, node_postprocessors=[rerank,SimilarityPostprocessor(similarity_cutoff=0.05)])
    query_engine.update_prompts({
        "response_synthesizer:text_qa_template":get_prompt_template("text_qa_template.jinja"),
        "response_synthesizer:refine_template":get_prompt_template("refine_template.jinja"),
        })
    # [print(f"===\n**Prompt Key**: {k}\n" f"**Text:** \n{p.get_template()}\n====\n") for k, p in query_engine.get_prompts().items()]
    response = query_engine.query(query_txt)
    logger.info(f"response.source_nodes")
    [logger.info(f"\n{node}\n") for node in response.source_nodes]
    return response
    
    
if __name__ == '__main__':
    from pipeline.news import News
    news = News(6125)
    documents = news.fetch_documents()
    summary_news(documents=documents[:2],response_mode="refine")
    
