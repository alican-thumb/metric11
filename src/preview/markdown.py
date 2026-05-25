from __future__ import annotations

from src.preview.probability import action_label


def build_markdown(preview: dict) -> str:
    match = preview["match"]
    probability = preview["probabilities"]
    target_team = match["target_team"]
    lines = [
        f"# Maç Önü Raporu: {match['home_team']} - {match['away_team']}",
        "",
        f"- Maç ID: `{match['match_id']}`",
        f"- Tarih: {match['date']}",
        f"- Hakem: {match['main_referee']}",
        f"- Büyük maç: {match['is_big_match']}",
        f"- Veri penceresi: {preview['data_window']['prior_match_count']} önceki maç",
        f"- Not: Bu rapor test amaçlıdır; gerçek sonuç {match['actual_score']} olarak sonradan biliniyor ama hesaplamada kullanılmadı.",
        "",
        "## Olasılık Sinyali",
        "",
        f"- {target_team} kazanır: %{round(probability['target_win_probability'] * 100)}",
        f"- Beraberlik: %{round(probability['draw_probability'] * 100)}",
        f"- Rakip kazanır: %{round(probability['opponent_win_probability'] * 100)}",
        f"- Beklenen gol: {probability['expected_goals_for']} - {probability['expected_goals_against']}",
        f"- En olası skor: {probability.get('recommended_scoreline', {}).get('score')} (%{round(probability.get('recommended_scoreline', {}).get('probability', 0) * 100)})",
        f"- Model aksiyonu: {probability.get('recommended_call', {}).get('action_label') or action_label(probability.get('recommended_call', {}).get('action'))}",
        f"- Kart sinyali: {probability['card_signal']} ({probability['team_card_expectation']} {target_team} kart beklentisi)",
        f"- Eksik oyuncu sinyali: {probability.get('availability_missing_count', 0)}",
        f"- Beraberlik risk katmanı: {probability.get('draw_calibration', {}).get('risk_level', 'NONE')} ({', '.join(probability.get('draw_calibration', {}).get('reasons', [])) or 'sinyal yok'})",
        f"- Korumalı tahmin aksiyonu: {action_label(probability.get('draw_risk', {}).get('recommended_model_action', 'KEEP_MAIN_PICK'))} "
        f"(risk {probability.get('draw_risk', {}).get('risk_level', 'LOW')}, skor {probability.get('draw_risk', {}).get('score', 0)})",
        f"- Büyük maç profili: {probability.get('big_match_profile', {}).get('risk_level', 'NONE')} ({probability.get('big_match_profile', {}).get('adjustment', '-')})",
        f"- Güven: {probability['confidence']}",
        "",
        "## Takım Gücü Katmanı",
        "",
    ]
    team_strength = preview.get("team_strength_signal", {})
    opponent_strength = preview.get("opponent_strength_signal", {})
    if team_strength.get("available") and opponent_strength.get("available"):
        lines.extend(
            [
                f"- {target_team} güç skoru: {team_strength['strength_score']}/100 "
                f"(atak {team_strength['attack_score']}, savunma {team_strength['defense_score']}, süreklilik {team_strength['continuity_score']})",
                f"- Rakip güç skoru: {opponent_strength['strength_score']}/100 "
                f"(atak {opponent_strength['attack_score']}, savunma {opponent_strength['defense_score']}, süreklilik {opponent_strength['continuity_score']})",
                f"- Güç farkı: {round(team_strength['strength_score'] - opponent_strength['strength_score'], 1)}",
                f"- {target_team} çekirdek oyuncu sayısı: {team_strength.get('core_player_count', 0)} | Rakip çekirdek oyuncu sayısı: {opponent_strength.get('core_player_count', 0)}",
            ]
        )
    else:
        lines.append("- Takım gücü katmanı için yeterli veri yok.")

    lines.extend(
        [
            "",
            "## Olası 11 Sinyali",
            "",
        ]
    )
    for player in preview["player_signals"]["likely_starters"][:11]:
        lines.append(f"- {player['name']}: son pencere ilk 11={player['recent_starts']}, yedek={player['recent_bench']}")

    lines.extend(["", "## Kadro Tercih Önerisi", ""])
    lineup = preview.get("lineup_recommendation", {})
    lines.append(f"- Plan: {lineup.get('plan')}")
    lines.append(f"- Çekirdek 11 sinyali: {', '.join(lineup.get('core_starters', [])) or 'Yok'}")
    lines.append(f"- Hücum önceliği: {', '.join(lineup.get('attacking_priority', [])) or 'Yok'}")
    if lineup.get("card_caution"):
        for item in lineup["card_caution"]:
            lines.append(f"- Disiplin uyarısı: {item['name']} | kart/ilk11={item['cards_per_recent_start']} | {item['recommendation']}")
    else:
        lines.append("- Disiplin uyarısı: belirgin sinyal yok.")

    lines.extend(["", "## Teknik Direktör Kadro Denetimi", ""])
    audit = preview.get("coach_lineup_audit", {})
    lines.append(f"- Karar etiketi: {audit.get('verdict')}")
    lines.append(f"- Gerçek 11 / model 11 uyumu: %{round((audit.get('alignment_rate') or 0) * 100)}")
    lines.append(f"- Gerçek 11 skoru: {audit.get('actual_lineup_score')} | Model 11 skoru: {audit.get('recommended_lineup_score')}")
    lines.append(
        f"- Alternatif xG: {probability['expected_goals_for']}-{probability['expected_goals_against']} -> "
        f"{audit.get('alternative_xg_for')}-{audit.get('alternative_xg_against')}"
    )
    if audit.get("alternative_scoreline"):
        lines.append(
            f"- Alternatif en olası skor: {audit['alternative_scoreline']['score']} "
            f"(%{round(audit['alternative_scoreline']['probability'] * 100)})"
        )
    lines.append(f"- Model çekirdek 11: {', '.join(audit.get('model_core_starters', [])) or 'Yok'}")
    lines.append(f"- Gerçek ilk 11'de olmayan model oyuncuları: {', '.join(audit.get('omitted_core_players', [])) or 'Yok'}")
    if audit.get("questionable_starters"):
        for item in audit["questionable_starters"]:
            lines.append(f"- Tartışmalı tercih: {item['name']} | {item['reason']}")
    else:
        lines.append("- Tartışmalı tercih: belirgin sinyal yok.")

    lines.extend(["", "## Skor Senaryoları", ""])
    for item in probability.get("top_scorelines", [])[:6]:
        lines.append(f"- {item['score']}: %{round(item['probability'] * 100)}")

    lines.extend(["", "## Transfer Etki Simülasyonu", ""])
    transfer_impact = preview.get("transfer_impact_simulations", {})
    if transfer_impact.get("candidates"):
        lines.append(f"- Not: {transfer_impact.get('note')}")
        for item in transfer_impact["candidates"][:6]:
            lines.append(
                f"- {item['player_name']} ({item['current_team']} / {item['target_role']}): "
                f"xG {item['current_expected_goals_for']}-{item['current_expected_goals_against']} -> "
                f"{item['simulated_expected_goals_for']}-{item['simulated_expected_goals_against']}, "
                f"{target_team} kazanma %{round(item['simulated_target_win_probability'] * 100)}, "
                f"skor {item['simulated_scoreline']['score']} (%{round(item['simulated_scoreline']['probability'] * 100)}), "
                f"etki={item['impact_label']}, rol-fit={item['role_fit_score']}, güven={item['position_confidence']}. "
                f"{item.get('commercial_note') or ''}"
            )
    else:
        lines.append(f"- {transfer_impact.get('note') or 'Transfer etki simülasyonu için aday yok.'}")

    lines.extend(["", "## Kart Riski", ""])
    for player in preview["player_signals"]["card_risk_players"][:8]:
        lines.append(
            f"- {player['name']}: kart={player['recent_cards']}, ilk 11={player['recent_starts']}, "
            f"kart/ilk 11={player['cards_per_recent_start']}, büyük maç kart={player['big_match_cards']}"
        )

    lines.extend(["", "## Gol Adayları", ""])
    for player in preview["goal_candidates"]["candidates"][:8]:
        marker = " / gerçek golcü" if player["actual_scorer"] else ""
        lines.append(
            f"- {player['name']}: skor={player['goal_threat_score']}, sezon gol={player['season_goals_before_match']}, "
            f"son pencere gol={player['recent_goals']}, ilk 11={player['recent_starts']}, "
            f"rakip savunma çarpanı={player.get('opponent_defense_multiplier', 1.0)}{marker}"
        )

    lines.extend(["", "## Eksik / Uygunluk Sinyali", ""])
    if preview.get("availability_signal", {}).get("unavailable"):
        for item in preview["availability_signal"]["unavailable"]:
            lines.append(
                f"- {item['status']}: {item.get('player_name') or item.get('player_external_id')} | "
                f"{item.get('reason', '')} | kaynak={item.get('source')} | güven={item.get('confidence')}"
            )
    else:
        lines.append("- Bu maç için eksik oyuncu sinyali yok.")

    lines.extend(["", "## Anlatılı Analiz", ""])
    lines.extend(preview["narrative"])
    return "\n\n".join(lines)
