import os
import re
import sys

import click
from tqdm import tqdm
import xlrd

from decodetxt2rw import test_and_touch_dir, get_json_file_name, save_json
from globals import DWS_XLS_FOLDER, \
                    WZ_JSON_FOLDER


def get_assortment(xls_book: xlrd.book.Book, names_col_number=3, indexes_col_number=12) -> dict:
    a_sheet = xls_book.sheet_by_name("Asortyment")
    names = a_sheet.col_values(names_col_number)[5:]
    indexes = a_sheet.col_values(indexes_col_number)[5:]
    return dict(zip(names, indexes))


def get_xls_book(xls_file_name: str) -> xlrd.book.Book:
    book = xlrd.open_workbook(xls_file_name)
    if isinstance(book,xlrd.book.Book):
        return book
    else:
        raise xlrd.biffh.XLRDError


def get_dws_sheet_list(xls_book: xlrd.book.Book) -> list:
    dws_list = xls_book.sheet_names()
    return [item for item in dws_list if re.fullmatch(r"\d\d\d_\d\d", item) is not None]


def get_dws_sheet(xls_book: xlrd.book.Book, sheet_name: str) -> xlrd.sheet.Sheet:
    return xls_book.sheet_by_name(sheet_name)


def get_count_of_wz(dws_sheet: xlrd.sheet.Sheet, col_number=8, start_row=41) -> int:
    row_number = start_row
    number_of_wz = 0
    while  row_number<dws_sheet.nrows:
        if dws_sheet.cell_value(row_number,col_number) == "Liczba dokumentów WZ :":
            number_of_wz = int(dws_sheet.cell_value(row_number,col_number+1))
            break
        row_number +=1
    return number_of_wz


def get_wz_number(row_items: list) -> str:
    if re.fullmatch(r"\d\d\d/[0-1][0-9]/2[0-9]/6", row_items[-2]) is not None:
        return row_items[-2]
    else:
        return ""


def get_wz_start(dws_sheet: xlrd.sheet.Sheet):
    wz_count = get_count_of_wz(dws_sheet)
    wz_mark_col = dws_sheet.col_values(11, 0)
    count = 0
    i = 0
    while count < wz_count:
        while wz_mark_col[i] != "Wz":
            i += 1
        yield i
        i += 1
        count += 1


def compose_wz_item(assortment_dict: dict, item_name: str, item_count: int) -> dict:
    wz_item = {}
    wz_item["index"] = int(assortment_dict.get(item_name, 0))
    wz_item["name"] = item_name
    wz_item["quantity"] = item_count
    return wz_item


def get_wz_content(assortment_dict: dict, dws_sheet: xlrd.sheet.Sheet, start_row=49, start_col=6, end_col=15) -> dict:
    wz_content_list = []
    sr = start_row
    row = dws_sheet.row_values(sr,start_col, end_col)
    while row[-1]!="EOWZ":
        try:
            wz_tmp_number = get_wz_number(row)
            if len(wz_tmp_number) > 0:
                wz_number = wz_tmp_number
            count = int(row[-1])
            wz_content_list.append(compose_wz_item(assortment_dict, str(row[1]), count))
        except ValueError:
            pass
        sr += 1
        row = dws_sheet.row_values(sr,start_col, end_col)
    result = {}
    result["WZ_number"] = wz_number
    result["DWS_number"] = dws_sheet.name.replace('_', '/')
    result["items"] = wz_content_list
    return result


@click.command()
@click.argument("assortment-xls-file", nargs=1)
@click.argument("dws-xls-file", nargs=1)
def main(assortment_xls_file: str, dws_xls_file: str):
    """
    Program rozpakowuje WZty dyspozycji DWSygn do plików w formacie json (do podkatalogu WZ_json/). 
    Argumenty:\n
        assortment-xls-file: plik w formacie xls zawierający asortyment DWSygn z przypisanymi indeksami magazynowymi.\n
        dws-xls-file: plik w formacie xls zawierający dyspozycje DWSygn oraz dokumenty WZ\n
    Przykład:\n
    >python decodexls2wz.py "DWS_xls/asortyment.xls" "DWS_xls/DWSygn.xls"\n
    v1.0.0
    """
    print("Wczytanie listy asortymentu...", end="")
    try:
        assortment_book = get_xls_book(os.path.join(assortment_xls_file))
    except Exception as e:
        print(f"\nBłąd podczas wczytywania listy. {e}")
        sys.exit(1)
    else:
        assortment_dict = get_assortment(assortment_book)
        print("gotowe.")
    print("Wczytywanie listy DWSygn...", end="")
    try:
        dws_book = get_xls_book(os.path.join(dws_xls_file))
    except Exception as e:
        print(f"\nBłąd podczas wczytywania listy. {e}")
        sys.exit(1)
    else:
        dws_list = get_dws_sheet_list(dws_book)
        print("gotowe.")
    test_and_touch_dir(WZ_JSON_FOLDER)
    t = tqdm(total=len(dws_list), unit=" DWS", desc="Rozpakowywanie WZ")
    for dws_name in dws_list:
        dws_sheet = get_dws_sheet(dws_book, dws_name)
        wz_list = [get_wz_content(assortment_dict, dws_sheet, start_row=sr) for sr in get_wz_start(dws_sheet)]
        for wz in wz_list:
            save_json(wz, get_json_file_name(WZ_JSON_FOLDER,"WZ_"+wz["WZ_number"]))
        t.update(n=1)
    t.close()


if __name__ == "__main__":
    main()
    