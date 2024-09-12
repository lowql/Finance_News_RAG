
from utils.path_manager import get_news_content_file
from llama_index.core import Document

def fetch_documents():
    documents = []
    with open(get_news_content_file(6125),'r',encoding='utf8') as csvfile:
        import csv
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            documents.append(Document(
                text=row['content'],
                metadata={'author':row['author'],'headline':row['headline']},
                metadata_seperator="\n",
                metadata_template="{key} [ {value} ] ",
                text_template="Metadata:\n {metadata_str}\n-----\nContent: {content}",
                ))
    return documents
def build_kg_not_clean(neo4j_connection):
    documents = fetch_documents()
    driver = neo4j_connection
    driver.set_prompt_template()
    index = driver.build_index_from_documents(documents=documents)
    return driver,index

def test_build_not_clean(neo4j_connection):
    driver,index = build_kg_not_clean(neo4j_connection)
    retriever = index.as_retriever(include_text=False)
    from llama_index.core import PromptTemplate
    text_qa_template = PromptTemplate(driver.text_qa_template)
    refine_template = PromptTemplate(driver.refine_template)
    from llama_index.core import get_response_synthesizer
    synth = get_response_synthesizer(response_mode="refine",streaming=True,refine_template=refine_template,text_qa_template=text_qa_template)
    from llama_index.core.query_engine import RetrieverQueryEngine
        
    from llama_index.core.postprocessor import SimilarityPostprocessor
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer = synth,
        node_postprocessors=[
            SimilarityPostprocessor(similarity_cutoff=0.7)  # 设置相似度阈值
        ]
    )
    query_engine.from_args(
        retriever=retriever,
        response_mode= 'compact',
        verbose=False,
        
    )
    response = query_engine.query("請介紹廣運")
    response.print_response_stream()
    
    for node in response.source_nodes:
        print(f"Content: {node.get_content()}")
            
    print(len(response.source_nodes))
    
def test_template(neo4j_connection):
    driver = neo4j_connection
    driver.set_prompt_template()
    print("\nbelow is kg extract template\n")
    print(f"data type is: {type(driver.kg_extract_templete)}")
    print(driver.kg_extract_templete)
    print("\nbelow is refine template\n")
    print(f"data type is: {type(driver.refine_template)}")
    print(driver.refine_template)
    print("\nbelow is text qa template\n")
    print(f"data type is: {type(driver.text_qa_template)}")
    print(driver.text_qa_template)
    