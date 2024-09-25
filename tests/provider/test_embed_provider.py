
def test_provider_from_ollama():
    pass

def test_provider_from_huggingface():
    from llama_index.llms.huggingface import HuggingFaceLLM
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