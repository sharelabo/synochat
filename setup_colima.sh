#!/bin/bash

# Homebrewがインストールされているか確認
if ! command -v brew &> /dev/null; then
    echo "Homebrewをインストールします..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# colimaをインストール
echo "colimaをインストールします..."
brew install colima

# colimaを起動
echo "colimaを起動します..."
colima start

# Docker Composeをインストール
echo "Docker Composeをインストールします..."
brew install docker-compose

# Python仮想環境を作成
echo "Python仮想環境を作成します..."
python3 -m venv venv
source venv/bin/activate

# 必要なPythonパッケージをインストール
echo "Pythonパッケージをインストールします..."
pip install -r requirements.txt

echo "セットアップが完了しました。"
echo "以下のコマンドを実行してアプリケーションを起動してください："
echo "docker-compose up -d"