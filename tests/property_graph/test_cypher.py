from retrievers.pg_query import graph_store
import pytest
""" 
why use vector index: https://neo4j.com/docs/cypher-manual/current/indexes/search-performance-indexes/using-indexes/

"""
keywords = ["焦點股","公告","盤中速報","熱門股","營收","大漲"]
def test_get_schema():
    print(graph_store.get_schema_str())
@pytest.mark.parametrize("keyword", keywords)
def test_string_match(keyword):
    print(f"keyword is {keyword}")
    cypher = """
    MATCH (n:`新聞`)-[:`提及`]->(c:`公司`)
    WHERE n.headline CONTAINS $keyword
    RETURN c.name as company,n.author AS author, n.headline AS headline
    LIMIT 5
    """
    rows = graph_store.structured_query(cypher,param_map={'keyword':keyword})
    [print(row) for row in rows]
regex_patterns = [".*子公司.*","^《.*》.*"]
@pytest.mark.parametrize("regex_pattern", regex_patterns)
def test_string_match_regex(regex_pattern):
    print(f"regex_pattern is {regex_pattern}")
    cypher = """
    MATCH (n:`新聞`)-[:`提及`]->(c:`公司`)
    WHERE n.headline  =~ $regex_pattern
    RETURN c.name as company,n.author AS author, n.headline AS headline
    LIMIT 5
    """
    rows = graph_store.structured_query(cypher,param_map={'regex_pattern':regex_pattern})
    [print(row )for row in rows]
def test_string_not_match_regex(regex_pattern="(^[【《].*[》】].*)"):
    print(f"regex_pattern is {regex_pattern}")
    cypher = """
    MATCH (n:`新聞`)-[:`提及`]->(c:`公司`)
    WHERE not n.headline  =~ $regex_pattern
    RETURN n.headline AS headline
    LIMIT 100
    """
    rows = graph_store.structured_query(cypher,param_map={'regex_pattern':regex_pattern})
    [print(row )for row in rows]
def test_check_category_be_set():
    cypher = """
    MATCH (n:`新聞`)
    WHERE n.category IS NOT NULL
    RETURN n.headline as headline, n.category as category
    """
    rows = graph_store.structured_query(cypher)
    [print(row )for row in rows]
def test_check_category_not_be_set():
    cypher = """
    MATCH (n:`新聞`)
    WHERE n.category IS NULL
    RETURN n.headline as headline, n.category as category
    """
    rows = graph_store.structured_query(cypher)
    [print(row )for row in rows]
regex_patterns = ["^《.*》.*"]
@pytest.mark.parametrize("regex_pattern", regex_patterns)
def test_string_match_regex_then_order(regex_pattern):
    print(f"regex_pattern is {regex_pattern}")
    cypher = """
    MATCH (n:`新聞`)-[:`提及`]->(c:`公司`)
    WHERE n.headline =~ $regex_pattern
    WITH c.name as company, n.author AS author, n.headline AS headline,
        CASE
            WHEN n.headline CONTAINS '《台北股市》' THEN '台北股市'
            WHEN n.headline CONTAINS '《金融股》' THEN '金融股'
            ELSE '其他'
        END AS category
    WHERE category = '其他'
    RETURN DISTINCT  headline
    ORDER BY headline
    """
    rows = graph_store.structured_query(cypher,param_map={'regex_pattern':regex_pattern})
    [print(row )for row in rows]
def test_temporal_type():
    cypher = """
        MATCH (n:新聞)
        WHERE datetime(n.time) > datetime("2023-10-01T00:00:00")
        AND datetime(n.time) < datetime("2023-10-31T23:59:59")
        RETURN n.headline as headline, n.time as time
    """
    rows = graph_store.structured_query(cypher)
    [print(row )for row in rows]
def test_not_relation():
    """ 
    列出所有 還未 gen_by_llm 的新聞 Nodes
    """
    cypher = """
    MATCH (n:`新聞`)
    WHERE NOT (n)-[:gen_by_llm]->()
    RETURN n
    """
    rows = graph_store.structured_query(cypher)
    [print(row) for row in rows]
def test_regex_category_filter():
    """ 
    我需要 "^《.*》.*" 匹配到的內容只顯示一次\n
    {'category': '《數位雲端》富邦媒6月、H1營收同期高 7月整「裝」續衝'}\n
    {'category': '《百貨股》富邦媒6月5日除息'}\n
    效果應該如下\n
    {'category': '《百貨股》'}\n
    {'category': '《數位雲端》'}\n
    """
    cypher = """
    MATCH (n:`新聞`)
    WHERE n.headline =~ "^《.*》.*"
    WITH n.headline as headline,split(n.headline, "》")[0] + "》" AS category
    RETURN category, headline
    """
    # Variable `n` not defined
    rows = graph_store.structured_query(cypher)
    [print(row) for row in rows]
def test_create_vector_index():
    """ 
    我們將結合使用文字嵌入相似度和單字距離來尋找潛在的重複項。我們先定義圖中實體的向量索引。
    """
    graph_store.structured_query("""
        CREATE VECTOR INDEX entity IF NOT EXISTS
        FOR (m:`__Entity__`)
        ON m.embedding
        OPTIONS {indexConfig: {
            `vector.dimensions`:4096,
            `vector.similarity_function`: 'cosine'
        }}""")
def test_finds_duplicates():
    """ 
     在不涉及太多細節的情況下，我們結合使用文字嵌入和單字距離來尋找圖中潛在的重複項。
     您可以調整相似度閾值和單字距離來找到檢測盡可能多的重複項而不會出現太多誤報的最佳組合。
     不幸的是，實體消歧是一個難題，沒有完美的解決方案。透過這種方法，我們得到了相當好的結果，但也存在一些誤報
    """
    similarity_threshold = 0.9
    word_edit_distance = 5
    data = graph_store.structured_query("""
        MATCH (e:__Entity__)
        CALL {
        WITH e
        CALL db.index.vector.queryNodes('entity', 10, e.embedding)
        YIELD node, score
        WITH node, score
        WHERE score > toFLoat($cutoff)
            AND (toLower(node.name) CONTAINS toLower(e.name) OR toLower(e.name) CONTAINS toLower(node.name)
                OR apoc.text.distance(toLower(node.name), toLower(e.name)) < $distance)
            AND labels(e) = labels(node)
        WITH node, score
        ORDER BY node.name
        RETURN collect(node) AS nodes
        }
        WITH distinct nodes
        WHERE size(nodes) > 1
        WITH collect([n in nodes | n.name]) AS results
        UNWIND range(0, size(results)-1, 1) as index
        WITH results, index, results[index] as result
        WITH apoc.coll.sort(reduce(acc = result, index2 IN range(0, size(results)-1, 1) |
                CASE WHEN index <> index2 AND
                    size(apoc.coll.intersection(acc, results[index2])) > 0
                    THEN apoc.coll.union(acc, results[index2])
                    ELSE acc
                END
        )) as combinedResult
        WITH distinct(combinedResult) as combinedResult
        // extra filtering
        WITH collect(combinedResult) as allCombinedResults
        UNWIND range(0, size(allCombinedResults)-1, 1) as combinedResultIndex
        WITH allCombinedResults[combinedResultIndex] as combinedResult, combinedResultIndex, allCombinedResults
        WHERE NOT any(x IN range(0,size(allCombinedResults)-1,1) 
            WHERE x <> combinedResultIndex
            AND apoc.coll.containsAll(allCombinedResults[x], combinedResult)
        )
        RETURN combinedResult  
    """, param_map={'cutoff': similarity_threshold, 'distance': word_edit_distance})
    for row in data:
        print(row)

graph_store.close()   