from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Kullanıcıya gösterilebilir kaynak kategori özetini üretir.")
    parser.add_argument("--catalog", default=str(PROCESSED_DIR / "data_catalog_2025_2026.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / "public_source_summary_2025_2026.json"))
    args = parser.parse_args()

    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    payload = build_summary(catalog)
    output_path = Path(args.output)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    output_path.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(output_path.with_suffix(".md").read_text(encoding="utf-8"))


def build_summary(catalog: dict) -> dict:
    public_sources = []
    for source in catalog.get("sources", []):
        public_sources.append(
            {
                "label": source.get("public_label", "Veri kaynağı"),
                "type": source.get("type"),
                "risk": source.get("risk"),
                "display_policy": source.get("display_policy"),
                "coverage": source.get("coverage"),
            }
        )
    return {
        "season": catalog.get("season"),
        "public_sources": public_sources,
        "policy": catalog.get("source_display_policy", {}),
        "note": "Bu dosya kullanıcı arayüzünde gösterilebilir kategori özetidir. İç veri kataloğu gerçek kaynak ve lisans takibini ayrıca tutar.",
    }


def build_markdown(payload: dict) -> str:
    lines = [
        "# Kullanıcıya Gösterilebilir Kaynak Özeti",
        "",
        f"- Sezon: {payload['season']}",
        "- Not: Bu özet gerçek kaynak takibini saklamaz; sadece ürün arayüzünde kullanılacak güvenli kategori dilini üretir.",
        "",
        "## Kaynak Kategorileri",
        "",
    ]
    for source in payload["public_sources"]:
        lines.append(
            f"- {source['label']} ({source['type']}, risk={source['risk']}): {source['coverage']}"
        )
    lines.extend(["", "## Politika", ""])
    for policy in payload["policy"].values():
        lines.append(f"- {policy}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
