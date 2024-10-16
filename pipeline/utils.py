def get_codes():
    """ 取得所有成功收錄新聞的資料 """
    import os
    news = os.listdir('./dataset/news/')
    return [new.split('_')[0] for new in news]

def show_documents(documents):
        """ 
        檢查 documents 的內實際內容
        """
        from llama_index.core.schema import MetadataMode
        for doc in documents:
            print(doc.get_content(MetadataMode.LLM))
            print("="*100)

def show_EntityNodes(entities):
    """ from llama_index.core.graph_stores.types import EntityNode """
    for entity in entities:
        print(f"Entity:: id is {entity.name}")
        print(f"Entity:: label is {entity.label}")
        print(f"Entity:: property is {entity.properties}")
        if entity.properties is not None:
            for key,value in entity.properties.items():
                print(f"{key} :: {value}")
        print("="*50)
def show_Relations(relations):
    """ from llama_index.core.graph_stores.types import Relation """
    for relation in relations:
        print(f"Relation:: label is {relation.label}")
        print(f"Relation:: source is {relation.source_id}")
        print(f"Relation:: target is {relation.target_id}")
        if relation.properties is not None:
            for key,value in relation.properties.items():
                print(f"{key} :: {value}")
        print("="*50)
