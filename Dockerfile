FROM python:3.9-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコピー
COPY synology_chat.py .
COPY .env .

# データ保存用のボリュームを設定
VOLUME /app/data

# ポート設定
EXPOSE 5001

# 環境変数
ENV MESSAGES_FILE=/app/data/received_messages.json

# サーバーの起動
CMD ["python", "synology_chat.py"]