from llama_index.core import PropertyGraphIndex

from llama_index.core import Settings
from setup import get_embed_model,get_llm,get_graph_store
from utils.test_tools import display_prompt_dict
from utils.get import get_prompt_template

Settings.llm = get_llm()
Settings.embed_model = get_embed_model()
def update_query_prompt(query_engine):
    display_prompt_dict(query_engine.get_prompts())
    query_engine.update_prompts(
        {"response_synthesizer:text_qa_template": get_prompt_template('text_qa')}
    )
    display_prompt_dict(query_engine.get_prompts())
    
def pg_query(query_txt,response_mode="tree_summarize"):
    print('###',query_txt,'\n')
    graph_store = get_graph_store()
    index = PropertyGraphIndex.from_existing(
        property_graph_store=graph_store,
        use_async = False,
    )
    
    query_engine = index.as_query_engine(response_mode=response_mode)
    display_prompt_dict(query_engine.get_prompts())
    
    
    print(type(query_engine),'\n')
    # response = query_engine.query(query_txt)
    # return response

if __name__ == '__main__':
    from llama_index.core.response_synthesizers import ResponseMode
    pg_query("ResponseMode.REFINE",ResponseMode.REFINE)
    pg_query("ResponseMode.NO_TEXT",ResponseMode.NO_TEXT)
    pg_query("ResponseMode.COMPACT",ResponseMode.COMPACT)
    pg_query("ResponseMode.ACCUMULATE",ResponseMode.ACCUMULATE)
    pg_query("ResponseMode.COMPACT_ACCUMULATE",ResponseMode.COMPACT_ACCUMULATE)
    pg_query("ResponseMode.TREE_SUMMARIZE",ResponseMode.TREE_SUMMARIZE)
    pg_query("ResponseMode.SIMPLE_SUMMARIZE",ResponseMode.SIMPLE_SUMMARIZE)
    pg_query("ResponseMode.CONTEXT_ONLY",ResponseMode.CONTEXT_ONLY)
    
