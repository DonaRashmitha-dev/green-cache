"""Environmental impact calculator for cache hits."""

import structlog

from src.config import settings

logger = structlog.get_logger(__name__)

DEFAULT_ENERGY_PER_TOKEN_WH = 0.0005
CARBON_INTENSITY_KG_PER_KWH = 0.39
DEFAULT_WUE_L_PER_KWH = 1.8
DEFAULT_PUE = 1.5
CO2_PER_KM_CAR = 0.120
CO2_PER_TREE_YEAR = 22.0


class ImpactCalculator:
    """Calculate environmental impact savings from cache hits."""

    def __init__(
        self,
        energy_per_token_wh: float | None = None,
        wue_l_per_kwh: float | None = None,
        pue: float | None = None,
    ) -> None:
        self._energy_per_token_wh = energy_per_token_wh or settings.energy_per_token_wh
        self._wue_l_per_kwh = wue_l_per_kwh or settings.wue_l_per_kwh
        self._pue = pue or settings.pue

        logger.info(
            "impact_calculator_initialized",
            energy_per_token_wh=self._energy_per_token_wh,
            wue_l_per_kwh=self._wue_l_per_kwh,
            pue=self._pue,
        )

    def calculate_savings(self, tokens_saved: int) -> dict[str, float]:
        if tokens_saved <= 0:
            return {"energy_saved_wh": 0.0, "water_saved_ml": 0.0, "carbon_saved_g": 0.0}

        energy_wh = tokens_saved * self._energy_per_token_wh * self._pue
        energy_kwh = energy_wh / 1000.0
        water_ml = energy_kwh * self._wue_l_per_kwh * 1000.0
        carbon_g = energy_kwh * CARBON_INTENSITY_KG_PER_KWH * 1000.0

        return {
            "energy_saved_wh": round(energy_wh, 6),
            "water_saved_ml": round(water_ml, 6),
            "carbon_saved_g": round(carbon_g, 6),
        }

    def contextualize(self, total_energy_wh: float, total_carbon_g: float) -> dict[str, float]:
        carbon_kg = total_carbon_g / 1000.0
        return {
            "equivalent_car_km": round(carbon_kg / CO2_PER_KM_CAR, 4),
            "equivalent_trees_year": round(carbon_kg / CO2_PER_TREE_YEAR, 6),
            "energy_kwh": round(total_energy_wh / 1000.0, 6),
        }

    def get_explanation(self) -> str:
        return f"""Environmental Impact Estimation Methodology
=============================================
These are APPROXIMATIONS based on published research.

Energy Model:
  - Base energy per token: {self._energy_per_token_wh} Wh/token
  - PUE (facility overhead): {self._pue}x

Water Model:
  - WUE (Water Usage Effectiveness): {self._wue_l_per_kwh} L/kWh

Carbon Model:
  - Grid carbon intensity: {CARBON_INTENSITY_KG_PER_KWH} kg CO2/kWh

Contextual Equivalents:
  - Car: {CO2_PER_KM_CAR} kg CO2/km
  - Tree: {CO2_PER_TREE_YEAR} kg CO2/year
"""


_impact_calculator: ImpactCalculator | None = None


def get_impact_calculator() -> ImpactCalculator:
    global _impact_calculator
    if _impact_calculator is None:
        _impact_calculator = ImpactCalculator()
    return _impact_calculator
