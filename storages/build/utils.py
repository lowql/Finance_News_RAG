from llama_index.llms.ollama import Ollama

models = ['llama3.1:latest','jcai/llama3-taide-lx-8b-chat-alpha1:Q4_K_M ']
model = models[1]
llm = Ollama(model=model, request_timeout=60.0)

def get_prompt(context):
    from llama_index.core import PromptTemplate

    template = """
"你現在是一位專業的財金播報員，請保持專業性並根據以下新聞內容，提取精簡重點。請以條列式Markdown格式輸出。"
"以下內容沒有提及解釋為目前資料庫內容不足，無法提供"
"\n---------------------\n"
"{context_str}"
"\n---------------------\n"
"請以以下格式回覆，不要超過50字："
- **公司名稱**：...
- **產業類別**：...
- **主要產品或服務**：...
- **市場趨勢**：...
- **近期財報**：...
- **營收表現**：...
- **未來展望**：...
- **競爭優勢**：...
- **股價表現**：...
- **分析師評級**：...
- **補充事項**:...
    """
    qa_template = PromptTemplate(template)

    # you can create text prompt (for completion API)
    prompt = qa_template.format(context_str=context)
    return prompt

def gen_summary(context,mode = 'batch'):
    print("=============================================================")
    print("use model is",model)
    print("=============================================================")
    if mode == 'stream':
        completions = llm.stream_complete(get_prompt(context))
        for completion in completions:
            print(completion.delta, end="")
    return llm.complete(get_prompt(context)).text

