import requests

try:
    llm_url = "http://140.125.45.129:11434" 
    status_code = requests.get(llm_url).status_code
    print(f"provider connect status code is {status_code}")
    llm_url = "http://140.125.45.129:11434"
except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
    llm_url = "http://localhost:11434"
    print(f"please check local ollama is running")