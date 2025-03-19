import json
import pandas as pd
from datetime import datetime, date
import re
import os


def get_period_start_end(dt):
    """日付から期間の開始日と終了日を取得"""
    current_date = dt.date()
    if current_date.day <= 10:
        # 前月11日から今月10日
        if current_date.month == 1:
            start_date = date(current_date.year - 1, 12, 11)
        else:
            start_date = date(current_date.year, current_date.month - 1, 11)
        end_date = date(current_date.year, current_date.month, 10)
    else:
        # 今月11日から来月10日
        if current_date.month == 12:
            end_date = date(current_date.year + 1, 1, 10)
        else:
            end_date = date(current_date.year, current_date.month + 1, 10)
        start_date = date(current_date.year, current_date.month, 11)
    return start_date, end_date


def get_period_filename(start_date, end_date, extension=".json"):
    """期間に基づいてファイル名を生成"""
    return (
        f"messages_{start_date.strftime('%Y%m')}_{start_date.day:02d}-"
        f"{end_date.strftime('%Y%m')}_{end_date.day:02d}{extension}"
    )


def extract_tags(text):
    # タグを抽出（#タグ の形式）
    tags = re.findall(r"#(\w+)", text)
    # タグを除いた本文を取得
    clean_text = re.sub(r"#\w+", "", text).strip()
    return tags, clean_text


def classify_time(text, time_str):
    """メッセージの内容に基づいて時刻を分類"""
    has_start = "開始" in text
    has_end = "終了" in text

    if has_start and not has_end:
        return time_str, "", ""
    elif not has_start and has_end:
        return "", time_str, ""
    else:
        return "", "", time_str


def process_messages():
    # dataディレクトリ内の全てのJSONファイルを処理
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"ディレクトリが見つかりません: {data_dir}")
        return

    json_files = [
        f
        for f in os.listdir(data_dir)
        if f.startswith("messages_") and f.endswith(".json")
    ]

    if not json_files:
        print("処理対象のJSONファイルが見つかりません")
        return

    for json_file in json_files:
        json_path = os.path.join(data_dir, json_file)
        print(f"JSONファイルを処理中: {json_file}")

        try:
            # JSONファイルを読み込む
            with open(json_path, "r", encoding="utf-8") as f:
                messages = json.load(f)

            # メッセージを処理
            processed_messages = {}
            for msg in messages:
                # タグと本文を分離
                text = msg.get("text", "")
                tags, clean_text = extract_tags(text)
                tags_str = ", ".join(tags) if tags else ""

                # 時刻を分類
                received_at = msg.get("received_at", "")
                if received_at:
                    timestamp = datetime.fromisoformat(received_at)
                    time_str = timestamp.strftime("%H:%M")
                    start_time, end_time, unknown_time = classify_time(
                        clean_text, time_str
                    )

                    # ユーザー名でグループ化
                    username = msg.get("username", "未設定")
                    if username not in processed_messages:
                        processed_messages[username] = []

                    # データを追加
                    processed_messages[username].append(
                        {
                            "年月日": timestamp.strftime("%Y/%m/%d"),
                            "出勤時刻": start_time,
                            "退社時刻": end_time,
                            "不明": unknown_time,
                            "タグ": tags_str,
                            "本文": clean_text,
                        }
                    )

            # Excelファイルとして保存
            excel_filename = os.path.splitext(json_path)[0] + ".xlsx"
            with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
                # 各ユーザーのデータをシートとして保存
                for username, messages in processed_messages.items():
                    # DataFrameを作成
                    df = pd.DataFrame(messages)
                    # シート名としてユーザー名を使用（Excelの制限に合わせて31文字以内に制限）
                    sheet_name = username[:31]
                    # シートとして保存
                    df.to_excel(writer, index=False, sheet_name=sheet_name)

            print(f"Excelファイルを作成しました: {os.path.basename(excel_filename)}")

        except Exception as e:
            print(f"ファイル処理中にエラーが発生しました: {json_file}")
            print(f"エラー: {str(e)}")
            continue


if __name__ == "__main__":
    process_messages()
