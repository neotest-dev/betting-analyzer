from decimal import Decimal, ROUND_HALF_UP


class ROICalculator:
    """High-precision Decimal calculations for Surebet ROI"""

    @staticmethod
    def calculate_surebet_roi(inverse_sum: float) -> float:
        """
        Calculate surebet ROI percentage from inverse odds sum.
        roi = ((1 / inverse_sum) - 1) * 100
        """
        if inverse_sum <= 0:
            return 0.0

        inv_dec = Decimal(str(inverse_sum))
        roi_dec = ((Decimal('1') / inv_dec) - Decimal('1')) * Decimal('100')
        return float(roi_dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
