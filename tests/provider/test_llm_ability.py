

context = """ 
    日 期：2023年06月09日
    公司名稱：廣運 (6125)
    主 旨：廣運訂定除息基準日
    發言人：沈麗娟
    說 明：
    1.董事會、股東會決議或公司決定日期:112/03/10
    2.除權、息類別（請填入「除權」、「除息」或「除權息」）:除息
    3.發放股利種類及金額:
    盈餘分配現金股利：新台幣401,884,983元，每股配發現金股利1.62元。
    4.除權（息）交易日:112/07/06
    5.最後過戶日:112/07/07
    6.停止過戶起始日期:112/07/10
    7.停止過戶截止日期:112/07/14
    8.除權（息）基準日:112/07/14
    9.債券最後申請轉換日期:不適用
    10.債券停止轉換起始日期:不適用
    11.債券停止轉換截止日期:不適用
    12.現金股利發放日期:112/07/28 
"""

import pytest
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings

models = ['llama3.1:latest','jcai/llama3-taide-lx-8b-chat-alpha1:Q4_K_M ']

#轉換成以下形式
# 使用列表推导式和product函数创建所有可能的模型-问题对
from itertools import product
questions = [
    "台灣的總統是誰?",
    
    "公司名稱：廣運 (6125) \n 主 旨：廣運訂定除息基準日 \n 發言人：沈麗娟 \n 發言人是誰?",
    
    """設備大廠廣運（6125），今天旗下群豐欣業公司於高雄台糖成功物流園區舉行開幕典禮，藉此機會展現智慧物流系統發展。
    談及群豐公司成立緣起，廣運董事長謝清福表示，這是與合作伙伴台糖公司在歷經約一年時間，由廣運重新增修建置完成此一體式棧板式自動倉儲系統，此系統為33米高、11個高速走行存取主機（Crane）、儲位15000個、廣運自行開發智慧管理平台WMS（Warehouse Management System，倉庫管理系統）並結合ERP系統及無人搬運車AGV（Automated Guided Vehicle）等，除了作為廣運提供潛在客戶的「工程實績展示基地」，並進行實際運作驗證，也為客戶發展「持續優化設備軟硬體」，期許能替客戶創造更好的競爭優勢。
    廣運在智慧倉儲物流、常溫及低溫冷鏈設備耕耘已久，涵蓋客戶有全聯、中華郵政、中國石油、遠雄港、杏一、酷澎、宅配通、momo、Pchome、新竹物流、捷盟（康是美）及統昶等。廣運在智慧物流發貨系統建設方面，通常提供有自動倉儲、自動分揀、無人搬運車、輸送機、環形台車、龍門系統、自動拆棧機器人，電子標籤檢貨系統、自動開箱／貼標／秤重/封箱/捆膜等設備，並且搭配廣運自行開發智慧管理平台WMS進行整合，彈性調度自動化設備進行各種運作，並與客戶的MES及ERP進行垂直系統整合，滿足客戶多元化客製需求。
    廣運為客戶建置先進的物流中心，並提供售後服務，這是維繫客戶營運的兩隻腳。廣運力求做得更好，設身處地理解客戶需求並了解客戶的痛點，實際參與運作是最好的方法。因此和台糖公司合作，期許能提供客戶更佳的物流解決方案，讓智慧系統運作及高效營運操作成為客戶物流營運的基石。
    更多中時新聞網報導災後重建需求大 鋼廠迎榮景繳了一輩子勞保一場空？四種人退休也領不到錢SCFI、BDI運價齊飆 貨櫃散裝競速 陸航海王預警 「5大挑戰」 Q1獲利崩剩1／4\n\n 請條列出公司的利多消息""",
   
    """設備大廠廣運（6125），今天旗下群豐欣業公司於高雄台糖成功物流園區舉行開幕典禮，藉此機會展現智慧物流系統發展。
    談及群豐公司成立緣起，廣運董事長謝清福表示，這是與合作伙伴台糖公司在歷經約一年時間，由廣運重新增修建置完成此一體式棧板式自動倉儲系統，此系統為33米高、11個高速走行存取主機（Crane）、儲位15000個、廣運自行開發智慧管理平台WMS（Warehouse Management System，倉庫管理系統）並結合ERP系統及無人搬運車AGV（Automated Guided Vehicle）等，除了作為廣運提供潛在客戶的「工程實績展示基地」，並進行實際運作驗證，也為客戶發展「持續優化設備軟硬體」，期許能替客戶創造更好的競爭優勢。
    廣運在智慧倉儲物流、常溫及低溫冷鏈設備耕耘已久，涵蓋客戶有全聯、中華郵政、中國石油、遠雄港、杏一、酷澎、宅配通、momo、Pchome、新竹物流、捷盟（康是美）及統昶等。廣運在智慧物流發貨系統建設方面，通常提供有自動倉儲、自動分揀、無人搬運車、輸送機、環形台車、龍門系統、自動拆棧機器人，電子標籤檢貨系統、自動開箱／貼標／秤重/封箱/捆膜等設備，並且搭配廣運自行開發智慧管理平台WMS進行整合，彈性調度自動化設備進行各種運作，並與客戶的MES及ERP進行垂直系統整合，滿足客戶多元化客製需求。
    廣運為客戶建置先進的物流中心，並提供售後服務，這是維繫客戶營運的兩隻腳。廣運力求做得更好，設身處地理解客戶需求並了解客戶的痛點，實際參與運作是最好的方法。因此和台糖公司合作，期許能提供客戶更佳的物流解決方案，讓智慧系統運作及高效營運操作成為客戶物流營運的基石。
    更多中時新聞網報導災後重建需求大 鋼廠迎榮景繳了一輩子勞保一場空？四種人退休也領不到錢SCFI、BDI運價齊飆 貨櫃散裝競速 陸航海王預警 「5大挑戰」 Q1獲利崩剩1／4\n\n 簡要說明各公司持有的技術，並標註持有技術的公司([公司名稱]::(持有技術))""",
    
    """
    任務：生成查詢圖形資料庫的 Cypher 語句。
    指示：
    僅使用架構中提供的關係類型和屬性。
    不要使用任何未提供的其他關係類型或屬性。
    架構：
    ("公司", "旗下公司", "子公司"),
    ("公司", "合作關係", "公司"),
    注意：在您的回應中不要包含任何解釋或道歉。
    不要回應任何可能詢問其他問題的問題，除了要求您構建 Cypher 語句。
    除了生成的 Cypher 語句外，不要包含任何文本。

    \n\n設備大廠廣運（6125），今天旗下群豐欣業公司於高雄台糖成功物流園區舉行開幕典禮，藉此機會展現智慧物流系統發展。
    談及群豐公司成立緣起，廣運董事長謝清福表示，這是與合作伙伴台糖公司在歷經約一年時間，由廣運重新增修建置完成此一體式棧板式自動倉儲系統，此系統為33米高、11個高速走行存取主機（Crane）、儲位15000個、廣運自行開發智慧管理平台WMS（Warehouse Management System，倉庫管理系統）並結合ERP系統及無人搬運車AGV（Automated Guided Vehicle）等，除了作為廣運提供潛在客戶的「工程實績展示基地」，並進行實際運作驗證，也為客戶發展「持續優化設備軟硬體」，期許能替客戶創造更好的競爭優勢。
    廣運在智慧倉儲物流、常溫及低溫冷鏈設備耕耘已久，涵蓋客戶有全聯、中華郵政、中國石油、遠雄港、杏一、酷澎、宅配通、momo、Pchome、新竹物流、捷盟（康是美）及統昶等。廣運在智慧物流發貨系統建設方面，通常提供有自動倉儲、自動分揀、無人搬運車、輸送機、環形台車、龍門系統、自動拆棧機器人，電子標籤檢貨系統、自動開箱／貼標／秤重/封箱/捆膜等設備，並且搭配廣運自行開發智慧管理平台WMS進行整合，彈性調度自動化設備進行各種運作，並與客戶的MES及ERP進行垂直系統整合，滿足客戶多元化客製需求。
    廣運為客戶建置先進的物流中心，並提供售後服務，這是維繫客戶營運的兩隻腳。廣運力求做得更好，設身處地理解客戶需求並了解客戶的痛點，實際參與運作是最好的方法。因此和台糖公司合作，期許能提供客戶更佳的物流解決方案，讓智慧系統運作及高效營運操作成為客戶物流營運的基石。
    更多中時新聞網報導災後重建需求大 鋼廠迎榮景繳了一輩子勞保一場空？四種人退休也領不到錢SCFI、BDI運價齊飆 貨櫃散裝競速 陸航海王預警 「5大挑戰」 Q1獲利崩剩1／4\n\n 簡要說明公司間的合作關係，使用cypher語法表述""",
    
    context + "\n請保持上下文關係不變的狀態下，以JSON表示\n",
    
    
]
model = models[1]
llm = Ollama(model=model, request_timeout=60.0)
@pytest.mark.parametrize("query_txt", questions)
def test_IQ_speend(query_txt):
    print(query_txt)
    print("=============================================================")
    print("use model is",model)
    print("=============================================================")
    completions = llm.stream_complete(query_txt)
    for completion in completions:
        print(completion.delta, end="")
    print("\n=============================================================\n")
    
questions = [
    "發言人是?", 
    "文章的主旨是?",
    "發放股利種類及金額?",
    "最後過戶日",
    "除權（息）交易日"
    
]
model_question_pairs = [(query_text, model) for query_text, model in product(questions, models)]
@pytest.mark.parametrize("query_txt,model", model_question_pairs)
def test_announcement_news(query_txt,model):
    llm = Ollama(model=model, request_timeout=60.0)
    from llama_index.core import PromptTemplate

    template = (
        "你現在是專業的財金播報員，請確保你的專業性，回答請根據以下提供的資訊內容\n"
        "過程中保持客觀"
        "\n---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "請跟據上下文回答問題: {query_str}\n"
        "回覆時，請不要有冗言贅字"
    )
    qa_template = PromptTemplate(template)

    # you can create text prompt (for completion API)
    prompt = qa_template.format(context_str=context, query_str=query_txt)
    print(prompt)
    print("=============================================================")
    print("use model is",model)
    print("=============================================================")
    completions = llm.stream_complete(prompt)
    for completion in completions:
        print(completion.delta, end="")
    print("\n=============================================================\n")
    