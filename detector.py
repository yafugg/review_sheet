"""Detect typos, missing characters, and notation inconsistencies using Claude API."""

import json
from dataclasses import dataclass

import anthropic

from extractor import TextBlock


@dataclass
class Correction:
    location: str
    original: str
    suggested: str
    reason: str
    block_index: int  # index in the TextBlock list


SYSTEM_PROMPT = """あなたは日本語の設計書レビュアーです。
与えられたテキストブロックのリストから、以下の問題を検出してください：

1. 誤字（例：「設定」→「設置」の誤り）
2. 脱字（文字が抜けている箇所）
3. 表記ゆれ（同じ意味の語が異なる表記で使われている。例：「ユーザー」と「ユーザ」の混在）

各問題について以下のJSON形式で返してください：
[
  {
    "block_index": <テキストブロックのインデックス番号>,
    "original": "<問題のある元のテキスト（セル全体または段落全体）>",
    "suggested": "<修正後のテキスト>",
    "reason": "<修正理由の説明>"
  }
]

問題がない場合は空のJSON配列 [] を返してください。
JSON以外のテキストは含めないでください。"""


def detect_corrections(blocks: list[TextBlock], client: anthropic.Anthropic) -> list[Correction]:
    if not blocks:
        return []

    # Build the input for Claude
    blocks_text = "\n".join(
        f"[{i}] ({b.location}): {b.text}"
        for i, b in enumerate(blocks)
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"以下のテキストブロックを確認し、問題を検出してください：\n\n{blocks_text}",
            }
        ],
    )

    response_text = message.content[0].text.strip()

    # Strip markdown code fences if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    try:
        items = json.loads(response_text)
    except json.JSONDecodeError:
        print(f"[警告] Claude のレスポンスをパースできませんでした:\n{response_text}")
        return []

    corrections = []
    for item in items:
        idx = item.get("block_index", -1)
        if 0 <= idx < len(blocks):
            corrections.append(
                Correction(
                    location=blocks[idx].location,
                    original=item.get("original", ""),
                    suggested=item.get("suggested", ""),
                    reason=item.get("reason", ""),
                    block_index=idx,
                )
            )
    return corrections
