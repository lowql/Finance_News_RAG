def get_prompt_template(type:str):
    from llama_index.core import PromptTemplate
    from utils.path_manager import get_llama_index_template
    with open(get_llama_index_template(type), 'r',encoding='utf8') as template_file:
            template =  template_file.read()
    prompt_tmpl = PromptTemplate(template)
    return prompt_tmpl