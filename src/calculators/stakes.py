from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any


class StakeCalculator:
    """Calculates surebet stake distribution using Decimal precision"""

    @staticmethod
    def calculate_surebet_stakes(bankroll: float, odds_list: List[float]) -> Dict[str, Any]:
        """
        Calculate optimal surebet stakes for a given bankroll using Decimal precision.

        Formula:
          inverse_sum = sum(1 / odds_i)
          stake_i = bankroll / (odds_i * inverse_sum)
        """
        b_dec = Decimal(str(bankroll))
        odds_dec = [Decimal(str(o)) for o in odds_list]

        inverse_sum = sum(Decimal('1') / o for o in odds_dec)

        if inverse_sum >= Decimal('1'):
            roi_dec = ((Decimal('1') / inverse_sum) - Decimal('1')) * Decimal('100')
            return {
                "is_surebet": False,
                "inverse_sum": float(inverse_sum),
                "roi_percentage": float(roi_dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "stakes": []
            }

        total_payout = b_dec / inverse_sum
        profit = total_payout - b_dec
        roi = (profit / b_dec) * Decimal('100')

        stakes = []
        for i, o in enumerate(odds_dec):
            stake = b_dec / (o * inverse_sum)
            stake_rounded = stake.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            leg_payout = stake_rounded * o
            stakes.append({
                "leg_index": i,
                "odds": float(o),
                "stake": float(stake_rounded),
                "percentage": float(((stake / b_dec) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "payout": float(leg_payout.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            })

        return {
            "is_surebet": True,
            "bankroll": float(b_dec),
            "inverse_sum": float(inverse_sum.quantize(Decimal('0.00001'), rounding=ROUND_HALF_UP)),
            "profit": float(profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "roi_percentage": float(roi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "stakes": stakes
        }
