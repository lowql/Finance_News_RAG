## python 環境安裝
poetry install
poetry shell
pip install llama-index-graph-stores-neo4j llama-index-vector-stores-neo4jvector llama-index-llms-ollama

## Build 建構新聞知識圖譜

python -m storages.build.main                   

---

## pytest 常用參數

1. general:: 
   1. -s (Shortcut for --capture=no)

2. reporting:: 
   1. -v, --verbose (Increase verbosity)

```shell
python -m pytest -sv
```

## Windows Host 如何訪問 WSL (正在嘗試中)

不適用 :: 啟用鏡像模式網路 : C:\Users\<YourUserName>\.wslconfig
```shell
[wsl2]
networkingMode=mirrored
```

```shell
PS C:\Users\vemi> wsl
wsl: 不支援 Hyper-V 防火牆
wsl: 不支援鏡像網路模式： Windows 版本 22621.2283 沒有所需的功能。
回到 NAT 網路。
wsl: 不支援 DNS 通道
```


1. 取得 IP addrs

> WSL內部Linux環境的IP地址
```shell
wsl hostname -I
#172.19.72.204
```

> Windows主機上為WSL創建的虛擬網卡的IP地址。它充當WSL和外部網絡之間的橋樑
```shell
$ ipconfig 
....
乙太網路卡 vEthernet (WSL):
   連線特定 DNS 尾碼 . . . . . . . . : 
   連結-本機 IPv6 位址 . . . . . . . : fe80::b11c:a5b6:c0c7:d959%74
   IPv4 位址 . . . . . . . . . . . . : 172.19.64.1
   子網路遮罩 . . . . . . . . . . . .: 255.255.240.0
   預設閘道 . . . . . . . . . . . . .:
```

2. 設置端口轉發規則
```
netsh interface portproxy add v4tov4 listenport=7474 listenaddress=0.0.0.0 connectport=7474 connectaddress=172.19.72.204
netsh interface portproxy add v4tov4 listenport=11434 listenaddress=0.0.0.0 connectport=11434 connectaddress=172.19.72.204
netsh interface portproxy add v4tov4 listenport=7687 listenaddress=0.0.0.0 connectport=7687 connectaddress=172.19.72.204
```
如何檢查?
```shell
netsh interface portproxy show all
```
3. 設置防火牆規則
```
New-NetFirewallRule -DisplayName "WSL Docker 7474" -Direction Inbound -LocalPort 7474 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "WSL Docker 11434" -Direction Inbound -LocalPort 11434 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "WSL Docker 7687" -Direction Inbound -LocalPort 7687 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Allow WSL" -Direction Inbound -InterfaceAlias "vEthernet (WSL)" -Action Allow
```
如何檢查?
```shell
Get-NetFirewallRule | Where-Object { $_.DisplayName -eq "WSL Docker 8080" } | Format-List -Property DisplayName, Enabled, Direction, Action, Protocol, LocalPort
```

1. 重新啟動 WSL
```shell
wsl --shutdown
```
1. 測試連接
```python
curl http://localhost:11434
```