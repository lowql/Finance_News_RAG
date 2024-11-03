from storages.build.property_graph import AutoBuildPropertyGraph,ManualBuildPropertyGraph
from storages.build.vector import build_News
from dataset.download.helper import read_record
from setup import get_graph_store,setup_logging
graph_store = get_graph_store()
codes = read_record()

""" 手工建立 KG """
manual_pg_builder = ManualBuildPropertyGraph()
def test_build_news_mention_company():
    [manual_pg_builder.news_mention_company(code) for code in codes]
    cypher = """match (n:`新聞`)
    set n :__Node__
    return n"""
    graph_store.structured_query(cypher)
    print("test_build_news_mention_company")
    
def test_build_company_rel():
    [manual_pg_builder.company_rel_company(code) for code in codes]
    print("test_build_company_rel")
    
def test_build_company_interaction_info_node():
    cypher = """
match (n:`公司`)
where n.code is not null
match (n)-[r]->(c)
where r:`供應商` or r:`客戶` or r:`競爭者` or r:`策略聯盟` or r:`被投資` or r:`轉投資`
with n as company, n.name + "的" + type(r) + "是" + c.name as interaction
merge (company)-[:`背景知識`]->(:`公司互動` {info:interaction})
    """
    graph_store.structured_query(cypher)
    print("test_build_company_interaction_info_node")

    
""" 手工建立 fulltext index """
def test_create_fulltext_index():
    cypher = """
create fulltext index keyword IF NOT EXISTS for (n:`__Node__`|`公司互動`) on each [n.text,n.content,n.info]
options {
    indexConfig: {
        `fulltext.analyzer` : 'cjk'
    }
}
    """
    graph_store.structured_query(cypher)
    print("test_create_fulltext_index")
""" 手工使用 cypher 設定分類新聞類別 """
def test_set_news_category():
    """
    {'category': '《熱門族群》', 'headline': '《熱門族群》AI需求高 建準、奇鋐重返月線'}\n
    {'category': '《台北股市》', 'headline': '《台北股市》AI搧風 凌陽創新、建準權證火'}\n
    {'category': '《電零組》', 'headline': '《電零組》建準樂觀明年 日系外資喊買助攻'}\n
    """
    cypher = """
    MATCH (n:`新聞`)
    WHERE n.headline =~ "^《.*》.*"
    WITH n as news,n.headline as headline,split(n.headline, "》")[0] + "》" AS category
    SET news.category = category
    RETURN category, headline
    """
    rows = graph_store.structured_query(cypher)
    [print(row) for row in rows]
    print("test_set_news_category")

""" 手工使用 cypher 設定公告消息類別 """
def test_set_news_notice_category():
    """ 
    {'headline': '【公告】統一應元富證券之邀參加線上法說會。'}
    """
    cypher = """
    MATCH (n:`新聞`)
    WHERE n.headline =~ "^【.*】.*"
    WITH n as news,n.headline as headline,split(n.headline, "】")[0] + "】" AS category
    SET news.category = category
    RETURN category, headline
    """
    rows = graph_store.structured_query(cypher)
    [print(row) for row in rows]
    print("test_set_news_notice_category")

""" 手工使用 cypher 根據關鍵字分類新聞"""
def test_set_news_keyword_category(keywords=["焦點股","盤中速報","熱門股","盤後速報","潛力股"]):
    for keyword in keywords:
        print(f"keyword is {keyword}")
        cypher = """
        MATCH (n:`新聞`)-[:`提及`]->(c:`公司`)
        WHERE n.headline CONTAINS $keyword
        SET n.category = $keyword
        RETURN n.headline AS headline,n.category AS category
        """
        rows = graph_store.structured_query(cypher,param_map={'keyword':keyword})
        [print(row) for row in rows]
        print("test_set_news_keyword_category")

""" 自動使用 LLM 產生新聞摘要 """
def test_set_summary_by_llm():
    print("test_set_summary_by_llm")
    from storages.build.utils import gen_summary
    cypher = """
    MATCH (n:`新聞`)-[:`提及`]->(c:`公司`)
    OPTIONAL MATCH (n)-[:gen_by_llm]->(s:`總結`)
    WITH n, s
    WHERE n.headline CONTAINS "焦點股" AND NOT n.author in ["時報資訊","中央社"] AND s IS NULL
    RETURN n.headline AS headline,n.author as author,n.content AS content
    """
    rows = graph_store.structured_query(cypher)
    for row in rows:
        print('\n','='*50,'\n',row['headline'],'\n','='*50,'\n')
        cypher = """
        MATCH (n:`新聞`:__Node__ {headline: $headline})
        OPTIONAL MATCH (n)-[:gen_by_llm]->(s:`總結`)
        WITH n, s
        WHERE s IS NULL
        MERGE (n)-[l:gen_by_llm]->(s_new:`總結` {content: $summary_gen_by_llm})
        RETURN s_new        
        """
        print("context summary is ")
        try:
            summary = gen_summary(row['content'])
            print(summary)
        except Exception as e:
            print(e)
            continue
        graph_store.structured_query(cypher,param_map={'headline':row['headline'],'summary_gen_by_llm':summary})
        
""" 手工建立 vector node  """
def test_build_news_with_vector():
    print("test_build_news_with_vector")
    [build_News(code) for code in codes]

def test_make_rel_of_embedding_news():
    cypher = """
    match(n:`新聞`)
    with n.name as headline,n as news
    match (em:`__Node__`)
    where em.embedding is not null and em.headline = headline
    merge (em)-[r:`根據`]->(news)
    """
    graph_store.structured_query(cypher)
    #移出重複生成的embedding nodes
    cypher = """
    // 首先找出要刪除的節點
    MATCH (s1)-[r1:`根據`]->(t1)
    MATCH (s2)-[r2:`根據`]->(t2)
    WHERE s1.headline = s2.headline 
    AND s1.content = s2.content
    AND s1.id > s2.id  // 確保只刪除ID較大的節點，保留最早的節點
    WITH COLLECT(DISTINCT s1) as nodesToDelete

    // 刪除這些節點的關係和節點
    UNWIND nodesToDelete as nodeToDelete
    OPTIONAL MATCH (nodeToDelete)-[r]-()
    DELETE r, nodeToDelete
    """
    graph_store.structured_query(cypher)
""" 自動使用 LLM 建立 KG """
auto_pg_builder = AutoBuildPropertyGraph()
def test_auto_builder():
    print("test_auto_builder")
    for code in codes:
        print(f"stock id {code} run auto kg builder")
        auto_pg_builder.build_News_KG_use_dynamicPathExtractor(code)
def test_remove_all():
    manual_pg_builder.remove_all()

if __name__ == "__main__":
    test_build_news_mention_company()
    test_build_company_rel()
    test_build_company_interaction_info_node()
    test_create_fulltext_index()
    test_set_news_category()
    test_set_news_notice_category()
    test_set_news_keyword_category()
    test_build_news_with_vector()
    
    # test_set_summary_by_llm()
    test_auto_builder()