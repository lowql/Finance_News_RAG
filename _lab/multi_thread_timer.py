import threading
import time
from dataset.get_news import main
import traceback

def run_script():
    try:
        main()
        print("成功執行腳本")
    except Exception as e:
        print(f"執行腳本時發生錯誤: {e}")
        print("錯誤詳情:")
        print(traceback.format_exc())

def schedule_script(interval_seconds):
    while True:
        thread = threading.Thread(target=run_script)
        thread.start()
        time.sleep(interval_seconds)

# 使用示例
if __name__ == "__main__":
    schedule_thread = threading.Thread(target=schedule_script, args=(5,))  # 每5秒執行一次
    schedule_thread.start()
    
    try:
        while True:
            time.sleep(1)  # 保持主線程運行
    except KeyboardInterrupt:
        print("程序被用戶中斷")