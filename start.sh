#!/bin/bash

# colimaが起動していない場合は起動
if ! colima status &> /dev/null; then
    echo "colimaを起動します..."
    colima start
fi

# Docker Composeでアプリケーションを起動
echo "アプリケーションを起動します..."
docker-compose up -d

# ログを表示
echo "アプリケーションのログを表示します..."
docker-compose logs -f