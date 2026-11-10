"""Numerical software tests only. These are not customer cases or tariff advice."""
import unittest
from decimal import Decimal
from review_motor_quotes import review_rows


def test_input(**changes):
    # Explicit test inputs, not an insurer's commercial quotation.
    row = dict(record_id="TEST-ONLY", insurer="Software test", quote_reference="UNIT-TEST",
               vehicle_use="Test input", sum_insured_tzs="10000000", rate_percent="3.5",
               minimum_base_premium_tzs="250000", quoted_base_premium_tzs="350000")
    row.update(changes)
    return row


class QuoteReviewTests(unittest.TestCase):
    def test_sum_insured_controls_the_rate_component(self):
        base = review_rows([test_input()])[0]
        doubled = review_rows([test_input(sum_insured_tzs="20000000", quoted_base_premium_tzs="700000")])[0]
        self.assertEqual(Decimal(base["rate_component_tzs"]), Decimal("350000"))
        self.assertEqual(Decimal(doubled["rate_component_tzs"]), Decimal("700000"))
        self.assertEqual(doubled["review_status"], "Arithmetic matches inputs")

    def test_confirmed_minimum_applies_at_low_value(self):
        result = review_rows([test_input(sum_insured_tzs="1000000", quoted_base_premium_tzs="250000")])[0]
        self.assertEqual(Decimal(result["expected_base_premium_tzs"]), Decimal("250000"))

    def test_unknown_minimum_is_not_treated_as_zero(self):
        result = review_rows([test_input(minimum_base_premium_tzs="")])[0]
        self.assertEqual(result["expected_base_premium_tzs"], "")
        self.assertEqual(result["review_status"], "Needs confirmation")

    def test_entered_zero_minimum_is_distinct_from_unknown(self):
        result = review_rows([test_input(minimum_base_premium_tzs="0")])[0]
        self.assertEqual(result["review_status"], "Arithmetic matches inputs")

    def test_duplicate_record_ids_are_both_flagged(self):
        results = review_rows([test_input(), test_input()])
        self.assertTrue(all("Repeated record ID" in row["questions"] for row in results))

    def test_missing_or_nonfinite_inputs_do_not_pass(self):
        for field, value in [("sum_insured_tzs", ""), ("sum_insured_tzs", "0"),
                             ("rate_percent", "NaN"), ("quoted_base_premium_tzs", "Infinity")]:
            with self.subTest(field=field, value=value):
                result = review_rows([test_input(**{field: value})])[0]
                self.assertEqual(result["review_status"], "Needs confirmation")

    def test_decimal_calculation_and_tolerance_boundary(self):
        row = test_input(sum_insured_tzs="1234567", rate_percent="2.75",
                         minimum_base_premium_tzs="0", quoted_base_premium_tzs="33950.60")
        exact = review_rows([row])[0]
        allowed = review_rows([row], tolerance=Decimal("0.01"))[0]
        self.assertEqual(Decimal(exact["difference_tzs"]), Decimal("0.0075"))
        self.assertEqual(exact["review_status"], "Needs confirmation")
        self.assertEqual(allowed["review_status"], "Arithmetic matches inputs")


if __name__ == "__main__":
    unittest.main()
