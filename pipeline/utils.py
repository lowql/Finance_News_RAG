def show_documents(documents):
        """ 
        檢查 documents 的內實際內容
        """
        from llama_index.core.schema import MetadataMode
        for doc in documents:
            print(doc.get_content(MetadataMode.LLM))
            print("="*100)