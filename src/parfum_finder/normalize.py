"""Number parsing and formatting for prices and volumes, plus text folding.

This is the correctness core of the whole app. Parsing is tolerant: both Turkish
(1.250,00) and English (1,250.00) thousands/decimal conventions are recognized.
Formatting is canonical: prices are always printed comma-thousands/dot-decimal,
volumes are always printed dot-decimal.

The stdlib `locale` module is deliberately not used here. It mutates global state
and isn't thread-safe, which is a poor fit for concurrent scraping.

Required test cases: "1.250,00 TL", "1,250.00", "250 TL", "₺1.250", "250,50",
"0,5 ml", "1.5ml", "5 ML", "5cc", "5 cc".
"""

import re
from decimal import Decimal

_NUMBER_PATTERN = re.compile(r"\d[\d.,]*")


def casefold_tr(text: str) -> str:
    """Lower-case text for comparison, without breaking Turkish "İ".

    Python folds "İ" to "i" plus a separate combining dot, so "ORİJİNAL ŞİŞE"
    comes out as "ori̇jinal şi̇şe" and a word written "orijinal şişe" does not
    appear in it. Comparisons against it would silently never match. Mapping that
    one letter first is what makes the two strings comparable.

    Dotless "I" is left to plain casefolding on purpose. Turkish would fold it to
    "ı", which would break the English words that fill these titles, "ORIGINAL"
    among them.
    """
    return text.replace("İ", "i").casefold()


def parse_price(raw: str) -> Decimal:
    """Parse a price string, e.g. '1.250,00 TL' -> Decimal('1250.00').

    Recognizes both Turkish and English separator conventions. Currency
    symbols and codes around the number are ignored, only the digits matter.
    """
    return _parse_number(raw)


def parse_size_ml(raw: str) -> Decimal:
    """Parse a volume string, e.g. '5 ML' -> Decimal('5'), '0,5 ml' -> Decimal('0.5').

    'cc' is treated as equivalent to 'ml', so the unit text is ignored the
    same way currency symbols are ignored in parse_price.
    """
    return _parse_number(raw)


def format_price(v: Decimal) -> str:
    """Format a price for display (comma-thousands, dot-decimal).

    Decimal('1250') -> '1,250.00 ₺'.
    """
    return f"{v:,.2f} ₺"


def format_ml(v: Decimal) -> str:
    """Format a volume for display (dot-decimal): Decimal('1.5') -> '1.5 ml'."""
    return f"{v.normalize():f} ml"


def _parse_number(raw: str) -> Decimal:
    """Pull the numeric value out of a string that may carry a currency or unit label.

    Turkish sites write "1.250,00" (dot groups thousands, comma is the decimal
    point); English-formatted feeds write "1,250.00" (the roles are swapped).
    When both separators show up, whichever one appears last is the decimal
    point. When only one shows up, a run of exactly three digits after it is
    treated as a thousands group instead of a fraction, since prices and
    volumes here never carry three fractional digits.
    """
    match = _NUMBER_PATTERN.search(raw)
    if match is None:
        raise ValueError(f"no number found in {raw!r}")
    number = match.group()

    has_dot = "." in number
    has_comma = "," in number

    if has_dot and has_comma:
        if number.rindex(",") > number.rindex("."):
            decimal_sep, group_sep = ",", "."
        else:
            decimal_sep, group_sep = ".", ","
    elif has_comma:
        decimal_sep, group_sep = _classify_single_separator(number, ",")
    elif has_dot:
        decimal_sep, group_sep = _classify_single_separator(number, ".")
    else:
        decimal_sep, group_sep = "", ""

    if group_sep:
        number = number.replace(group_sep, "")
    if decimal_sep and decimal_sep != ".":
        number = number.replace(decimal_sep, ".")

    return Decimal(number)


def _classify_single_separator(number: str, sep: str) -> tuple[str, str]:
    """Decide whether a lone separator marks a fraction or a thousands group.

    Returns a (decimal_sep, group_sep) pair, one of which is always empty.
    """
    fragment = number.rsplit(sep, 1)[1]
    if len(fragment) == 3:
        return "", sep
    return sep, ""
