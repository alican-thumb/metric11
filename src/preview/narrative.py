from __future__ import annotations

from src.preview.probability import action_label


def build_narrative(
    target_team: str,
    opponent: str,
    team_form: dict,
    team_strength: dict,
    opponent_recent_form: dict,
    opponent_strength: dict,
    opponent_history: dict,
    opponent_defense: dict,
    availability_signal: dict,
    referee_signal: dict,
    player_signals: dict,
    goal_candidates: dict,
    probability: dict,
    lineup_recommendation: dict,
    coach_lineup_audit: dict,
    transfer_impact: dict,
    is_big_match: bool,
) -> list[str]:
    paragraphs = []
    match_type = "büyük maç/derbi seviyesi" if is_big_match else "normal lig maçı"
    paragraphs.append(
        f"{target_team} bu karşılaşmaya son {team_form['last_n']} maçta "
        f"{team_form['wins']} galibiyet, {team_form['draws']} beraberlik ve {team_form['losses']} mağlubiyetlik "
        f"formla geliyor. Bu pencere içinde maç başı {team_form['goals_for_per_match']} gol üretip "
        f"{team_form['goals_against_per_match']} gol yedi. Eşleşme tipi: {match_type}."
    )
    if team_strength.get("available") and opponent_strength.get("available"):
        edge = team_strength["strength_score"] - opponent_strength["strength_score"]
        edge_text = "avantajlı" if edge > 4 else "dezavantajlı" if edge < -4 else "dengede"
        paragraphs.append(
            f"Takım gücü katmanı {target_team} için {team_strength['strength_score']}/100, "
            f"{opponent} için {opponent_strength['strength_score']}/100 skor üretiyor; güç farkı "
            f"{round(edge, 1)} puan ve maç {edge_text} okunuyor. Bu skor puan/maç, gol farkı, son form, "
            f"iç-dış saha performansı ve kadro sürekliliğinden türetildi."
        )

    if opponent_history.get("matches"):
        paragraphs.append(
            f"Bu sezon {opponent} ile önceki eşleşme verisi var: {opponent_history['matches']} maçta "
            f"Beşiktaş maç başı {opponent_history['goals_for_per_match']} gol ve "
            f"{opponent_history['cards_for_per_match']} kart ortalaması üretti. Bu yüzden raporda hem skor hem kart tarafı "
            f"önceki eşleşme etkisiyle ayarlandı."
        )
    else:
        paragraphs.append(
            f"Bu sezon {opponent} ile önceki eşleşme bulunmadığı için rakip özel sinyal zayıf; ağırlık daha çok son form ve oyuncu kullanımına verildi."
        )

    if opponent_recent_form.get("last_n"):
        paragraphs.append(
            f"Rakibin son {opponent_recent_form['last_n']} maçlık genel formu modele ayrı eklendi: "
            f"maç başı {opponent_recent_form['goals_for_per_match']} gol atıp "
            f"{opponent_recent_form['goals_against_per_match']} gol yiyor. Skor tahmini artık sadece Beşiktaş formuna değil, "
            f"rakibin hücum/savunma profilinin birleşimine göre hesaplanıyor."
        )

    if opponent_defense.get("available"):
        paragraphs.append(
            f"Rakibin son {opponent_defense['last_n']} maçlık savunma formu gol adayı modeline eklendi: "
            f"maç başı {opponent_defense['goals_against_per_match']} gol yiyor, "
            f"%{round(opponent_defense['clean_sheet_rate'] * 100)} clean sheet oranı var. "
            f"Gol adayı skor çarpanı {opponent_defense['goal_candidate_multiplier']}."
        )

    if availability_signal.get("unavailable"):
        unavailable_names = ", ".join(item.get("player_name") or item.get("player_external_id") for item in availability_signal["unavailable"][:5])
        paragraphs.append(
            f"Eksik oyuncu sinyali modele dahil edildi: {unavailable_names}. Bu oyuncular olası 11 ve gol adayı listesinden çıkarıldı; "
            f"skor beklentisi düşük güvenle aşağı ayarlandı."
        )

    if referee_signal.get("prior_matches"):
        paragraphs.append(
            f"Hakem profili kart tarafında anlamlı bir sinyal veriyor: {referee_signal['referee']} bu sezon önceki "
            f"{referee_signal['prior_matches']} Beşiktaş maçında toplam maç başı {referee_signal['cards_per_match']} kart, "
            f"Beşiktaş'a maç başı {referee_signal['target_cards_per_match']} kart ortalamasıyla öne çıkıyor."
        )
    elif referee_signal.get("available"):
        paragraphs.append(f"Hakem için bu sezon önceki Beşiktaş örneği yok; hakem etkisi düşük güvenle ele alındı.")

    starters = ", ".join(player["name"] for player in player_signals["likely_starters"][:6])
    card_risks = ", ".join(player["name"] for player in player_signals["card_risk_players"][:4])
    if starters:
        paragraphs.append(
            f"Olası 11 sinyalinde son dönemde öne çıkan isimler: {starters}. Kart riski tarafında ise son 8 maç penceresinde "
            f"{card_risks or 'belirgin bir oyuncu'} dikkat çekiyor."
        )
    else:
        paragraphs.append(
            f"Olası 11 sinyali için veri penceresi zayıf. Kart riski tarafında ise son maç penceresinde "
            f"{card_risks or 'belirgin bir oyuncu'} dikkat çekiyor."
        )
    goal_names = ", ".join(candidate["name"] for candidate in goal_candidates["candidates"][:4])
    actual_note = ""
    if goal_candidates["actual_scorers"]:
        actual_names = ", ".join(goal["name"] for goal in goal_candidates["actual_scorers"])
        actual_note = f" Test sonucunda gerçek Beşiktaş golcüleri: {actual_names}."
    paragraphs.append(
        f"Gol adayı sinyalinde öne çıkan isimler: {goal_names or 'belirgin bir oyuncu yok'}. "
        f"Bu skor son gol formu, sezon içi gol sayısı ve son dönemde ilk 11 başlama sıklığından türetildi.{actual_note}"
    )
    top_scores = ", ".join(
        f"{item['score']} (%{round(item['probability'] * 100)})"
        for item in probability.get("top_scorelines", [])[:3]
    )
    call = probability.get("recommended_call", {})
    paragraphs.append(
        f"Skor dağılımında en olası senaryolar: {top_scores}. Model aksiyonu: "
        f"{call.get('action_label') or action_label(call.get('action'))}; önerilen ana skor {call.get('scoreline') or 'yok'}."
    )
    caution_names = ", ".join(item["name"] for item in lineup_recommendation.get("card_caution", [])[:3])
    paragraphs.append(
        f"Kadro tercih önerisi: {lineup_recommendation['plan']}. Hücum önceliği "
        f"{', '.join(lineup_recommendation.get('attacking_priority', [])[:3]) or 'net değil'}. "
        f"Disiplin yönetimi gereken oyuncular: {caution_names or 'belirgin sinyal yok'}."
    )
    paragraphs.append(
        f"Teknik direktör kadro denetimi: model gerçek ilk 11 ile önerilen çekirdek plan arasında "
        f"%{round(coach_lineup_audit.get('alignment_rate', 0) * 100)} uyum buldu; karar etiketi "
        f"{coach_lineup_audit.get('verdict')}. Alternatif model 11'i kullanılsaydı xG "
        f"{probability['expected_goals_for']}-{probability['expected_goals_against']} yerine "
        f"{coach_lineup_audit.get('alternative_xg_for')}-{coach_lineup_audit.get('alternative_xg_against')} bandına gelebilirdi."
    )
    if transfer_impact.get("candidates"):
        top_transfer = transfer_impact["candidates"][0]
        paragraphs.append(
            f"Transfer etki simülasyonunda örnek aday {top_transfer['player_name']} ({top_transfer['target_role']}) "
            f"maç planına eklenseydi model xG'yi {top_transfer['current_expected_goals_for']}-{top_transfer['current_expected_goals_against']} "
            f"bandından {top_transfer['simulated_expected_goals_for']}-{top_transfer['simulated_expected_goals_against']} bandına taşırdı. "
            f"Bu senaryoda en olası skor {top_transfer['simulated_scoreline']['score']} ve kazanma olasılığı "
            f"%{round(top_transfer['simulated_target_win_probability'] * 100)} olurdu."
        )
    paragraphs.append(
        f"MVP olasılık motoru Beşiktaş galibiyetini %{round(probability['target_win_probability'] * 100)}, beraberliği "
        f"%{round(probability['draw_probability'] * 100)}, rakip galibiyetini %{round(probability['opponent_win_probability'] * 100)} "
        f"olarak işaretliyor. Gol beklentisi {probability['expected_goals_for']}-{probability['expected_goals_against']}; "
        f"kart sinyali {probability['card_signal']}."
    )
    return paragraphs
