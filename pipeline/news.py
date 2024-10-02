from dataset.utils import fetch_news

class Pipeline:
    def __init__(self,code):
        self.code = code
        self.df = fetch_news(code)
        self.documents = self.df['content'].tolist()
        self.meta_headline =  self.df['headline'].tolist()
        self.meta_author =  self.df['author'].tolist()
        self.meta_time =  self.df['time'].tolist()
        
    def news_nodes(self):
        from llama_index.core.schema import TextNode
        nodes = []
        for idx, document in enumerate(self.documents):
            node = TextNode(text=document,metadata={
                'headline':self.meta_headline[idx],
                'author':self.meta_author[idx],
                'time':self.meta_time[idx]})
            nodes.append(node)
        # print(nodes[0].metadata)
        # print(nodes[0].get_content())
        return nodes