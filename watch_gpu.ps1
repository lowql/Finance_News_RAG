# 设置监控间隔（以秒为单位）
$interval = 3

# 清理控制台函数
function Clear-Host-NoScrollback {
    $Host.UI.RawUI.CursorPosition = @{X=0; Y=0}
    $Host.UI.RawUI.WindowPosition = @{X=0; Y=0}
    $width = $Host.UI.RawUI.BufferSize.Width
    $height = $Host.UI.RawUI.WindowSize.Height
    $space = " " * $width
    for ($i = 0; $i -lt $height; $i++) {
        Write-Host $space
    }
    $Host.UI.RawUI.CursorPosition = @{X=0; Y=0}
}

# 循环监控
while ($true) {
    # 清理控制台，但保持在同一位置
    Clear-Host-NoScrollback


    # "temperature.memory"
    #  HBM memory temperature. in degrees C.

    # "power.management"
    # A flag that indicates whether power management is enabled. Either "Supported" or "[Not Supported]". Requires Inforom PWR object version 3.0 or higher or Kepler device.

    # "power.draw"
    # The last measured power draw for the entire board, in watts. On Ampere or newer devices, returns average power draw over 1 sec. On older devices, returns instantaneous power draw. Only available if power management is supported. This reading is accurate to within +/- 5 watts.

    # "power.draw.average"
    # The last measured average power draw for the entire board, in watts. Only available if power management is supported and Ampere (except GA100) or newer devices. This reading is accurate to within +/- 5 watts.

    # "power.draw.instant"
    # The last measured instant power draw for the entire board, in watts. Only available if power management is supported. This reading is accurate to within +/- 5 watts.
    # 执行 nvidia-smi 命令并获取功耗和内存信息
    $output = nvidia-smi --query-gpu=power.draw,power.draw.average,power.draw.instant,memory.total,memory.free,memory.used --format=csv,noheader,nounits

    # 处理并格式化输出
    $gpuInfo = $output -split ','
    $powerDraw = [math]::Round([float]$gpuInfo[0], 2)
    $powerAvg = $gpuInfo[1]
    $powerInst = $gpuInfo[2]
    $memoryTotal = [math]::Round([float]$gpuInfo[3] / 1024, 2)
    $memoryFree = [math]::Round([float]$gpuInfo[4] / 1024, 2)
    $memoryUsed = [math]::Round([float]$gpuInfo[5] / 1024, 2)
    

    # 打印格式化的输出
    Write-Host "GPU status"
    Write-Host "power_usage: ${powerDraw} W"
    Write-Host "power_avg: ${powerAvg} W"
    Write-Host "power_Inst: ${powerInst} W"
    Write-Host "total mem: ${memoryTotal} GB"
    Write-Host "used mem: ${memoryUsed} GB"
    Write-Host "free mem: ${memoryFree} GB"
    Write-Host ""

    # 等待指定的间隔
    Start-Sleep -Seconds $interval
}