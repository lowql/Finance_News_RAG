from storages.build.property_graph import AutoBuildPropertyGraph
auto_builder = AutoBuildPropertyGraph()
def test_dynamicPathExtractor():
    auto_builder.build_News_KG_use_dynamicPathExtractor(2421)
    auto_builder.client.close()