from storages.build.property_graph import AutoBuildPropertyGraph,ManualBuildPropertyGraph,graph_store
import os
news = os.listdir('./dataset/news/')
codes = [new.split('_')[0] for new in news]

from dataset.download.helper import read_record
codes = read_record()

# auto_builder = AutoBuildPropertyGraph()
# def test_auto_builder():
#     auto_builder.build_index_from_documents()

builder = ManualBuildPropertyGraph()
def test_build_news():
    [builder.news_mention_company(code) for code in codes]
    
def test_build_company_rel():
    [builder.company_rel_company(code) for code in codes]

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

import pytest
keywords = ["焦點股","盤中速報","熱門股","盤後速報","潛力股"]
@pytest.mark.parametrize("keyword", keywords)
def test_set_news_keyword_category(keyword):
    print(f"keyword is {keyword}")
    cypher = """
    MATCH (n:`新聞`)-[:`提及`]->(c:`公司`)
    WHERE n.headline CONTAINS $keyword
    SET n.category = $keyword
    RETURN n.headline AS headline,n.category AS category
    """
    rows = graph_store.structured_query(cypher,param_map={'keyword':keyword})
    [print(row) for row in rows]

def test_set_summary_by_llm():
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
        MATCH (n:`新聞` {headline: $headline})
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

def test_remove_all():
    builder.remove_all()