from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.core.extractors import TitleExtractor,KeywordExtractor,SummaryExtractor
from llama_index.core.indices.property_graph import DynamicLLMPathExtractor,ImplicitPathExtractor
from llama_index.core.indices import PropertyGraphIndex
import re
from typing import Literal
from utils.path_manager import get_llama_index_template
from jinja2 import Template
from llama_index.core.schema import Document,TransformComponent
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.settings import Settings
def get_embed_model():
    from llama_index.embeddings.ollama import OllamaEmbedding
    ollama_embedding = OllamaEmbedding(
        model_name="viosay/conan-embedding-v1:latest",
        base_url="http://localhost:11434",
        ollama_additional_kwargs={"mirostat": 0}
    )
    return ollama_embedding

def get_llm():
    from llama_index.llms.ollama import Ollama
    llm = Ollama(model='jcai/llama3-taide-lx-8b-chat-alpha1:Q4_K_M',request_timeout=600)
    return llm

Settings.llm = get_llm()
Settings.embed_model = get_embed_model()

class CustomNewExtractor(TransformComponent):
    def __call__(self, nodes, **kwargs):
        
        for node in nodes:
            headline = node.metadata['headline']
            author = node.metadata['author']
            time = node.metadata['time']
            if "【公告】" in node.metadata['headline']:
                print(node.get_content())
                documents = []
                announcement_metainfo,sections = self.parse_announcement(node.get_content())
                print(announcement_metainfo)
                for section in sections:
                    documents.append(
                        Document(
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
                            text_template="公告基本資訊:\n {metadata_str}\n\n 公告消息:\n {content}"
                        ))
                return documents
            else:
                return nodes
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

        self.allowed_entity_props = [] # TODO　未研究詳細處理機制
        self.allowed_relation_props = [] # TODO 未研究詳細處理機制

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
                        max_triplets_per_chunk=3,
                        num_workers=4,
                        extract_prompt=self.set_prompt_template("DYNAMIC_EXTRACT_TMPL.jinja"),
                        allowed_entity_types= self.allowed_entity_types,
                        allowed_relation_types= self.allowed_relation_types
                    )
    def get_sentence_splitter(self):
        return SentenceSplitter(paragraph_separator="\n",chunk_size=5000)
    def get_custom_extractor(self):
        return CustomNewExtractor()


from config.db_config import Neo4j_USER,Neo4j_PWD,Neo4j_URI
def get_graph_store():
    from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
    return Neo4jPropertyGraphStore(
        username=Neo4j_USER,
        password=Neo4j_PWD,
        url=Neo4j_URI,
    )

def get_vector_store(**kwargs):
    """ 
    :params retrieval_query(str): 
    :params node_label(str):  setup for Node label name i.e. MERGE(n:\<_node_label_\>)
    :params index_name(str): setup for vector index\n
        原則上 vector index name ，就是維持不變，所有的 node label 的 node.embedding都共同使用
    :params text_node_property(str): setup for fulltext index \n
        Noe4jVectorStore 自帶的 create_new_keyword_index 沒辦法額外設定中文分詞，所以另外在
        test_build 手工使用 Cypher 建立 fulltext index。
    """
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

def get_property_graph_index_from_existing():
    return PropertyGraphIndex.from_existing(
        property_graph_store=get_graph_store(),
        vector_store=get_vector_store(node_label="新聞"),
    )
    
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