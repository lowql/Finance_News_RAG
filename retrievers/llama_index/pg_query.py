from llama_index.core import PropertyGraphIndex

from llama_index.core import Settings
from setup import get_embed_model,get_llm,get_graph_store
from utils.test_tools import display_prompt_dict,display_nodes
from utils.get import get_prompt_template

Settings.llm = get_llm()
Settings.embed_model = get_embed_model()
graph_store = get_graph_store()
index = PropertyGraphIndex.from_existing(
    property_graph_store=graph_store,
    use_async = False,
)
    
def update_query_prompt(query_engine):
    display_prompt_dict(query_engine.get_prompts())
    query_engine.update_prompts(
        {"response_synthesizer:text_qa_template": get_prompt_template('text_qa'),
         "response_synthesizer:refine_template":get_prompt_template('refine')
        },
        
    )
    display_prompt_dict(query_engine.get_prompts())
    
def pg_retriever_query(query_txt,response_mode="no_text"):
    from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
    retriever = index.as_retriever(similarity_top_k=5) 
    query_engine = RetrieverQueryEngine.from_args(retriever, response_mode=response_mode)
    update_query_prompt(query_engine)
    response = query_engine.query(query_txt)
    display_nodes(response.source_nodes)
    print()
    print(response)
    
def pg_query(query_txt,response_mode="tree_summarize"):
    query_engine = index.as_query_engine(response_mode=response_mode)
    display_prompt_dict(query_engine.get_prompts())
    
    response = query_engine.query(query_txt)
    print(response.source_nodes)

if __name__ == '__main__':
    from llama_index.core.response_synthesizers import ResponseMode
    pg_retriever_query("ResponseMode.NO_TEXT",ResponseMode.NO_TEXT)
    # pg_query("NO_TEXT",ResponseMode.NO_TEXT)
    # pg_query("CONTEXT_ONLY",ResponseMode.CONTEXT_ONLY)
    
