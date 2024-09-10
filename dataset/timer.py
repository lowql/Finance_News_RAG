""" Package operations: 1 install, 2 updates, 0 removals

  - Downgrading nltk (3.9.1 -> 3.8.1)
  - Downgrading llama-index-core (0.11.3 -> 0.10.56)
  - Installing schedule (1.2.2) 
"""
import schedule
import time
import subprocess
from datetime import datetime, timedelta
from dataset.get_news import main
def run_script():
    try:
        main()
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

    while True:
        display_countdown(interval)
        schedule.run_pending()
        time.sleep(1)