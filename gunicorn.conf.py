# 是否開啟除錯模式，當程式碼有變動，會自動重啟
debug = True
# 訪問地址
bind = "0.0.0.0:5000"
# 工作進程數
workers = 2
# 工作線程數
threads = 2
# 超時時間
timeout = 600
# 輸出日誌級別
loglevel = 'debug'
# 存放日誌路徑
pidfile = "log/gunicorn.pid"
# 存放訪問日誌路徑
accesslog = "log/access.log"
# 存放錯誤日誌路徑
errorlog = "log/debug.log"
# gunicorn + apscheduler 場景下，解決多 worker 運行定時任務重複執行的問題
preload_app = True
