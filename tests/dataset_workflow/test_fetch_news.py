
def test_fetch_from_FinMind():
    from dataset.timer import schedule_script,display_countdown,fetch_FinMind
    import schedule
    interval = 60  # 設置間隔時間（分鐘）
    schedule_script(interval)
    while fetch_FinMind() == False:
        print("API 使用額度已達上限休息1HR")
        display_countdown(interval)
        schedule.run_pending()

def test_record():
    from dataset.download.helper import update_record
    update_record()
    
def test_news_filter():
    from dataset.download.helper import read_record
    import pandas as pd
    from utils.path_manager import get_download_news_file,get_filter_news_file
    from dataset.news_filter import news_filter
    codes = read_record()
    
    for code in codes:
        csv_file = get_download_news_file(code)
        print(f"filter process {csv_file}")
        try:
            df = pd.read_csv(csv_file,index_col=0)
        except:
            print("Can't read csv_file")
            continue
        df = news_filter(df)
        output_file = get_filter_news_file(code)
        df.to_csv(output_file, index=False)
        print(f"處理完成，結果已保存到 {output_file}")
        print()

def test_fetch_yahoo_content():
    from dataset.news_crawler.fetch_yahoo import fetch_from_filter
    fetch_from_filter()
    pass