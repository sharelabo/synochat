#!/bin/bash

# WSL2環境でのDocker Desktop統合の確認
if ! command -v docker &> /dev/null; then
    echo "Dockerが見つかりません。"
    echo "Windows側でDocker Desktopをインストールし、WSL統合を有効にしてください。"
    echo ""
    echo "手順:"
    echo "1. Windows側でDocker Desktopをインストール: https://www.docker.com/products/docker-desktop/"
    echo "2. Docker Desktopを起動"
    echo "3. Docker Desktopの設定を開く (Settings)"
    echo "4. 「Resources」→「WSL Integration」を選択"
    echo "5. 現在のWSLディストリビューション（Ubuntu）を有効にする"
    echo "6. 「Apply & Restart」をクリック"
    echo "7. WSLを再起動: PowerShellで「wsl --shutdown」を実行後、WSLを再度開く"
    echo ""
    echo "設定完了後、このスクリプトを再度実行してください。"
    exit 1
fi

echo "Docker Desktop WSL統合が有効になっています。"

# Dockerが正しく動作するか確認
if ! docker ps &> /dev/null; then
    echo "Docker Desktop が起動していないか、権限が不足しています。"
    echo "以下を確認してください："
    echo "1. Windows側でDocker Desktopが起動しているか"
    echo "2. WSL統合が有効になっているか"
    echo "3. 必要に応じてWSLを再起動（PowerShellで「wsl --shutdown」を実行）"
    exit 1
fi

echo "Dockerの動作を確認しました。"

# Python仮想環境を作成
echo "Python仮想環境を作成します..."
python3 -m venv venv
source venv/bin/activate

# 必要なPythonパッケージをインストール
echo "Pythonパッケージをインストールします..."
pip install -r requirements.txt

echo "セットアップが完了しました。"
echo "以下のコマンドを実行してアプリケーションを起動してください："
echo "./start_linux.sh"