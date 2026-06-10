#!/usr/bin/env python3
"""
設計書レビューツール

ExcelまたはWord形式の設計書から誤字・脱字・表記ゆれを検知し、
ユーザーの確認を得てから修正を適用します。

使い方:
    python main.py <設計書ファイル>

環境変数:
    ANTHROPIC_API_KEY  Claude API キー（必須）
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

import anthropic

from extractor import extract_text_blocks
from detector import detect_corrections, Correction
from applier import apply_corrections

BATCH_SIZE = 50  # Number of text blocks to send to Claude at once


def confirm_correction(c: Correction, index: int, total: int) -> bool:
    print(f"\n{'─' * 60}")
    print(f"[{index}/{total}] 修正候補")
    print(f"  場所     : {c.location}")
    print(f"  修正前   : {c.original}")
    print(f"  修正後   : {c.suggested}")
    print(f"  理由     : {c.reason}")
    print(f"{'─' * 60}")

    while True:
        answer = input("  この修正を適用しますか？ [y/n/q] > ").strip().lower()
        if answer in ("y", "yes"):
            return True
        elif answer in ("n", "no"):
            return False
        elif answer in ("q", "quit"):
            print("\n処理を中断しました。")
            sys.exit(0)
        else:
            print("  'y'（適用）、'n'（スキップ）、'q'（中断）を入力してください。")


def make_backup(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(f"{path.stem}_backup_{timestamp}{path.suffix}")
    shutil.copy2(path, backup)
    return backup


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"[エラー] ファイルが見つかりません: {file_path}")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[エラー] 環境変数 ANTHROPIC_API_KEY が設定されていません。")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"\n設計書レビューツール")
    print(f"{'=' * 60}")
    print(f"対象ファイル: {file_path}")

    # Extract text
    print("\nテキストを抽出中...")
    try:
        blocks = extract_text_blocks(file_path)
    except ValueError as e:
        print(f"[エラー] {e}")
        sys.exit(1)

    print(f"  {len(blocks)} 件のテキストブロックを抽出しました。")

    if not blocks:
        print("テキストが見つかりませんでした。処理を終了します。")
        return

    # Detect in batches
    print("\nClaude で問題を検出中...")
    all_corrections: list[Correction] = []
    for start in range(0, len(blocks), BATCH_SIZE):
        batch = blocks[start: start + BATCH_SIZE]
        # Adjust block_index to be absolute
        corrections = detect_corrections(batch, client)
        for c in corrections:
            c.block_index += start
        all_corrections.extend(corrections)
        print(f"  {min(start + BATCH_SIZE, len(blocks))}/{len(blocks)} ブロック処理完了")

    if not all_corrections:
        print("\n問題は検出されませんでした。設計書はきれいです！")
        return

    print(f"\n{len(all_corrections)} 件の修正候補が見つかりました。")

    # Ask user about each correction
    approved: list[Correction] = []
    for i, correction in enumerate(all_corrections, 1):
        if confirm_correction(correction, i, len(all_corrections)):
            approved.append(correction)

    if not approved:
        print("\n適用する修正はありませんでした。")
        return

    # Backup and apply
    backup_path = make_backup(file_path)
    print(f"\nバックアップを作成しました: {backup_path}")

    print(f"{len(approved)} 件の修正を適用中...")
    try:
        apply_corrections(file_path, blocks, approved)
        print(f"\n完了！ {len(approved)} 件の修正を適用しました。")
        print(f"修正済みファイル: {file_path}")
    except Exception as e:
        print(f"[エラー] 修正の適用中にエラーが発生しました: {e}")
        print(f"バックアップから復元するには: cp \"{backup_path}\" \"{file_path}\"")
        sys.exit(1)


if __name__ == "__main__":
    main()
