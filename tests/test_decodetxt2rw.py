import pytest

import decodetxt2rw as dt2rw


testdata = [
    ("-RW/U00054/22", "RW/U00054/22"),
    ("Rw/U00018/23 ", "RW/U00018/23"),
]

@pytest.mark.parametrize("input, expected",testdata)
def test_decode_rw_number(input, expected):
    assert dt2rw.decode_rw_number(input) == expected


@pytest.mark.parametrize("input, expected", [
    ("Wz123/12/23/6", ["123/12/23/6"]),
    ("wz 123/01/22/6 , WZ234/01/23/6", ["123/01/22/6", "234/01/23/6"]),
    ("234/06/23/6",[]),
])
def test_decode_wz_numbers(input, expected):
    assert dt2rw.decode_wz_numbers(input) == expected


@pytest.mark.parametrize("input, expected", [
    ("TRAFIC - SŁUPSK - WZ 244/04/22/6; DWS 060/22", ["060/22"]),
    ("dws 123/23 , DWs234/23, 090/22", ["123/23", "234/23"]),
    ("234/23",[]),
])
def test_decode_dws_numbers(input, expected):
    assert dt2rw.decode_dws_numbers(input) == expected


@pytest.mark.parametrize("input, expected", [
    ("20 ŻELKOWA KOLONII: SIEDLECKA DW803 EEE", False),
    ('—”) 1815 J00072PODK LATARNIA MONDIAL FUTURLED3 3x300 230V R-Y-G OGÓL 4 SZT 775.00 3 100.00', True),
    ('—”) 1885 100072PODK LATARNIA MONDIAL FUTURLED3 3x300 230V R-Y-G OGÓL 4 SZT 775.00 3 100.00', True),
    ("2167 J00171ANOD PŁYTA PW-95 2 SZT 24.60 49.20", True),
])
def test_is_index(input, expected):
    assert dt2rw.is_index(input) == expected


@pytest.mark.parametrize("input, expected", [
    ('—”) 1815 J00072PODK LATARNIA MONDIAL FUTURLED3 3x300 230V R-Y-G OGÓL 4 SZT 775.00 3 100.00', 1815),
    ("2167 J00171ANOD PŁYTA PW-95 2 SZT 24.60 49.20", 2167),
    ("m. 2160 UCHWYT UW-108,CYBANT M12x108x149 gwint 50 oci2um 4 SZT 5.83 23.32", 2160),
    ('—”) 1885 100072PODK LATARNIA MONDIAL FUTURLED3 3x300 230V R-Y-G OGÓL 4 SZT 775.00 3 100.00', 1885),
])
def test_get_index(input, expected):
    assert dt2rw.get_index(input) == expected


@pytest.mark.parametrize("input, expected", [
    ('—”) 1815 J00072PODK LATARNIA MONDIAL FUTURLED3 3x300 230V R-Y-G OGÓL 4 SZT 775.00 3 100.00', 4),
    ("2167 J00171ANOD PŁYTA PW-95 2 SZT 24.60 49.20", 2),
    ("m. 2160 UCHWYT UW-108,CYBANT M12x108x149 gwint 50 oci2um 4SZT 5.83 23.32", 4),
    ("- 2405 LISTWA LPC-FUT-2*200-595-496 123 SZT 14.00 14.00", 123),
])
def test_get_count(input, expected):
    assert dt2rw.get_count(input) == expected
