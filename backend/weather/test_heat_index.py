import math
from decimal import Decimal
from unittest import TestCase

from .models import RiskLevel
from .services.heat_index import (
    assess_heat_risk,
    calculate_heat_index_c,
    risk_level_for_heat_index,
    safety_recommendation_for_risk,
)
from .services.open_meteo import InvalidWeatherRequest


class HeatIndexTests(TestCase):
    def test_rothfusz_reference_case_returns_heat_index_in_celsius(self):
        result = calculate_heat_index_c(Decimal('32.2222'), Decimal('70'))

        self.assertAlmostEqual(result, 41.07, places=2)

    def test_heat_index_is_not_applicable_when_simple_estimate_is_below_80_f(self):
        self.assertIsNone(calculate_heat_index_c(25, 50))

    def test_low_humidity_adjustment_is_applied(self):
        adjusted = calculate_heat_index_c(35, 10)
        unadjusted = calculate_heat_index_c(35, 13)

        self.assertLess(adjusted, unadjusted)

    def test_high_humidity_adjustment_is_applied(self):
        adjusted = calculate_heat_index_c(30, 90)
        unadjusted = calculate_heat_index_c(30, 85)

        self.assertGreater(adjusted, unadjusted)

    def test_heat_index_inputs_reject_invalid_types_non_finite_and_bounds(self):
        invalid_inputs = (
            (True, 50),
            (float('nan'), 50),
            (float('inf'), 50),
            (-101, 50),
            (71, 50),
            (30, True),
            (30, -0.1),
            (30, 100.1),
            ('30', 50),
        )
        for temperature, humidity in invalid_inputs:
            with self.subTest(temperature=temperature, humidity=humidity):
                with self.assertRaises(InvalidWeatherRequest):
                    calculate_heat_index_c(temperature, humidity)

    def test_risk_threshold_boundaries(self):
        cases = (
            (26.99, RiskLevel.LOW),
            (27, RiskLevel.CAUTION),
            (31.99, RiskLevel.CAUTION),
            (32, RiskLevel.EXTREME_CAUTION),
            (40.99, RiskLevel.EXTREME_CAUTION),
            (41, RiskLevel.DANGER),
            (53.99, RiskLevel.DANGER),
            (54, RiskLevel.EXTREME_DANGER),
        )
        for heat_index, expected_level in cases:
            with self.subTest(heat_index=heat_index):
                self.assertEqual(
                    risk_level_for_heat_index(heat_index),
                    expected_level,
                )

    def test_risk_classification_handles_not_applicable_and_invalid_values(self):
        self.assertIsNone(risk_level_for_heat_index(None))
        for value in (True, math.nan, -101, 101, '27'):
            with self.subTest(value=value):
                with self.assertRaises(InvalidWeatherRequest):
                    risk_level_for_heat_index(value)

    def test_recommendations_exist_for_all_risk_levels_and_none(self):
        for risk_level in RiskLevel:
            with self.subTest(risk_level=risk_level):
                self.assertTrue(safety_recommendation_for_risk(risk_level))
        self.assertIsNone(safety_recommendation_for_risk(None))
        with self.assertRaises(InvalidWeatherRequest):
            safety_recommendation_for_risk('unknown')

    def test_assessment_returns_consistent_heat_index_risk_and_recommendation(self):
        result = assess_heat_risk(32.2222, 70)

        self.assertEqual(result['heat_index_c'], 41.07)
        self.assertEqual(result['risk_level'], RiskLevel.DANGER)
        self.assertTrue(result['recommendation'])

    def test_assessment_returns_empty_risk_fields_when_not_applicable(self):
        self.assertEqual(
            assess_heat_risk(25, 50),
            {
                'heat_index_c': None,
                'risk_level': None,
                'recommendation': None,
            },
        )
