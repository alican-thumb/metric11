"""
TFF oyuncu profillerini Transfermarkt kadro verileriyle zenginleştirir.
Eşleştirme mevcut kulüp içinde kadro adı/profil tam adı canonical karşılığı,
ardından iki-token örtüşmesi ile yapılır.
Çıktı: tff_player_profiles_enriched_2025_2026.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON
from src.normalization import canonical_player_name, normalize_name, normalize_team_name


def main() -> None:
    parser = argparse.ArgumentParser(description="TFF oyuncu profillerini Transfermarkt ile zenginleştirir.")
    parser.add_argument("--tff-input", default=str(PROCESSED_DIR / f"tff_player_profiles_league_all_{SEASON}.json"))
    parser.add_argument(
        "--fallback-tff-input",
        action="append",
        default=[
            str(PROCESSED_DIR / f"tff_player_profiles_all_priority_{SEASON}.json"),
            str(PROCESSED_DIR / f"tff_player_profiles_besiktas_{SEASON}.json"),
        ],
        help="Lig geneli tek dosya henüz yoksa birleştirilecek mevcut profil dosyaları.",
    )
    parser.add_argument("--tm-input", default=str(PROCESSED_DIR / f"transfermarkt_super_lig_squads_{SEASON}.json"))
    parser.add_argument("--tm-profiles", default=str(PROCESSED_DIR / f"transfermarkt_super_lig_player_profiles_{SEASON}.json"))
    parser.add_argument("--manual-aliases", default="data/manual/tm_player_manual_aliases.json")
    parser.add_argument("--output", default=str(PROCESSED_DIR / f"tff_player_profiles_enriched_{SEASON}.json"))
    args = parser.parse_args()

    tff_path = Path(args.tff_input)
    tm_path = Path(args.tm_input)

    if not tm_path.exists():
        raise SystemExit(f"Transfermarkt dosyası bulunamadı: {tm_path}. Önce collect_transfermarkt_league_squads çalıştırın.")

    tff_players = load_tff_profiles(tff_path, [Path(value) for value in args.fallback_tff_input])
    manual_aliases = load_manual_aliases(Path(args.manual_aliases))
    tm_payload: dict = json.loads(tm_path.read_text(encoding="utf-8"))
    tm_profiles_path = Path(args.tm_profiles)
    tm_profiles = json.loads(tm_profiles_path.read_text(encoding="utf-8")) if tm_profiles_path.exists() else {}
    profile_by_id = {
        str(item.get("transfermarkt_id")): item for item in tm_profiles.get("players", []) if item.get("transfermarkt_id")
    }

    # Constrain candidates to their club so same-name and transferred players
    # cannot be silently attached to a different current squad.
    tm_by_club: dict[str, list[dict]] = {}
    for club in tm_payload.get("clubs", []):
        club_key = normalize_team_name(club.get("team_name"))
        for p in club.get("players", []):
            if club_key:
                profile = profile_by_id.get(str(p.get("transfermarkt_id")), {})
                identity_names = [
                    value for value in (p.get("name"), profile.get("full_name"), profile.get("display_name")) if value
                ]
                tm_by_club.setdefault(club_key, []).append(
                    {
                        **p,
                        "_tm_team_name": club.get("team_name"),
                        "_tm_profile_full_name": profile.get("full_name"),
                        "_identity_names": list(dict.fromkeys(identity_names)),
                    }
                )

    enriched = []
    match_full = 0
    match_profile_full_name = 0
    match_last = 0
    match_manual = 0
    no_match = 0

    for player in tff_players:
        tff_norm = normalize_name(player.get("name", ""))
        club_key = normalize_team_name(player.get("club"))
        candidates = tm_by_club.get(club_key or "", [])
        tff_canonical = canonical_player_name(player.get("name", ""))
        exact_hits = [
            candidate
            for candidate in candidates
            if any(canonical_player_name(value) == tff_canonical for value in candidate.get("_identity_names", []))
        ]
        tm_hit = exact_hits[0] if len(exact_hits) == 1 else None
        method = "club_canonical"
        if tm_hit and canonical_player_name(tm_hit.get("name", "")) != tff_canonical:
            method = "club_profile_full_name"

        if tm_hit is None and tff_norm:
            tff_tokens = set(tff_norm.split())
            token_hits = [
                candidate
                for candidate in candidates
                if any(
                    len(tff_tokens & set(normalize_name(value).split())) >= 2
                    for value in candidate.get("_identity_names", [])
                )
            ]
            if len(token_hits) == 1:
                tm_hit = token_hits[0]
                method = "club_token_overlap"

        # Manual alias override (highest priority, applied last so automated match isn't blocked)
        manual_alias = _find_manual_alias(player, manual_aliases)

        enriched_player = dict(player)
        if manual_alias and tm_hit is None:
            # Apply manual alias for players automated matching couldn't resolve
            enriched_player["tm_market_value_eur"] = manual_alias.get("tm_market_value_eur")
            enriched_player["tm_market_value_text"] = manual_alias.get("tm_market_value_text")
            enriched_player["tm_contract_until"] = None
            enriched_player["tm_position"] = manual_alias.get("tm_position")
            enriched_player["tm_position_group"] = manual_alias.get("tm_position_group")
            enriched_player["tm_id"] = None
            enriched_player["tm_name"] = manual_alias.get("tm_name")
            enriched_player["tm_profile_url"] = None
            enriched_player["tm_profile_full_name"] = None
            enriched_player["tm_team_name"] = player.get("club")
            enriched_player["tm_match_method"] = "manual_alias"
            enriched_player["tm_requires_network_verify"] = manual_alias.get("requires_network_verify", True)
            enriched.append(enriched_player)
            match_manual += 1
            continue

        if tm_hit:
            enriched_player["tm_market_value_eur"] = tm_hit.get("market_value_eur")
            enriched_player["tm_market_value_text"] = tm_hit.get("market_value_text")
            enriched_player["tm_contract_until"] = tm_hit.get("contract_until")
            enriched_player["tm_position"] = tm_hit.get("position")
            enriched_player["tm_position_group"] = tm_hit.get("position_group")
            enriched_player["tm_id"] = tm_hit.get("transfermarkt_id")
            enriched_player["tm_name"] = tm_hit.get("name")
            enriched_player["tm_profile_url"] = tm_hit.get("profile_url")
            enriched_player["tm_profile_full_name"] = tm_hit.get("_tm_profile_full_name")
            enriched_player["tm_team_name"] = tm_hit.get("_tm_team_name")
            enriched_player["tm_match_method"] = method
            if method == "club_canonical":
                match_full += 1
            elif method == "club_profile_full_name":
                match_profile_full_name += 1
            else:
                match_last += 1
        else:
            enriched_player["tm_market_value_eur"] = None
            enriched_player["tm_market_value_text"] = None
            enriched_player["tm_contract_until"] = None
            enriched_player["tm_position"] = None
            enriched_player["tm_position_group"] = None
            enriched_player["tm_id"] = None
            enriched_player["tm_name"] = None
            enriched_player["tm_profile_url"] = None
            enriched_player["tm_profile_full_name"] = None
            enriched_player["tm_team_name"] = None
            enriched_player["tm_match_method"] = None
            no_match += 1

        enriched.append(enriched_player)

    total = len(tff_players)
    in_scope = sum(1 for player in tff_players if normalize_team_name(player.get("club")) in tm_by_club)
    matched = match_full + match_profile_full_name + match_last + match_manual
    print(f"TFF oyuncu: {total}")
    print(f"  Snapshot kapsamındaki TFF oyuncu: {in_scope}")
    print(f"  Kulüp içi canonical eşleşme: {match_full}")
    print(f"  Kulüp içi profil tam-ad eşleşme: {match_profile_full_name}")
    print(f"  Kulüp içi token eşleşme: {match_last}")
    print(f"  Manuel alias eşleşme: {match_manual}")
    print(f"  Eşleşmedi: {no_match}")
    print(f"  Tüm profil kapsamı: %{round(matched / total * 100, 1) if total else 0}")
    print(f"  Lig snapshot içi kapsama: %{round(matched / in_scope * 100, 1) if in_scope else 0}")

    Path(args.output).write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Çıktı: {args.output}")

    _write_markdown_summary(
        enriched,
        Path(args.output).with_suffix(".md"),
        match_full,
        match_profile_full_name,
        match_last,
        no_match,
        set(tm_by_club),
    )


def load_manual_aliases(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("aliases", [])
    except Exception:
        return []


def _find_manual_alias(player: dict, aliases: list[dict]) -> dict | None:
    tff_name_norm = normalize_name(player.get("name", ""))
    club_norm = normalize_team_name(player.get("club") or "")
    for alias in aliases:
        alias_name_norm = normalize_name(alias.get("tff_name", ""))
        alias_club_norm = normalize_team_name(alias.get("tff_club", ""))
        if tff_name_norm == alias_name_norm and club_norm == alias_club_norm:
            return alias
    return None


def load_tff_profiles(preferred: Path, fallbacks: list[Path]) -> list[dict]:
    paths = [preferred] if preferred.exists() else [path for path in fallbacks if path.exists()]
    if not paths:
        raise SystemExit(f"TFF dosyası bulunamadı: {preferred} veya fallback dosyaları")
    profiles: dict[str, dict] = {}
    for path in paths:
        for item in json.loads(path.read_text(encoding="utf-8")):
            key = str(item.get("external_id") or f"{item.get('name')}|{item.get('club')}")
            profiles[key] = {**profiles.get(key, {}), **item}
    return sorted(profiles.values(), key=lambda item: (item.get("club") or "", item.get("name") or ""))


def _write_markdown_summary(
    enriched: list[dict],
    md_path: Path,
    match_full: int,
    match_profile_full_name: int,
    match_last: int,
    no_match: int,
    snapshot_clubs: set[str],
) -> None:
    total = len(enriched)
    matched = [p for p in enriched if p.get("tm_id")]
    in_scope = [p for p in enriched if normalize_team_name(p.get("club")) in snapshot_clubs]
    valued = [p for p in matched if p.get("tm_market_value_eur")]
    top10 = sorted(valued, key=lambda p: p["tm_market_value_eur"], reverse=True)[:10]

    lines = [
        f"# TFF × Transfermarkt Zenginleştirilmiş Oyuncu Profilleri — {SEASON.replace('_', '-')}",
        "",
        f"- Toplam TFF oyuncu: {total}",
        f"- Lig snapshot kapsamında TFF oyuncu: {len(in_scope)}",
        f"- Kulüp içi canonical eşleşme: {match_full}",
        f"- Kulüp içi profil tam-ad eşleşme: {match_profile_full_name}",
        f"- Kulüp içi token eşleşme: {match_last}",
        f"- Eşleşmedi: {no_match}",
        f"- Tüm profil kapsamı: %{round(len(matched) / total * 100, 1) if total else 0}",
        f"- Lig snapshot içi kapsama: %{round(len(matched) / len(in_scope) * 100, 1) if in_scope else 0}",
        "",
        "## En Yüksek Piyasa Değeri (Eşleşen Oyuncular)",
        "",
    ]
    for p in top10:
        val = p["tm_market_value_eur"]
        val_str = f"€{val / 1_000_000:.1f}M" if val and val >= 1_000_000 else f"€{val:,}" if val else "—"
        lines.append(
            f"- {p.get('name')} ({p.get('club', '?')}) — {val_str} | "
            f"Sözleşme: {p.get('tm_contract_until') or p.get('contract_end') or '?'} | "
            f"Pozisyon: {p.get('tm_position') or '?'}"
        )

    no_match_players = [p for p in enriched if not p.get("tm_id")]
    if no_match_players:
        lines.extend(["", "## Eşleşmeyen Oyuncular (İlk 20)", ""])
        for p in no_match_players[:20]:
            lines.append(f"- {p.get('name')} ({p.get('club', '?')})")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Özet: {md_path}")


if __name__ == "__main__":
    main()
