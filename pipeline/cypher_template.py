
class CypherTemplate():
    def fetch_documents():
        documents = []
        from llama_index.core import Document
        # prompt,cypher_query,ideal_response
        with open('./dataset/cypher/CypherQuery_example.csv','r',encoding='utf8') as csvfile:
            import csv
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                documents.append(Document(
                        text=row['cypher_query'],
                        metadata={'user_query':row['prompt']},
                        metadata_seperator="\n",
                        metadata_template="{key} : {value} ",
                        text_template="使用者提問:\n {metadata_str}\n\n對應的cypher回覆:\n {content}",
                    ))
        return documents