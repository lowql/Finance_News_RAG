# start-neo4j.sh
#!/bin/bash

CONTAINER_NAME="neo4j-apoc"

# 檢查容器是否存在
if [ "$(docker ps -aq -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "Container ${CONTAINER_NAME} already exists."
    
    # 檢查容器是否正在運行
    if [ "$(docker ps -q -f name=^/${CONTAINER_NAME}$)" ]; then
        echo "Stopping running container..."
        docker stop ${CONTAINER_NAME}
    fi
    
    echo "Removing existing container..."
    docker rm ${CONTAINER_NAME}
fi

source .env

echo "Starting new container..."

# docker-compose up