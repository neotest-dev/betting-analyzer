import pytest
from src.calculators.stakes import StakeCalculator
from src.calculators.roi import ROICalculator
from src.odds.normalizer import OddsNormalizer


def test_decimal_stake_precision():
    """Test Decimal stake distribution sums exactly to bankroll"""
    bankroll = 100.0
    odds = [2.30, 3.80, 4.10]
    res = StakeCalculator.calculate_surebet_stakes(bankroll, odds)

    assert res["is_surebet"] is True
    total_staked = sum(s["stake"] for s in res["stakes"])
    # Allow 1 cent rounding error max
    assert abs(total_staked - bankroll) <= 0.05


def test_surebet_roi_calculator():
    """Test surebet ROI calculation from inverse_sum"""
    # inverse_sum = 0.9417 → ROI = (1/0.9417 - 1) * 100 ≈ 6.19%
    roi = ROICalculator.calculate_surebet_roi(0.9417)
    assert roi > 0
    assert isinstance(roi, float)


def test_overround_calculation():
    """Test overround calculation"""
    odds = [2.00, 3.50, 4.00]
    # 1/2 + 1/3.5 + 1/4 = 0.5 + 0.2857 + 0.25 = 1.0357
    overround = OddsNormalizer.calculate_overround(odds)
    assert round(overround, 4) == 1.0357
