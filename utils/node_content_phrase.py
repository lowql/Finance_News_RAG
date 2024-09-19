import re

import json
import ast

def parse_string_to_json(input_strings):
    # 將輸入字符串分割成列表
    string_list = input_strings.split('", "')
    
    # 去除首尾的多餘引號
    string_list = [s.strip('"') for s in string_list]
    
    for s in string_list:
        try:
            # 使用 ast.literal_eval 安全地解析字符串為字典
            d = ast.literal_eval(s)
            print(d)
            return d
        except:
            return {}
def triplet_info(origin_triplet_string):   
    triplet = extract_parentheses_content(origin_triplet_string)      
    dict_list = []  
    for item in triplet:
        dict_list.append(parse_string_to_json(item))
    # 創建一個包含所有字典的JSON對象
    json_obj = {
        "entity1_info": dict_list[0] if len(dict_list) > 0 else None,
        "relation_info": dict_list[1] if len(dict_list) > 1 else None,
        "entity2_info": dict_list[2] if len(dict_list) > 2 else None
    }
    
    # 將JSON對象轉換為格式化的JSON字符串
    json_string = json.dumps(json_obj, ensure_ascii=False, indent=2)
    
    return json_string


def extract_parentheses_content(input_string):
    # 正則表達式模式：匹配任何非空白字符，後跟括號內的任何內容
    pattern = r'\S+\s*\((.*?)\)'
    
    # 查找所有匹配
    matches = re.findall(pattern, input_string)
    
    # 返回所有匹配結果
    return matches

# 測試函數
if __name__ == "__main__":
    # 測試用例
    test_strings = """
    高密度倉儲物流 
    ({'headline': '《光電股》廣運2022年營收成長逾3成 今年前2個月也增溫', 'author': '時報資訊', 'name': '高密度倉儲物流', 'triplet_source_id': '894ed139-709b-43e5-9e0d-2e27fc33f638'}) 
    -> RELATED_TO 
    ({'headline': '《光電股》廣運2022年營收成長逾3成 今年前2個月也增溫', 'author': '時報資訊', 'triplet_source_id': '894ed139-709b-43e5-9e0d-2e27fc33f638'}) 
    -> 廣運（6125） 
    ({'headline': '廣運2022年營收成長逾3成 今年前2個月也增溫', 'author': '袁顥庭／台北報導', 'name': '廣運（6125）', 'triplet_source_id': 'ac8474a1-2468-486f-9b54-3cbde61c4cfd'})"""
    
    print(f"輸入: {test_strings}")
    print(triplet_info(origin_triplet_string=test_strings))