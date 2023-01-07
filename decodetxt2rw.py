import re
import os
import glob
import json


RW_TXT_FOLDER = "RW_txt/"
RW_JSON_FOLDER = "RW_json/"

PATTERN_RW = r"RW/U\d+/22"
PATTERN_DWS = r"DWS\s?\d\d\d/22"
PATTERN_WZ = r"WZ\s?\d\d\d/\d\d/22/6"
PATTERN_INDEX = r"\d\d\d\d\sJ"
PATTERN_COUNT = r"\d+\s?SZT"
# PATTERN_PRIZES = r"[0-9]+[\.,][0-9]+\s[0-9]*.*[0-9]+[\.,][0-9]+"
PATTERN_PRIZES = r"[0-9]*\s*[0-9]+[\.,][0-9][0-9]"


def get_text_from_file(filename: str) -> str:
    try:
        with open(filename, "r", encoding='UTF-8') as stream:
            text = stream.read()
    except:
        text = ''
    return text


def get_text_filename_list(path: str) -> list[str]:
    return glob.glob(os.path.join(path, "*.txt"))


def get_json_file_name(out_dir: str, out_number: str) -> str:
    return os.path.join(out_dir, out_number.replace("/","_")+".json")


def save_json(_dict: dict, filename: str):
    with open(filename, "w") as json_file:
        json.dump(_dict, json_file)


def decode_rw_number(source: str) -> str:
    rw_number = re.findall(PATTERN_RW, source)
    try:
        return rw_number[0]
    except:
        return None


def decode_dws_numbers(source: str) -> list[str]:
    tmp = re.findall(PATTERN_DWS, source)
    return [re.findall(r"\d\d\d/22", tmp_item)[0] for tmp_item in tmp]


def decode_wz_numbers(source: str) -> list[str]:
    tmp = re.findall(PATTERN_WZ, source)
    return [re.findall(r"\d+/\d\d/22/6", tmp_item)[0] for tmp_item in tmp]


def is_index(source_line: str) -> bool:
    return len(re.findall(PATTERN_INDEX, source_line)) > 0


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


def get_count(source_line: str) -> int:
    try:
        return get_numeric_int(re.findall(PATTERN_COUNT, source_line)[0])
    except IndexError:
        return 0
    

def get_prizes(source_line: str) -> list[float, float]:
    try:
        prizes_list = re.findall(PATTERN_PRIZES, source_line)
        if len(prizes_list) == 2:
           return [get_numeric_float(n) for n in prizes_list]
        else:
            return [1, 0]
    except IndexError or ValueError:
        return [1, 0]


def decode_item(source_line: str) -> dict:
    item = {}
    item["index"] = get_index(source_line)
    item["quantity"] = get_count(source_line)
    item["prizes"] = get_prizes(source_line)
    item["quantity_by_prizes"] = item["prizes"][1] / item["prizes"][0]
    item["verified"] = item["count"] == item["count_by_prizes"]
    return item


def compose_rw(rw_raw_text: str) -> dict:
    rw_item = {}
    rw_item["RW_document"] = decode_rw_number(rw_raw_text)
    rw_item["DWS_documents"] = decode_dws_numbers(rw_raw_text)
    rw_item["WZ_documents"] = decode_wz_numbers(rw_raw_text)
    rw_item["items"] = [decode_item(line) for line in rw_raw_text.splitlines() if is_index(line)]
    return rw_item


def main():
    files_list = get_text_filename_list(RW_TXT_FOLDER)
    for file in files_list:
        rw_dict = compose_rw(get_text_from_file(file))
        save_json(rw_dict, get_json_file_name(RW_JSON_FOLDER, rw_dict["RW_document"]))


if __name__ == "__main__":
    main()
