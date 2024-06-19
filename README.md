# Synology Chat Webhook Logger

このプロジェクトは、Synology Chatからのウェブフックを受信し、メッセージを処理し、特定のタグが含まれている場合に情報を特定のExcelファイルに記録するFlaskアプリケーションです。

## 特徴

- Synology ChatからのPOSTリクエストをリッスンします。
- 事前に定義されたトークンを使用してリクエストを認証します。
- ウェブフックデータからタイムスタンプ、ユーザー名、メッセージ内容を抽出します。
- メッセージ内容に指定されたタグが含まれている場合、その情報を異なるExcelファイルに記録します。

## 必要条件

- Python 3.x
- Flask
- pandas
- openpyxl
- python-dotenv
- synochat

## セットアップ

1. **リポジトリをクローン**:

   ```sh
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. **仮想環境を作成し、依存関係をインストール**:

   ```sh
   python3 -m venv myenv
   source myenv/bin/activate  # Windowsの場合は `myenv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の環境変数を追加**:

   ```plaintext
   SYNOLOGY_CHAT_TOKEN=your_synology_chat_token
   TAG_1=your_tag_1
   EXCEL_1=your_excel_1.xlsx
   TAG_2=your_tag_2
   EXCEL_2=your_excel_2.xlsx
   TAG_3=your_tag_3
   EXCEL_3=your_excel_3.xlsx
   TAG_4=your_tag_4
   EXCEL_4=your_excel_4.xlsx
   TAG_5=your_tag_5
   EXCEL_5=your_excel_5.xlsx
   TAG_6=your_tag_6
   EXCEL_6=your_excel_6.xlsx
   TAG_7=your_tag_7
   EXCEL_7=your_excel_7.xlsx
   ```

## アプリケーションの実行

1. **Flaskサーバーを起動**:

   ```sh
   python synology_chat.py
   ```

   サーバーは `http://0.0.0.0:5001` で起動します。

2. **Synology Chatの設定**:
   - Synology Chatで、以下の設定でアウトゴーイングウェブフックを設定します:
     - **URL**: `http://<your_server_ip>:5001/echo`
     - **トークン**: `.env` ファイルに記載されているトークンを使用
   - 使用するタグが `.env` ファイルに指定されたタグと一致していることを確認してください。

## 仕組み

- アプリケーションは `/echo` でPOSTリクエストをリスンします。
- リクエストを受信すると、 `.env` ファイルに指定されたトークンを使用して認証します。
- メッセージを処理してタイムスタンプ、ユーザー名、メッセージ内容を抽出します。
- メッセージに含まれるタグに応じて、対応するExcelファイルにデータを記録します。
- 指定されたExcelファイルが存在しない場合は新規作成し、存在する場合は新しいデータを既存のファイルに追加します。

## トラブルシューティング

- `.env` ファイルが正しく設定され、適切なタグとExcelファイル名が含まれていることを確認してください。
- Flaskサーバーが実行中であり、Synology Chatサーバーからアクセス可能であることを確認してください。
- サーバーログにエラーメッセージが表示されていないか確認してください。