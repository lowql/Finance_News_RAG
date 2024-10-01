1. 獲取資料集
    1. 從 FinMind API 獲得過往的歷史新聞
    2. 過濾新聞 (only yahoo)
    3. decode google RSS URL && drop unusable url
    4. fetch yahoo news && get new content
2. buid index && store index
    1. property graph
        1. 自動 DynamicLLMPathExtractor
        2. 手動 :: 根據新聞 Title 區分 不同的新聞型態，對應不同的內容提取形式
            1. TODO: research graph_store.structured_query()
            2. TODO: 評估 llm 對不同內容形式的提取形式
            3. TODO: 設計 cypher query
    2. vector 
        1. 


```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```