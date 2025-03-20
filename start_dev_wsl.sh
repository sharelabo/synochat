#!/bin/bash

# Dockerが利用可能か確認
if ! command -v docker &> /dev/null; then
    echo "Dockerが見つかりません。"
    echo "セットアップスクリプトを実行してください："
    echo "./setup_linux.sh"
    exit 1
fi

# Docker Desktopが起動しているか確認
if ! docker ps &> /dev/null; then
    echo "Docker Desktopが起動していないようです。"
    echo "以下を確認してください："
    echo "1. Windows側でDocker Desktopが起動しているか"
    echo "2. WSL統合が有効になっているか"
    echo "3. 必要に応じてWSLを再起動（PowerShellで「wsl --shutdown」を実行）"
    exit 1
fi

# Docker Composeでアプリケーションを起動
echo "アプリケーションを起動します..."
docker compose up -d

# ログを表示
echo "アプリケーションのログを表示します..."
docker compose logs -f