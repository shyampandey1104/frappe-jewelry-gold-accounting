"""Jewelry, Gold Bullion & Karat Purity Accounting Engine for Frappe Framework."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class GoldDailyRate(BaseModel):
    rate_24k_per_gram: float
    rate_22k_per_gram: float
    rate_18k_per_gram: float
    silver_per_gram: float
    effective_date: str


class JewelryOrnament(BaseModel):
    item_code: str
    description: str
    karat: int  # 24, 22, 18
    gross_weight_grams: float
    stone_weight_grams: float = 0.0
    wastage_percentage: float = 3.0  # e.g. 3% melting/filing wastage
    making_charge_type: str = "PER_GRAM"  # PER_GRAM or PERCENTAGE
    making_charge_value: float = 450.0  # ₹450/gram or 10%
    hallmark_charge: float = 45.0  # Statutory BIS Hallmark fee


class JewelryAccountingEngine:
    """Calculates precious metal purity, net weight, wastage, and statutory 3% Gold GST."""

    GST_RATE_JEWELRY = 3.0  # Statutory 3% GST on Gold in India (1.5% CGST + 1.5% SGST)

    def __init__(self, daily_rates: GoldDailyRate):
        self.rates = daily_rates

    def calculate_ornament_price(self, item: JewelryOrnament) -> Dict[str, Any]:
        net_gold_weight = max(0.0, item.gross_weight_grams - item.stone_weight_grams)
        billable_gold_weight = net_gold_weight * (1 + (item.wastage_percentage / 100.0))

        # Select rate by karat
        if item.karat == 24:
            rate_per_gram = self.rates.rate_24k_per_gram
        elif item.karat == 22:
            rate_per_gram = self.rates.rate_22k_per_gram
        elif item.karat == 18:
            rate_per_gram = self.rates.rate_18k_per_gram
        else:
            rate_per_gram = self.rates.rate_24k_per_gram * (item.karat / 24.0)

        gold_value = billable_gold_weight * rate_per_gram

        # Making charges
        if item.making_charge_type == "PER_GRAM":
            making_charge = net_gold_weight * item.making_charge_value
        else:
            making_charge = gold_value * (item.making_charge_value / 100.0)

        taxable_value = gold_value + making_charge + item.hallmark_charge
        gst_amount = taxable_value * (self.GST_RATE_JEWELRY / 100.0)
        cgst = gst_amount / 2.0
        sgst = gst_amount / 2.0
        final_price = taxable_value + gst_amount

        return {
            "item_code": item.item_code,
            "karat": f"{item.karat}K",
            "gross_weight": item.gross_weight_grams,
            "net_gold_weight": round(net_gold_weight, 3),
            "billable_weight_with_wastage": round(billable_gold_weight, 3),
            "gold_rate_applied": rate_per_gram,
            "gold_value": round(gold_value, 2),
            "making_charge": round(making_charge, 2),
            "hallmark_fee": item.hallmark_charge,
            "taxable_amount": round(taxable_value, 2),
            "cgst_1_5_pct": round(cgst, 2),
            "sgst_1_5_pct": round(sgst, 2),
            "grand_total": round(final_price, 2),
        }
