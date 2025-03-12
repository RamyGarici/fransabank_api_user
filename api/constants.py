from decimal import Decimal

PLAFONDS_CARTES = {
    "VISA": {"paiement": Decimal("5000.00"), "retrait": Decimal("2000.00")},
    "MASTERCARD": {"paiement": Decimal("5500.00"), "retrait": Decimal("2200.00")},
    "VISA_PLATINUM": {"paiement": Decimal("10000.00"), "retrait": Decimal("5000.00")},
    "MASTERCARD_ELITE": {"paiement": Decimal("12000.00"), "retrait": Decimal("6000.00")},
    "AMEX": {"paiement": Decimal("15000.00"), "retrait": Decimal("7000.00")},
    "AMEX_GOLD": {"paiement": Decimal("20000.00"), "retrait": Decimal("10000.00")},
}