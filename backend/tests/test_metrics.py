"""Tests for impact calculation."""

from src.metrics.impact_calculator import ImpactCalculator


def test_calculate_savings():
    calc = ImpactCalculator(energy_per_token_wh=0.0005, wue_l_per_kwh=1.8, pue=1.5)

    savings = calc.calculate_savings(1000)

    assert savings["energy_saved_wh"] == 0.75
    assert savings["water_saved_ml"] == 1.35
    assert savings["carbon_saved_g"] == 0.2925


def test_contextualize():
    calc = ImpactCalculator()

    energy_wh = 750000
    carbon_g = 292500

    context = calc.contextualize(energy_wh, carbon_g)

    assert context["energy_kwh"] == 750.0
    assert context["equivalent_car_km"] > 0
    assert context["equivalent_trees_year"] > 0
