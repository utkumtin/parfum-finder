"""Number parsing and formatting for prices and volumes.

This is the correctness core of the whole app. Parsing is tolerant: both Turkish
(1.250,00) and English (1,250.00) thousands/decimal conventions are recognized.
Formatting is canonical: prices are always printed comma-thousands/dot-decimal,
volumes are always printed dot-decimal.

The stdlib `locale` module is deliberately not used here. It mutates global state
and isn't thread-safe, which is a poor fit for concurrent scraping.

Required test cases: "1.250,00 TL", "1,250.00", "250 TL", "₺1.250", "250,50",
"0,5 ml", "1.5ml", "5 ML", "5cc", "5 cc".
"""

from decimal import Decimal


def parse_price(raw: str) -> Decimal:
    """Parse a price string, e.g. '1.250,00 TL' -> Decimal('1250.00').

    Recognizes both Turkish and English separator conventions.
    """
    raise NotImplementedError


def parse_size_ml(raw: str) -> Decimal:
    """Parse a volume string, e.g. '5 ML' -> Decimal('5'), '0,5 ml' -> Decimal('0.5').

    'cc' is treated as equivalent to 'ml'.
    """
    raise NotImplementedError


def format_price(v: Decimal) -> str:
    """Format a price for display (comma-thousands, dot-decimal).

    Decimal('1250') -> '1,250.00 ₺'.
    """
    raise NotImplementedError


def format_ml(v: Decimal) -> str:
    """Format a volume for display (dot-decimal): Decimal('1.5') -> '1.5 ml'."""
    raise NotImplementedError
