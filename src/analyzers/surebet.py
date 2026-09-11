from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any
from src.calculators.stakes import StakeCalculator
from src.odds.matcher import EventMatcher


class SurebetAnalyzer:
    """
    SUREBET ANALYZER MODULE
    Detects mathematical arbitrage opportunities across MULTIPLE bookmakers.

    A valid surebet requires:
      1. inverse_sum = sum(1/odd_i) < 1.0  (mathematical arbitrage condition)
      2. Each selection must come from a DIFFERENT bookmaker (cross-bookmaker)

    Rule #2 prevents false positives where all best odds happen to come from the
    same operator — those are NOT exploitable in practice.
    """

    @staticmethod
    def analyze_event(event: Dict[str, Any], default_bankroll: float = 100.0) -> List[Dict[str, Any]]:
        """
        Analyze an event for surebet opportunities across bookmakers.

        Formula:
          inverse_sum = 1/odds_1 + 1/odds_2 (+ 1/odds_3)
          If inverse_sum < 1 AND bookmakers are diverse => Surebet opportunity.
          ROI = (1/inverse_sum - 1) * 100
        """
        bookmakers = event.get("bookmakers", [])
        if len(bookmakers) < 2:
            return []

        market = event.get("market", "1X2")
        best_odds = EventMatcher.extract_best_odds(bookmakers)

        # Determine required outcome keys for this market type
        required_outcomes = []
        if market == "1X2":
            required_outcomes = ["home_win", "draw", "away_win"]
        elif market in ["Moneyline", "Over/Under Goals 2.5", "Corners Over/Under 9.5"]:
            keys = list(best_odds.keys())
            if len(keys) >= 2:
                required_outcomes = keys[:2]

        if not required_outcomes or not all(k in best_odds for k in required_outcomes):
            return []

        odds_list = [best_odds[k]["odds"] for k in required_outcomes]
        bookies_list = [best_odds[k]["bookmaker"] for k in required_outcomes]

        # ── VALIDATION: Bookmaker diversity ──────────────────────────────────
        # A surebet requires placing bets at DIFFERENT bookmakers. If all best
        # odds come from the same operator, this is a mathematical coincidence,
        # NOT an exploitable arbitrage opportunity.
        unique_bookmakers = set(bookies_list)
        if len(unique_bookmakers) < 2:
            return []
        # ─────────────────────────────────────────────────────────────────────

        calculation = StakeCalculator.calculate_surebet_stakes(default_bankroll, odds_list)

        if not calculation["is_surebet"]:
            return []

        legs = []
        for idx, k in enumerate(required_outcomes):
            stake_info = calculation["stakes"][idx]
            legs.append({
                "selection": k,
                "bookmaker": bookies_list[idx],
                "odds": float(odds_list[idx]),
                "stake_amount": stake_info["stake"],
                "stake_percentage": stake_info["percentage"],
                "payout": stake_info["payout"]
            })

        opp_id = f"surebet_{event['event_id']}_{market.replace(' ', '_')}"

        return [{
            "opportunity_id": opp_id,
            "type": "surebet",
            "event_id": event["event_id"],
            "sport": event["sport"],
            "league": event["league"],
            "home_team": event["home_team"],
            "away_team": event["away_team"],
            "market": market,
            "roi": calculation["roi_percentage"],
            "probability": round((1.0 / calculation["inverse_sum"]) * 100, 2),
            "timestamp": event.get("timestamp", ""),
            "details": {
                "inverse_sum": calculation["inverse_sum"],
                "profit": calculation["profit"],
                "bankroll": default_bankroll,
                "unique_bookmakers": sorted(unique_bookmakers),
                "unique_bookmakers_count": len(unique_bookmakers),
                "legs": legs
            }
        }]
