"""Perfume matching: brand and concentration are mandatory; fuzzy matching only
applies to the name.

Raw title similarity alone can't tell 'Sauvage' apart from 'Sauvage Elixir' or
'Eau Sauvage', or 'Bleu de Chanel EDT' from 'EDP'. So brand and concentration
(EDT/EDP/EDC/Parfum/Extrait/Elixir) are checked as mandatory exact tokens first;
fuzzy matching only runs on whatever's left of the name.

A low-confidence match must never be added to the basket silently. The UI has to
ask for confirmation first.

TODO: normalize the title, split out concentration and brand, enforce the mandatory
match, then fuzzy-match the remainder.
"""
