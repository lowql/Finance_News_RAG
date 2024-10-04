## python 環境安裝
poetry install
poetry add pytest times 
poetry shell
pip install ollama llama-index-program-lmformatenforcer
pip install lm-format-enforcer
pip install llama-index-graph-stores-neo4j 
pip install llama-index-vector-stores-neo4jvector 
pip install llama-index-llms-ollama
pip install matplotlib

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

from windows host
```shell
wsl hostname -I
#<wsl_ip>172.19.72.204
```

from wsl 
```shell
ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1
```

> (單純補充::之後的操作不會使用)
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
netsh interface portproxy add v4tov4 listenport=7474 listenaddress=0.0.0.0 connectport=7474 connectaddress=<wsl_ip>
netsh interface portproxy add v4tov4 listenport=11434 listenaddress=0.0.0.0 connectport=11434 connectaddress=<wsl_ip>
netsh interface portproxy add v4tov4 listenport=7687 listenaddress=0.0.0.0 connectport=7687 connectaddress=<wsl_ip>
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

2. 檢查 WSL 網路設置
```
wsl hostname -I
```

3. 測試連接
```python
curl http://localhost:11434
```


---

## Docker

### 啟用服務
```shell
docker-compose up
```

### 停用服務
```shell
docker-compose down
```
### 檢查網路配置效果 (之前有坑)
```shell
docker ps
```
## TroubleShoot 
```sh
PS C:\Users\vemi> ollama list
Error: Head "http://127.0.0.1:11434/": read tcp 127.0.0.1:52220->127.0.0.1:11434: wsarecv: An existing connection was forcibly closed by the remote host.
```

1. 首先檢查 PORT 的占用
netstat -ano | findstr :11434
netstat -ano | Select-String "LISTENING"
2. 確認占用 PORT 的程序
Get-Process -Id <_id>
1. 結束占用 PORT 的進程
Stop-Process -Id <_id> -Force
1. 再次檢查 PORT 的狀態
netstat -ano | findstr :11434

```powershell
tasklist /svc | findstr svchost.exe
```

```powershell
Get-WmiObject -Class Win32_Process | Select-Object Name, ProcessId, @{Name='ExecutablePath';Expression={$_.ExecutablePath}} | Sort-Object Name
```

other
1. 查找具體服務
tasklist /svc /FI "PID eq 1056"
1. 檢查服務詳情
`Get-Service -Name "服务名称"`
1. 重啟服務 
`Restart-Service -Name "服务名称"`
1. 檢查服務配置 
Get-WmiObject win32_service | Where-Object {$_.ProcessId -eq <_id>}
1. 停止服務
`Stop-Service -Name "服务名称"`
1. 驗證服務狀態

警告：

在永久停止任何服务之前，请确保您完全理解该服务的作用及停止它可能带来的影响。
某些系统服务是 Windows 正常运行所必需的。
停止这些服务可能会导致系统不稳定或功能丧失。

如果您不确定，最好先将服务设置为手动启动，而不是完全禁用它：
```powershell
Set-Service -Name "服务名称" -StartupType Manual
```

如果在停止服务后遇到任何系统问题，您可以通过将启动类型改回"Automatic"并启动服务来恢复：
```powershell
Set-Service -Name "服务名称" -StartupType Automatic
Start-Service -Name "服务名称"
```