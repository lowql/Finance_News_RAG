#!/bin/bash

# 设置Docker Compose文件路径
COMPOSE_FILE="docker-compose.yml"
# just check flag file
ENV_CHECK_FILE=".env_check_done"

# 检查Docker Compose文件是否存在
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "错误: Docker Compose文件 '$COMPOSE_FILE' 不存在。"
    exit 1
fi

# 检查并配置环境
check_and_configure_environment() {
    if [ -f "$ENV_CHECK_FILE" ]; then
        echo "环境已经配置过，跳过配置步骤。"
        return
    fi

    echo "正在检查和配置环境..."

    # 检查是否已安装NVIDIA Container Toolkit
    if ! command -v nvidia-container-toolkit &> /dev/null; then
        echo "正在安装NVIDIA Container Toolkit..."
        
        # 安装NVIDIA Container Toolkit
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
        curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        sudo apt-get update
        sudo apt-get install -y nvidia-container-toolkit

        # 配置Docker使用NVIDIA Container Toolkit
        sudo nvidia-ctk runtime configure --runtime=docker
        sudo systemctl restart docker

        echo "NVIDIA Container Toolkit 已安装和配置。"
    else
        echo "NVIDIA Container Toolkit 已安装，跳过安装步骤。"
    fi

    # 创建检查文件以标记环境已配置
    touch "$ENV_CHECK_FILE"
    # 更新环境检查文件
    echo "Version: 1.0" > "$ENV_CHECK_FILE"
    echo "Last configured: $(date)" >> "$ENV_CHECK_FILE"
    echo "NVIDIA Driver Version: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)" >> "$ENV_CHECK_FILE"
    echo "环境检查和配置完成。"
}


# 检查Docker Compose文件是否存在
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "错误: Docker Compose文件 '$COMPOSE_FILE' 不存在。"
    exit 1
fi

# 启动服务
start_services() {
    echo "正在启动服务..."
    docker-compose -f $COMPOSE_FILE up -d
    echo "Pull yi model"
    docker exec -it ollama-api ollama pull yi
    echo "服务已启动。"
}

# 停止服务
stop_services() {
    echo "正在停止服务..."
    docker-compose -f $COMPOSE_FILE down
    echo "服务已停止。"
}

# 重启服务
restart_services() {
    echo "正在重启服务..."
    docker-compose -f $COMPOSE_FILE down
    start_services
    echo "服务已重启。"
}

# 检查服务状态
check_status() {
    echo "检查服务状态..."
    docker-compose -f $COMPOSE_FILE ps

    echo "check docker version"
    echo -e "\n version information:"
    docker exec neo4j-api neo4j --version
    echo -e "\n Detailed version information:"
    docker exec neo4j-api neo4j version

    
}

# 显示日志
show_logs() {
    echo "显示服务日志..."
    docker-compose -f $COMPOSE_FILE logs
}

# 主菜单
show_menu() {
    echo "===== Docker Compose 服务管理 ====="
    echo "1. 启动服务"
    echo "2. 停止服务"
    echo "3. 重启服务"
    echo "4. 检查服务状态"
    echo "5. 显示服务日志"
    echo "6. 退出"
    echo "请输入选项 (1-6): "
}

# 主循环
while true; do
    show_menu
    read -r opt
    check_and_configure_environment
    case $opt in
        1) start_services ;;
        2) stop_services ;;
        3) restart_services ;;
        4) check_status ;;
        5) show_logs ;;
        6) echo "退出脚本。"; exit 0 ;;
        *) echo "无效选项，请重试。" ;;
    esac
    echo
done