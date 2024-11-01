# 1. 構建Docker鏡像:  
# docker build -t neo4j_for_stock .

# Dockerfile
FROM neo4j:community-bullseye

# 安裝APOC插件
ENV NEO4J_PLUGINS=["apoc"]

# 複製設定文件

# Failed to read config /var/lib/neo4j/conf/neo4j.conf: Unrecognized setting. No declared setting with name: server.bolt.address. 
# Cleanup the config or disable 'server.config.strict_validation.enabled' to continue.
# COPY neo4j.conf /conf/neo4j.conf

COPY /config/apoc.conf /conf/apoc.conf
COPY /config/neo4j.conf /conf/neo4j.conf

# 暴露端口
EXPOSE 7474 7687

# 下載 APOC 插件
RUN apt-get update && apt-get install -y wget && \
    wget -P /var/lib/neo4j/plugins https://github.com/neo4j/apoc/releases/download/5.2.0/apoc-5.2.0-core.jar && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 啟動命令
CMD ["neo4j"]

