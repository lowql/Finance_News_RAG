import requests
import pandas as pd
from datetime import datetime, timedelta,date
from utils.path_manager import get_download_news_file
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

    try:
        print(f"使用現有的檔案: {csv_file}")
        all_data = pd.read_csv(csv_file, index_col=0)
        if all_data.empty:
            raise Exception("(首次爬取)CSV_File沒有過往寫入的資料") 
        print("成功讀取 CSV 文件。")
        format_string = "%Y-%m-%d %H:%M:%S"
        last_time = all_data.iloc[[-1]]['date'].values[0]
        current_date = datetime.strptime(last_time,format_string)
        current_date += timedelta(days=1)
    except pd.errors.EmptyDataError:
        print("錯誤: CSV 文件是空的或沒有可解析的列。")
        all_data = pd.DataFrame()  # 創建一個空的 DataFrame
    except Exception as e:
        print(f"發生未預期的錯誤：{str(e)}") #發生未預期的錯誤：positional indexers are out-of-bounds
        all_data = pd.DataFrame()  # 創建一個空的 DataFrame    
    
    return all_data,current_date,end_date

def fetch_news_day_by_day(dataset, data_id, start_date, end_date, token):
    
    all_data,current_date,end_date = current_end_date(start_date,end_date)
    print(f"current date is : {current_date}\nend date is : {end_date}")

    while current_date <= end_date:
        # 格式化日期為字串
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"\r{date_str}",end="",flush=True)

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
            print(f"\nError: {response.status_code} for date: {date_str}")
            print(response.text)
            all_data.to_csv(csv_file)
            print("當前資料已儲存")
            return False
        
        # 更新下一個日期
        current_date += timedelta(days=1)

    all_data.to_csv(csv_file)
    return True

def main():
    global csv_file 

    # 設定參數
    dataset = "TaiwanStockNews"
    start_date = "2023-01-01"
    end_date = date.today().strftime("%Y-%m-%d")  # Get current date
    print(f"start date is : {start_date} \ end date is : {end_date}")
    
    """ FinMind password 
    1. FINAPI@project#1
    ! gemail.yuntech 無法使用 :(, 註冊信箱只能使用 gmail, yahoo .... 
    """
    from dotenv import load_dotenv
    import os

    load_dotenv(dotenv_path='.env')
    finmind_token = os.getenv("finmind_token")
    token = [finmind_token]
    
    
    # 確保目錄存在
    os.makedirs('./dataset/download', exist_ok=True)

    # 檔案路徑
    record_file_path = './dataset/download/record.txt'

    # 確保文件存在，如果不存在則創建
    if not os.path.exists(record_file_path):
        open(record_file_path, 'x').close()

    # 獲取資料
    from dataset.download.helper import need_to_download_company
    unique_codes = need_to_download_company()
    print(f"本次下載企業 {unique_codes}")
    for code in unique_codes:
        code = str(code)
        csv_file= Path(get_download_news_file(code))    
        print("csv file path is : ",csv_file)
        
        try:
            df = pd.read_csv(csv_file)
            start_date = df.loc[:,'date'].tolist()[-1]
            print(f"上次最後下載日期:  {start_date} ~ {end_date}")
        except: 
            print(f"本次為全新下載: {start_date} ~ {end_date}")
        status = fetch_news_day_by_day(dataset, code, start_date, end_date, token[0])
        if status == False:
             return False
        if status == True:
            print("成功下載")
            with open('./dataset/download/record.txt','a',encoding='utf8') as record:
                record.write(f"{code},")
           
    return True

if __name__ == "__main__":
    main()
