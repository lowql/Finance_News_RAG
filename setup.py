from config import Neo4j_USER,Neo4j_PWD,Neo4j_URI,llm_url
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.core.indices.property_graph import DynamicLLMPathExtractor
from llama_index.core.indices import PropertyGraphIndex
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.llms.ollama import Ollama
import re
import os
from typing import Literal
from utils.path_manager import get_llama_index_template
from llama_index.core.schema import Document,TransformComponent,MetadataMode
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.settings import Settings
import threading
import time
import sys
from itertools import cycle
import logging
from pathlib import Path

def setup_logging(log_file = 'rag.log'):
    """設定並測試logging功能"""
    
    # 確保日誌目錄存在
    log_dir = Path(log_file).parent
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)

    # 配置 logging
    try:
        # 創建 logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        
        # 確保 logger 沒有重複的處理器
        if not logger.handlers:
            # 創建檔案處理器
            file_handler = logging.FileHandler(log_file, 'w', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # 創建格式器
            formatter = logging.Formatter(
                '%(asctime)s - %(module)s - %(levelname)s : %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p'
            )
            file_handler.setFormatter(formatter)
            
            # 將處理器添加到 logger
            logger.addHandler(file_handler)
        
        # 測試日誌記錄
        logger.info("初始化 logger")
        
        # 強制寫入檔案
        for handler in logger.handlers:
            handler.flush()
            
        # 驗證日誌檔案
        if not os.path.exists(log_file):
            raise Exception("日誌檔案未被創建")
            
        if os.path.getsize(log_file) == 0:
            raise Exception("日誌檔案是空的")
            
        return logger
        
    except Exception as e:
        print(f"設定 logging 時發生錯誤: {e}")
        raise
logger = setup_logging()
logger.info("初始化 RAG flow 所需物件")
base_url = llm_url
class Provider():
    def __init__(self):
        self.embed_model = self.get_embed_model()
        self.llm = self.get_llm()
        self.reranker = self.get_reranker()
    def get_embed_model(self):
        from llama_index.embeddings.ollama import OllamaEmbedding
        model_name = "viosay/conan-embedding-v1:latest"
        logger.info(f"Current embedding model use {model_name}")
        ollama_embedding = OllamaEmbedding(
            model_name=model_name,
            base_url=base_url,
            ollama_additional_kwargs={"mirostat": 0}
        )
        return ollama_embedding
    
    #linux: curl http://140.125.45.129:11434:11434/api/generate -d '{"model": "jcai/llama3-taide-lx-8b-chat-alpha1:Q4_K_M","prompt":"Why is the sky blue?"}'
    #windows: 
    # curl -Uri "http://140.125.45.129:11434/api/generate" -Method Post -Body '{"model":"jcai/llama3-taide-lx-8b-chat-alpha1:Q4_K_M","prompt":"Why is the sky blue?"}' -ContentType "application/json"
    def get_llm(self):
        model_name = 'jcai/llama3-taide-lx-8b-chat-alpha1:Q4_K_M'
        logger.info(f"Current llm model use {model_name}")
        llm = Ollama(model=model_name,
                    base_url=base_url,
                    request_timeout=600)
        return llm

    def get_reranker(self,rerank_top_n=3):
        rerank_model = "BAAI/bge-reranker-large"
        print(f"============= Current rerank model use {rerank_model} ==============")
        rerank = SentenceTransformerRerank(model=rerank_model,top_n=rerank_top_n)
        return rerank
provider = Provider()
Settings.llm = provider.llm
Settings.embed_model = provider.embed_model
def get_embed_model():
    return provider.embed_model
def get_llm():
    return provider.llm
def get_reranker(rerank_top_n=None):
    if rerank_top_n is not None:
        provider.get_reranker(rerank_top_n=rerank_top_n)
    return provider.reranker

class CustomNewExtractor(TransformComponent):
    def __call__(self, nodes, **kwargs):
        
        for node in nodes:
            headline = node.metadata['headline']
            author = node.metadata['author']
            time = node.metadata['time']
            content = node.get_content()
            documents = []
            if "【公告】" in node.metadata['headline']:
                # print(content)
                announcement_metainfo,sections = self.parse_announcement(content)
                # print(announcement_metainfo)
                for section in sections:
                    document = Document(
                            text=section,
                            metadata={
                                'headline':headline,
                                'author':author,
                                'time':time,
                                "title": announcement_metainfo['title'],
                                "spokesperson": announcement_metainfo['spokesperson'],
                            },
                            metadata_seperator="\n",
                            metadata_template="{key} : {value} ",
                            text_template="公告基本資訊:\n{metadata_str}\n\n公告消息:\n{content}"
                        )
                    content = document.get_content(metadata_mode=MetadataMode.LLM)
                    document.set_content(content)
                    documents.append(document)
                return documents
            else:
                print("parse normal news")
                paragraphs = self.parse_normal_news(content)
                for paragraph in paragraphs:
                    document =  Document(
                            text=paragraph,
                            metadata={
                                'headline':headline,
                                'author':author,
                                'time':time,
                            },
                            metadata_seperator="\n",
                            metadata_template="{key} : {value} ",
                            text_template="===\n新聞基本資訊:\n{metadata_str}\n\n新聞內文:\n{content}\n===\n"
                        )
                    documents.append(document)
                return documents
    def parse_announcement(self,text):
        """ 
        {
            '主旨': '[更正]廣運董事會決議通過取得不動產案',
            '發言人': '沈麗娟',
            '說明': {
                '1': {
                    '標的物之名稱及性質（如坐落台中市北區ＸＸ段ＸＸ小段土地）': '位於桃園市平鎮區山子頂段土地及其上建物'
                },...
        """
        # 定義標題和內文的正則表達式模式
        title_pattern = re.compile(r"主\s*旨：(.+)")
        spokesperson_pattern = re.compile(r"發言人：(.+)")
        sections_pattern = re.compile(r"(\d+)\.(.+?):([\s\S]*?)(?=\n\d+\.|\Z)", re.MULTILINE)

        # 解析主旨
        title = title_pattern.search(text)
        title = title.group(1).strip() if title else ""

        # 解析發言人
        spokesperson = spokesperson_pattern.search(text)
        spokesperson = spokesperson.group(1).strip() if spokesperson else ""
        # 組合結果
        announcement_metainfo = {
            "title": title,
            "spokesperson": spokesperson,
        }
        # 解析說明中的條目
        sections = []
        for match in sections_pattern.finditer(text):
            section_number = match.group(1).strip()
            section_title = match.group(2).strip()
            section_content = match.group(3).strip()

            sections.append(f"{section_number}.{section_title} :: {section_content}")

        return announcement_metainfo,sections

    def parse_normal_news(self,text):
        base_split_pattern = re.compile(r"([^。\n;]+[。\n;])")
        matches = base_split_pattern.findall(text)
        paragraphs = [match.strip() for match in matches if match.strip()]
        return paragraphs
        
class Transformations:
    def __init__(self):
        self.max_knowledge_triplets = 3
        self.entities = Literal["公司", "新聞"]
        self.relations = Literal["有", "研發", "使用", "提及", "影響","有關"]
        self.allowed_entity_types = [
            "人物",      # 例如，企業高管、經濟學家等
            "公司",      # 公司，如蘋果公司、特斯拉等
            "公司產品",  # 公司生產的產品或服務
            "持有技術",  # 公司持有的技術或專利
            "行業",      # 行業，如科技、金融、能源等
        ]
        self.allowed_relation_types = [
            "發布",       
            "合作",  # 公司合作
            "發表",       # 發佈新產品或服務
            "營利表現", # 公司報告財務業績
            "投資",     # 公司或個人投資
            "合併",    # 兩家公司合併
        ]

        self.allowed_entity_props = None # TODO　未研究詳細處理機制
        self.allowed_relation_props = None # TODO 未研究詳細處理機制

    def set_prompt_template(self,template_file_name):
        with open(get_llama_index_template(template_file_name), 'r',encoding='utf8') as template_file:
            return template_file.read()
    def get_kg_dynamic_extractor(self):
        """ 
            相關設定\n
            extract_prompt: Optional[Union[str, PromptTemplate]] = None,\n
            parse_fn: Optional[Callable] = None,\n
            max_triplets_per_chunk: int = 10,\n
            num_workers: int = 4,\n
            allowed_entity_types: Optional[List[str]] = None,\n
            allowed_entity_props: Optional[Union[List[str], List[Tuple[str, str]]]] = None,\n
            allowed_relation_types: Optional[List[str]] = None,\n
            allowed_relation_props: Optional[\n
                Union[List[str], List[Tuple[str, str]]]\n
            ] = None,\n
        """
        return DynamicLLMPathExtractor(
                        llm=get_llm(),
                        max_triplets_per_chunk=10,
                        num_workers=4,
                        extract_prompt=self.set_prompt_template("DYNAMIC_EXTRACT_TMPL.jinja"),
                        allowed_entity_types= self.allowed_entity_types,
                        allowed_relation_types= self.allowed_relation_types
                    )
    def get_sentence_splitter(self):
        return SentenceSplitter(paragraph_separator="\n",secondary_chunking_regex="[^,.;。?!]+[,.;。?!]?",chunk_size=500)
    def get_custom_extractor(self):
        return CustomNewExtractor()

class GraphStore():
    def __init__(self):
        self.is_connecting = True
        self.connection_status = "init connection"
        progress_thread = threading.Thread(target=self._show_progress)
        progress_thread.start()
        
        try:
            logger.info("neo4j connecting...")
            self.connection_status = "connecting graph store"
            self.graph_store = self.get_graph_store()
            logger.info("graph store build done")
            self.connection_status = "connecting vector store"
            self.vector_store = self.get_vector_store(node_label="__Node__")
            logger.info("vector store build done")
            logger.info("neo4j connecting done")
            
            logger.info("index building")
            self.connection_status = "building index"
            self.index = self.get_property_graph_index_from_existing()
            logger.info("index building done")
        finally:
            # 完成後停止進度顯示
            self.is_connecting = False
            progress_thread.join()
    
    def _show_progress(self):
        spinner = cycle(['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])
        while self.is_connecting:
            sys.stdout.write(f'\r{next(spinner)} {self.connection_status}... ')
            sys.stdout.flush()
            time.sleep(0.5)
    def get_graph_store(self):
        logger.info(f"build graph store: {Neo4j_URI}")
        return Neo4jPropertyGraphStore(
            username=Neo4j_USER,
            password=Neo4j_PWD,
            url=Neo4j_URI,
        )

    def get_vector_store(self,**kwargs):
        """ 
        :params retrieval_query(str): 
        :params node_label(str):  setup for Node label name i.e. MERGE(n:\<_node_label_\>)
        :params index_name(str): setup for vector index\n
            原則上 vector index name ，就是維持不變，所有的 node label 的 node.embedding都共同使用
        :params text_node_property(str): setup for fulltext index \n
            Noe4jVectorStore 自帶的 create_new_keyword_index 沒辦法額外設定中文分詞，所以另外在
            test_build 手工使用 Cypher 建立 fulltext index。
        """
        logger.info(f"build vector store: {Neo4j_URI}")
        print("kwargs of vector store:",kwargs)
        return Neo4jVectorStore(
                username=Neo4j_USER,
                password=Neo4j_PWD,
                url=Neo4j_URI,
                embedding_dimension=1024,# Conan-embedding-v1:: huggingface 上面 embedding dim 是 1792 但 ollama 版本卻是 1024
                node_label= kwargs.get("node_label","LlamaChunk"),
                hybrid_search=kwargs.get("hybrid_search", False),
                text_node_property=kwargs.get("text_node_property", "content"),
                retrieval_query=kwargs.get("retrieval_query","")
            )

    def get_property_graph_index_from_existing(self):
        return PropertyGraphIndex.from_existing(
            property_graph_store=self.graph_store,
            vector_store=self.vector_store,
        )
store = GraphStore()
def get_graph_store(store=store):
    logger.info("get graph store")
    return store.graph_store
def get_vector_store(store=store,**kwargs):
    logger.info("get vector store")
    if kwargs:
        print("kwargs :",kwargs)
        return store.get_vector_store(kwargs=kwargs)
    else:
        print("get normal vector store")
        return store.vector_store
def get_property_graph_index_from_existing(store=store):
    logger.info("get graph index")
    return store.index

def get_synthesize():
    from llama_index.core.schema import NodeWithScore
    from llama_index.core.data_structs import Node
    from llama_index.core.response_synthesizers import ResponseMode
    from llama_index.core import get_response_synthesizer

    response_synthesizer = get_response_synthesizer(
        response_mode=ResponseMode.COMPACT
    )

    response = response_synthesizer.synthesize(
        "query text", nodes=[NodeWithScore(node=Node(text="text"), score=1.0)]
    )
   
    return response

if __name__ == '__main__':
    get_vector_store(index_name="new_vector")