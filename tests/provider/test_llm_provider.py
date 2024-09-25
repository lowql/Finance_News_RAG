
def get_prompt():
    from llama_index.core.llms import ChatMessage, MessageRole
    from llama_index.core import ChatPromptTemplate
    """
    If you add a new proposition to a chunk, you may want to update the summary or else they could get stale
    """
    chunk = {}
    chunk['propositions'] = 'The month is October.'
    chunk['summary'] = 'time info'
    summary_template =  [
         ChatMessage(content="""\nYou are the steward of a group of chunks which represent groups of sentences that talk about a similar topic
            一個新的命題剛剛添加到您的一個區塊中，您應該產生一個非常簡短的一句話摘要，它將告訴觀眾塊組的含義。
            一個好的摘要會說明該區塊的內容，並給出有關添加到該區塊的內容的任何澄清說明。
            您將獲得一組位於該區塊中的命題以及該區塊的當前摘要。
            你的總結應該預見到概括性。
            如果你得到一個關於蘋果的建議，請將其推廣到食物。或月份，概括為「日期和時間」。
            例子：
            輸入： Proposition ：Greg 喜歡吃披薩
            輸出：此區塊包含有關格雷格喜歡吃的食物類型的信息。
            Only respond with the chunk new summary, nothing else.""", 
            role=MessageRole.SYSTEM),
         ChatMessage(content="""\n區塊 propositions:\n{proposition}\n\n 當前區塊 summary:\n{current_summary}""",
                     role=MessageRole.USER)
        ]
    chat_template = ChatPromptTemplate(message_templates=summary_template)
    messages = chat_template.format(proposition=chunk['propositions'],current_summary=chunk['summary'])
    return messages

def test_provider_from_ollama():
    from setup import get_llm
    llm = get_llm()
    res = llm.complete("給我說笑話在50字內")
    print(res)
    
def test_provider_from_huggingface():
    from llama_index.llms.huggingface import HuggingFaceLLM
    from huggingface_hub import login
    from dotenv import load_dotenv
    import os

    load_dotenv(dotenv_path='.env')
    login(token = os.getenv("hf_token"))
    # This uses https://huggingface.co/taide/Llama3-TAIDE-LX-8B-Chat-Alpha1
    # downloaded (if first invocation) to the local Hugging Face model cache,
    # and actually runs the model on your local machine's hardware
    locally_run = HuggingFaceLLM(model_name="taide/Llama3-TAIDE-LX-8B-Chat-Alpha1")
    completion_response = locally_run.complete("To infinity, and")
    print(completion_response)

def test_provider_from_llama_cpp():
    pass

def test_provider_from_groq():
    pass