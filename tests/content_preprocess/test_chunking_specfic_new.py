from utils.test_tools import fetch_document_as_df
from setup import get_llm
from llama_index.core.settings import Settings
from llama_index.core import Document

df = fetch_document_as_df()
filtered_df = df[df['headline'].str.contains('【公告】')]
Settings.llm = get_llm()
documents = {
    'content': filtered_df['content'].tolist(),
    'author': filtered_df['author'].tolist(),
    'headline': filtered_df['headline'].tolist()
}


print(f"文档数量: {len(documents['content'])}")
print(f"標題列表: {documents['headline']}")

# 创建 Document 对象列表
documents_obj = [
    Document(
        text=content,
        metadata={"author": author, "headline": headline}
    )
    for content, author, headline in zip(
        documents['content'],
        documents['author'],
        documents['headline']
    )
]
print('len of document_obj is ',len(documents_obj))

def display_nodes_info(nodes):
    print('len of nodes is',len(nodes))
    print('type of node is',type(nodes[0]))
    for i,node in enumerate(nodes):
        print(f"#{i}::\n {node.get_metadata_str()}\n {node.get_text()}\n")
    
""" 
我需要一個方式可以這樣分割chunk
chunks = re.split(r'(("日期"|"公司名稱"|"主旨"|發言人|"說明"):)', text)
日 期：2023年06月20日
公司名稱：廣運 (6125)
主 旨：代重要子公司金運-112年股東常會重要決議
發言人：沈麗娟
說 明：
    1.股東常會日期:112/06/20
    2.重要決議事項一、盈餘分配或盈虧撥補:承認本公司111年度盈餘分配表案。
    3.重要決議事項二、章程修訂:通過。
    4.重要決議事項三、營業報告書及財務報表:承認111年度決算表冊案。
    5.重要決議事項四、董監事選舉:無。
    6.重要決議事項五、其他事項:
        (1) 修訂本公司「章程」案:通過。
        (2) 修訂本公司『取得或處分資產處理程序』案:通過。
        (3) 資本公積配發股東紅利案:通過。
    7.其他應敘明事項:無。
並可以整合進 llama-index
"""
import re
from typing import List, Tuple
def split_chunks(text: str) -> List[Tuple[str, str]]:
    # 定義主要分割的關鍵詞
    main_keywords = ["日 期", "公司名稱", "主 旨", "發言人", "說 明"]
    
    # 創建主要分割的正則表達式模式
    main_pattern = "|".join(map(re.escape, main_keywords))
    
    # 分割文本
    main_chunks = re.split(f'({main_pattern})：', text)
    
    # 移除空白的chunks
    main_chunks = [chunk.strip() for chunk in main_chunks if chunk.strip()]
    
    # 將chunks組合成(title, content)的元組
    result = []
    for i in range(0, len(main_chunks), 2):
        if i + 1 < len(main_chunks):
            chunk_title = main_chunks[i]
            chunk_content = main_chunks[i+1].strip()
            
            # 對 "說 明" 部分進行進一步處理
            if chunk_title == "說 明":
                sub_chunks = re.split(r'(\d+\.)', chunk_content)
                sub_chunks = [chunk.strip() for chunk in sub_chunks if chunk.strip()]
                
                for j in range(0, len(sub_chunks), 2):
                    if j + 1 < len(sub_chunks):
                        sub_title = f"說 明 {sub_chunks[j]}"
                        sub_content = sub_chunks[j+1].strip()
                        result.append((sub_title, sub_content))
            else:
                result.append((chunk_title, chunk_content))
    
    return result

def test_regex_chunks():
    print(type(documents_obj[0].get_text()))
    # print(documents_obj[0].get_text())
    chunks = split_chunks(documents_obj[0].get_text())
    print("len of chunks is:",len(chunks))
    for chunk_id, chunk_content in chunks:
        print(f"Chunk {chunk_id}:")
        print(chunk_content)
        print()

def test_recursive_character():
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from llama_index.core.node_parser import LangchainNodeParser

    parser = LangchainNodeParser(RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        separators=[
            "\n",
            "。",
        ],
    ))
    nodes = parser.get_nodes_from_documents(documents_obj)
    display_nodes_info(nodes)
    
def test_markdown_parser():
    from llama_index.core.node_parser import MarkdownNodeParser
    parser = MarkdownNodeParser()

    nodes = parser.get_nodes_from_documents(documents_obj)
    display_nodes_info(nodes)

""" too long time """
# def test_semantic_splitter():
#     from llama_index.core.node_parser import SemanticSplitterNodeParser
#     from setup import get_embed_model

#     parser = SemanticSplitterNodeParser(
#         buffer_size=1, breakpoint_percentile_threshold=95, embed_model=get_embed_model()
#     )
#     nodes = parser.get_nodes_from_documents(documents_obj)
#     display_nodes_info(nodes)