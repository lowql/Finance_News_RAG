import requests
import pandas as pd
from datetime import datetime, timedelta
import argparse
from utils.path_manager import get_history_news_file
from pathlib import Path
# [ ]: 取得公司過去新聞 
""" 
觀察下來
因為台灣的新聞幾乎都是互相抄來抄去
所以只需要 Yahoo News 就幾乎可以覆蓋所有新聞消息
""" 

def current_end_date(start_date,end_date):
# 將初始日期和結束日期轉換為 datetime 對象
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    csv_file = Path(get_history_news_file(code=6125))
    
    if csv_file.exists():
        all_data = pd.read_csv(csv_file,index_col=0)
        
        # TypeError: strptime() argument 1 must be str, not Series -> .value[0]
        last_time = all_data.iloc[[-1]]['date'].values[0]

        format_string = "%Y-%m-%d %H:%M:%S"
        current_date = datetime.strptime(last_time,format_string)
        current_date += timedelta(days=1)
    else:
        all_data = pd.DataFrame()
    
    
    return current_date,end_date

def fetch_data_day_by_day(dataset, data_id, start_date, end_date, token):
    
    current_date,end_date = current_end_date(start_date,end_date)
    print(f"current date is : {current_date}\nend date is : {end_date}")

    # [ ]: API TOKEN 的限制導致無法一次下載指定區間的資料
    # 1. 需要可以延續之前下載完成的 {code}_history_news 添加後續區間段的資料
    while current_date <= end_date:
        # 格式化日期為字串
        date_str = current_date.strftime("%Y-%m-%d")
        print(date_str)
        # 定義 API URL 和請求參數
        url = "https://api.finmindtrade.com/api/v4/data"
        params = {
            "dataset": dataset,
            "data_id": data_id,
            "start_date": date_str,
            "token": token
        }
        response = requests.get(url, params=params)
        
        # 檢查請求是否成功
        if response.status_code == 200:
            data = response.json()
            # 檢查資料是否存在
            if 'data' in data:
                day_data = pd.DataFrame(data['data'])
                all_data = pd.concat([all_data, day_data], ignore_index=True)
            else:
                print(f"No data found for date: {date_str}")
        else:
            print(f"Error: {response.status_code} for date: {date_str}")
            print(response.text)
        
        # # 更新下一個日期
        current_date += timedelta(days=1)

    return all_data

def main():
    # 設定 argparse 來接收命令行參數
    parser = argparse.ArgumentParser(description='Fetch data from FinMind API')
    parser.add_argument('data_id', type=str, help='The data_id to fetch data for')
    args = parser.parse_args()

    # 設定參數
    dataset = "TaiwanStockNews"
    start_date = "2023-01-01"
    end_date = "2024-01-01"  # 替換為所需的結束日期
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAyNC0wNy0wMyAxNToxMTo0NCIsInVzZXJfaWQiOiJ2ZW1pICIsImlwIjoiMS4yMDAuMTEzLjIwMSJ9.YFuB8XlDRdht0dVWEFDnTEY7vaJUV69alb4Mi5e4gUg"
    
    # 獲取資料
    data = fetch_data_day_by_day(dataset, args.data_id, start_date, end_date, token)
    print(data)

if __name__ == "__main__":
    main()
