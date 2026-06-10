"""Create sample Excel and Word files with intentional errors for testing."""

from pathlib import Path


def create_sample_excel():
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "基本設計"

    data = [
        ["項目", "説明", "備考"],
        ["ユーザー認証", "ログイン時にパスワードを確認する", "セキュリティ要件参照"],
        ["ユーザ管理", "管理者がユーザを登録・削除できる", "ユーザー一覧画面から操作"],  # 表記ゆれ: ユーザー/ユーザ
        ["データ保存", "入力されたデータをデータベースに保存すう", "PostgreSQL使用"],  # 誤字: 保存すう
        ["エラー処理", "システムエラー発生時にログを記録する", ""],
        ["レポート出力", "月次レポートをPDF形式で出力する", "帳票設計書参照"],
        ["通知機能", "処理完了時にメールで通する", "SMTPサーバー使用"],  # 脱字: 通する→通知する
    ]

    for row in data:
        ws.append(row)

    path = Path("sample_design.xlsx")
    wb.save(path)
    print(f"作成: {path}")


def create_sample_word():
    from docx import Document

    doc = Document()
    doc.add_heading("システム基本設計書", 0)

    doc.add_heading("1. 概要", 1)
    doc.add_paragraph(
        "本システムはWebアプリケーションとして実装する。"
        "ユーザーはブラウザからアクセスし、各種機能を利用できる。"
    )

    doc.add_heading("2. 機能一覧", 1)
    doc.add_paragraph(
        "ユーザ認証機能：IDとパスワードによる認証を行う。"  # 表記ゆれ
    )
    doc.add_paragraph(
        "データ入力機能：フォームからデータを入力し、データベースに保管する。"  # 誤字: 保管→保存
    )
    doc.add_paragraph(
        "検索機能：条件を指定してデータを索できる。"  # 脱字: 索→検索
    )
    doc.add_paragraph(
        "レポート機能：月次・年次のレポートをエクセル形式で出力する。"
    )

    doc.add_heading("3. 非機能要件", 1)
    doc.add_paragraph("可用性：システムの稼働率は99.9%以上を目標とする。")
    doc.add_paragraph("性能：レスポンス時間は3秒以内とすう。")  # 誤字: とすう→とする

    path = Path("sample_design.docx")
    doc.save(path)
    print(f"作成: {path}")


if __name__ == "__main__":
    create_sample_excel()
    create_sample_word()
    print("サンプルファイルを作成しました。")
