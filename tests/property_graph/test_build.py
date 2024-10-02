from storages.build.property_graph import ManualBuildPropertyGraph
import os
news = os.listdir('./dataset/news/')
codes = [new.split('_')[0] for new in news]


builder = ManualBuildPropertyGraph()
def test_build_news():
    builder.news_mention_company(6125)

def test_build_company_rel():
    builder.company_rel_company(6125)

def test_remove_all():
    builder.remove_all()