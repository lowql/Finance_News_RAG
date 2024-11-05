import requests
import logging
logger = logging.getLogger(__name__)
try:
    llm_url = "http://140.125.45.129:11434" 
    status_code = requests.get(llm_url).status_code
    logger.info(f"provider connect status code is {status_code}")
    llm_url = "http://140.125.45.129:11434"
except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
    llm_url = "http://localhost:11434"
    logger.info(f"please check local ollama is running")