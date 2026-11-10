"""Unit tests for JewelryAccountingEngine."""

from jewelry.engine import JewelryAccountingEngine, GoldDailyRate, JewelryOrnament


def test_gold_ornament_pricing():
    rates = GoldDailyRate(
        rate_24k_per_gram=7800.0,
        rate_22k_per_gram=7150.0,
        rate_18k_per_gram=5850.0,
        silver_per_gram=92.0,
        effective_date="2026-11-10",
    )
    engine = JewelryAccountingEngine(rates)

    necklace = JewelryOrnament(
        item_code="JW-NCK-01",
        description="22K Floral Gold Necklace",
        karat=22,
        gross_weight_grams=25.5,
        stone_weight_grams=1.5,  # Net gold = 24.0g
        wastage_percentage=2.5,
        making_charge_type="PER_GRAM",
        making_charge_value=400.0,
    )

    res = engine.calculate_ornament_price(necklace)
    assert res["net_gold_weight"] == 24.0
    assert res["gold_rate_applied"] == 7150.0
    assert res["making_charge"] == (24.0 * 400.0)
    assert res["cgst_1_5_pct"] > 0
    assert res["grand_total"] > res["taxable_amount"]
