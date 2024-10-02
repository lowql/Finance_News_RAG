import schedule
import time
from datetime import datetime, timedelta
from dataset.get_news import fetch_FinMind
def run_script():
    try:
        fetch_FinMind()
        print("成功執行腳本")
    except Exception as e:
        print(f"執行腳本時發生錯誤: {e}")

def schedule_script(interval_minutes):
    schedule.every(interval_minutes).minutes.do(run_script)
    print(f"已安排每 {interval_minutes} 分鐘執行一次腳本")

def display_countdown(interval_minutes):
    next_run = datetime.now() + timedelta(minutes=interval_minutes)
    while datetime.now() < next_run:
        remaining = next_run - datetime.now()
        minutes, seconds = divmod(remaining.seconds, 60)
        print(f"\r下次執行倒計時: {minutes:02d}:{seconds:02d}", end="", flush=True)
        time.sleep(1)
    print("\r執行腳本中...                ", end="", flush=True)

if __name__ == "__main__":

    interval = 60  # 設置間隔時間（分鐘）
    schedule_script(interval)
    while fetch_FinMind() == False:
        print("API 使用額度已達上限休息1HR")
        display_countdown(interval)
        schedule.run_pending()
        time.sleep(1)