# Synology Chat Webhook Server

このプロジェクトは、Synology Chatからのウェブフックを受信し、メッセージをJSONファイルに保存するサーバーアプリケーションです。Docker対応しており、Synology NAS上でも簡単に実行できます。

## 特徴

- Synology ChatのWebhookからメッセージを受信します
- 受信したメッセージをJSONファイルに保存します
- Docker対応で、Synology NASを含むさまざまな環境で実行可能です
- マイクロサービスアーキテクチャに準拠し、メッセージの受信と処理を分離しています

## 必要条件

- Python 3.x
- Flask
- python-dotenv
- Docker（Dockerで実行する場合）

## セットアップ

### 通常のセットアップ（Dockerなし）

1. **リポジトリをクローン**:

   ```sh
   git clone https://github.com/sharelabo/synochat.git
   cd synochat
   ```

2. **仮想環境を作成し、依存関係をインストール**:

   ```sh
   python -m venv myenv
   source myenv/bin/activate  # Windowsの場合は `myenv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の環境変数を追加**:

   ```plaintext
   SYNOLOGY_CHAT_TOKEN=your_synology_chat_token
   MESSAGES_FILE=data/received_messages.json  # オプション
   PORT=5001  # オプション
   ```

### Dockerを使用したセットアップ

1. **Dockerイメージのビルド**:

   ```sh
   docker build -t synology-chat-webhook .
   ```

2. **Dockerコンテナーの実行**:

   ```sh
   docker run -d -p 5001:5001 -v $(pwd)/data:/app/data --name synology-chat-webhook synology-chat-webhook
   ```

### Docker Composeを使用したセットアップ（推奨）

1. **Docker Composeでサービスを起動**:

   ```sh
   docker-compose up -d
   ```

## アプリケーションの実行

### 通常の実行方法

```sh
python synology_chat.py
```

これにより、Webhookサーバーが起動し、ポート5001でWebhookリクエストを待ち受けます。

### Synology NASでの設定

1. **Synology NASのDocker GUIを使用**:
   - Docker Composeをインストールするか、「イメージ」タブからDockerfileをアップロードしてビルドします
   - 適切なポート転送（5001:5001）とボリュームマッピング（./data:/app/data）を設定します

2. **Synology Chatの設定**:
   - Synology Chatの「インテグレーション」設定でWebhookを追加します
   - URL: `http://[NASのIPアドレス]:5001/webhook`（NAS上で実行している場合は`http://localhost:5001/webhook`）
   - トークン: `.env`ファイルで設定したものと同じトークン

## 仕組み

1. アプリケーションは、設定されたポート（デフォルトは5001）でWebhookリクエストを待ち受けます
2. Synology Chatからメッセージが送信されると、Webhookリクエストとして受信します
3. トークンを検証し、有効な場合はメッセージをJSONファイルに保存します
4. JSONファイルは後で他のアプリケーションで処理できます

## トラブルシューティング

- `.env` ファイルが正しく設定され、適切なトークンが含まれていることを確認してください
- Dockerを使用している場合、ボリュームが正しくマウントされていることを確認してください
- ファイアウォールがポート5001を許可していることを確認してください
- Synology Chatの設定で、正しいWebhook URLとトークンが設定されていることを確認してください

## マイクロサービスアーキテクチャ

このアプリケーションは、メッセージの受信と処理を分離したマイクロサービスアーキテクチャに基づいています。

- **Webhookサーバー（このアプリケーション）**: メッセージを受信し、JSONファイルに保存します
- **メッセージ処理サービス（別途実装）**: JSONファイルからメッセージを読み取り、処理します

これにより、各コンポーネントを独立して拡張・保守することが可能になります。