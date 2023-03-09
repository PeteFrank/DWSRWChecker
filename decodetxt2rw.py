import os
import glob
import json
from operator import itemgetter
import re

import click
from tqdm import tqdm
from globals import RW_TXT_FOLDER,\
                    RW_JSON_FOLDER


PATTERN_RW = r"RW/U\d+/2[0-9]"
PATTERN_DWS = r"(?<=DWS)\s?\d\d\d/2[0-9]"
PATTERN_WZ = r"(?<=WZ)\s?\d\d\d/\d\d/2[0-9]/6"
PATTERN_INDEX = r"[0-9]{4}\s"
PATTERN_COUNT = r"\d+\s?SZT"


def get_files(path: str) -> list:
    return glob.glob(path)


def test_and_touch_dir(dir_name: str) -> None:
    if not os.path.exists(os.path.join(dir_name)):
        os.mkdir(os.path.join(dir_name))


def get_text_from_file(filename: str) -> str:
    try:
        with open(filename, "r", encoding='utf-8') as stream:
            text = stream.read()
    except:
        text = ''
    return text


def get_json_file_name(out_dir: str, out_number: str) -> str:
    return os.path.join(out_dir, out_number.replace("/","_")+".json")


def save_json(_dict: dict, filename: str):
    with open(filename, "w", encoding='utf-8') as json_file:
        json.dump(_dict, json_file)


def decode_rw_number(source: str) -> str:
    rw_number = re.findall(PATTERN_RW, source, re.IGNORECASE)
    try:
        return rw_number[0].upper()
    except IndexError:
        return None


def decode_dws_numbers(source: str) -> list[str]:
    dws = re.findall(PATTERN_DWS, source, re.IGNORECASE)
    try:
        return [dws_item.lstrip().upper() for dws_item in dws]
    except IndexError:
        return []


def decode_wz_numbers(source: str) -> list[str]:
    wz = re.findall(PATTERN_WZ, source, re.IGNORECASE)
    try:
        return[wz_item.lstrip().upper() for wz_item in wz]    
    except IndexError:
        return []


def is_index(source_line: str) -> bool:
    return re.search(PATTERN_INDEX, source_line) is not None


def get_numeric_int(input_str: str) -> int:
    return int(re.findall(r"\d+", input_str)[0])


def get_numeric_float(input_str: str) -> float:
    temp = input_str.replace(' ','').replace(',','.')
    return float(temp)


def get_index(source_line: str) -> int:
    try:
        return get_numeric_int(re.findall(PATTERN_INDEX, source_line)[0])
    except IndexError:
        return 0


def item_lines_generator(raw_text: str) -> str:
    tmp = raw_text.splitlines()
    length = len(tmp)
    i = 0
    while not re.search(r"INDEKS|NAZWA|CENA", tmp[i]) and i<length: i += 1
    while i<length:
        if is_index(tmp[i]):
            yield tmp[i]
        i += 1


def get_count(source_line: str) -> int:
    try:
        return get_numeric_int(re.findall(PATTERN_COUNT, source_line)[0])
    except IndexError:
        return 0
    

def decode_item(source_line: str) -> dict:
    item = {}
    item["index"] = get_index(source_line)
    item["quantity"] = get_count(source_line)
    return item


def compose_rw(rw_raw_text: str) -> dict:
    rw_item = {}
    rw_item["RW_document"] = decode_rw_number(rw_raw_text)
    rw_item["DWS_documents"] = decode_dws_numbers(rw_raw_text)
    rw_item["WZ_documents"] = decode_wz_numbers(rw_raw_text)
    rw_item["items"] = [decode_item(line) for line in item_lines_generator(rw_raw_text)]
    return rw_item


def verify_rw(rw : dict, file: str) -> dict:
    result = {}
    result["RW_document"] = rw["RW_document"]
    result["DWS_documents"] = "OK" if len(rw["DWS_documents"])>0 else "NO DWS"
    result["WZ_documents"] = "OK" if len(rw["WZ_documents"])>0 else "NO WZ"
    result["items"] = len(rw["items"]) if len(rw["items"])>0 else "NO ITEMS"
    result["filename"] = file
    return result


def print_report(report: list) -> str:
    output = "Dokument RW   Dokumenty DWS  Dokumenty WZ  POZYCJI  Z PLIKU\n"
    for item in sort_report(report):
        output += "{:12}  {:^13}  {:^12}  {:>7}  {}\n".format(
            item["RW_document"], item["DWS_documents"], item["WZ_documents"], item["items"], item["filename"]
        )
    return output

def sort_report(report: list) -> list:
    return sorted(report, key=itemgetter("RW_document"))


@click.command()
@click.option("--report", "-r", "_report", is_flag=True, show_default=True, default=False, help="Wyświetla raport przetwarzania.")
@click.argument("filenames", nargs=-1, required=False)
def main(_report: bool, filenames: list):
    """
    Program formatuje pliki tekstowe RW na pliki w formacie json.
    Gdy wywołany bez argumentów, przetwarza wszystkie pliki txt z podkatalogu RW_txt a pliki wynikowe zapisuje w podkatalogu RW_json.
    Jako argumenty wywołania wprowadza się nazwy plików do przetwarzania.
    Opcja -r lub --report powoduje wyświetlenie raportu z przetwarzania plików.\n
    Przykład:\n
    >python decodetxt2rw.py       <- przetwarza wszystkie pliki\n
    >python decodetxt2rw.py --report      <- przetwarza wszystkie pliki i wyświetla raport.\n
    >python rwimage2txt.py -r RW_txt/Scan_0001.txt   <- przetwarza tylko konkretny plik i wyświetla raport.\n
    v1.0.0
    """
    if len(filenames) > 0:
        files_list = []
        for filename in filenames:
            files_list.extend(get_files(filename))
    else:
        test_and_touch_dir(RW_TXT_FOLDER)
        files_list = get_files(os.path.join(RW_TXT_FOLDER, "*.txt"))
    report = []
    test_and_touch_dir(RW_JSON_FOLDER)
    t = tqdm(total=len(files_list), unit=" RW", desc="Przetwarzanie RW")
    for file in files_list:
        raw_text = get_text_from_file(file)
        if raw_text == '':
            print(f"\n\n\n\nPlik {file} nie zawiera poprawnych danych.")
        rw_dict = compose_rw(raw_text)
        save_json(rw_dict, get_json_file_name(RW_JSON_FOLDER, rw_dict["RW_document"]))
        report.append(verify_rw(rw_dict, file)) 
        t.update(n=1)
    t.close()
    if _report:
        print(print_report(report))
        print(f"Razem przetworzonych dokumentów RW: {len(files_list)}")


if __name__ == "__main__":
    main()
