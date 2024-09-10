import asyncio
from dataset.get_news import main
import traceback

async def run_script():
    try:
        # 假設 main() 是一個同步函數，我們使用 run_in_executor 來非阻塞地運行它
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, main)
        print("成功執行腳本")
    except Exception as e:
        print(f"執行腳本時發生錯誤: {e}")
        print("錯誤詳情:")
        print(traceback.format_exc())

async def schedule_script(interval_seconds):
    while True:
        await run_script()
        await asyncio.sleep(interval_seconds)

# 使用示例
if __name__ == "__main__":
    asyncio.run(schedule_script(5))  # 每5秒執行一次