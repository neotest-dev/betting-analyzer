from typing import List, Dict, Any

class PerformanceTrends:
    """Analyzes performance trends across historical matches"""

    @staticmethod
    def calculate_recent_form(historical_matches: List[Dict[str, Any]], team_name: str, matches_count: int = 5) -> Dict[str, Any]:
        """Compute form stats for the last N matches"""
        team_matches = [
            m for m in historical_matches
            if m.get("home_team", "").lower() == team_name.lower() or m.get("away_team", "").lower() == team_name.lower()
        ]
        
        recent = team_matches[-matches_count:] if len(team_matches) >= matches_count else team_matches
        
        if not recent:
            return {"team": team_name, "wins": 0, "draws": 0, "losses": 0, "form_string": "N/A"}

        wins = 0
        draws = 0
        losses = 0
        form_seq = []

        for m in recent:
            is_home = m.get("home_team", "").lower() == team_name.lower()
            h_goals = m.get("home_goals", 0)
            a_goals = m.get("away_goals", 0)

            if h_goals == a_goals:
                draws += 1
                form_seq.append("D")
            elif (is_home and h_goals > a_goals) or (not is_home and a_goals > h_goals):
                wins += 1
                form_seq.append("W")
            else:
                losses += 1
                form_seq.append("L")

        return {
            "team": team_name,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "form_string": "".join(form_seq)
        }
