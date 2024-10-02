from storages.build.property_graph import ManualBuildPropertyGraph
import os
news = os.listdir('./dataset/news/')
codes = [new.split('_')[0] for new in news]

from dataset.download.helper import read_record
codes = read_record()

builder = ManualBuildPropertyGraph()
def test_build_news():
    [builder.news_mention_company(code) for code in codes]
    
def test_build_company_rel():
    [builder.company_rel_company(code) for code in codes]

def test_remove_all():
    builder.remove_all()