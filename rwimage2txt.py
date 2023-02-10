from concurrent.futures import ThreadPoolExecutor
import glob
import os

import click
import cv2
import pytesseract
from tqdm import tqdm

from decodetxt2rw import get_files, test_and_touch_dir
from globals import RW_RAW_INPUT_FOLDER, \
                    RW_TEMP_FOLDER, \
                    RW_TXT_FOLDER


def read_raw_file(filename: str):
    try:
        return cv2.imread(filename)
    except FileNotFoundError:
        print("Plik" + filename + "nie został znaleziony.")
        return None


def get_greyscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def thresholding_inv(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def remove_horizontal(image, thresh):
    img = image.copy()
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        # cv2.drawContours(image, [c], -1, (255, 255, 255), 2)
        cv2.drawContours(img, [c], -1, (0, 0, 0), 6)
    return img


def make_txt(image):
    custom_config = r"--oem 3 --psm 6 -l pol+osd"
    return pytesseract.image_to_string(image, config=custom_config)


def get_result_name(filename: str):
    f_name = filename.rsplit('/', maxsplit=1)[1]
    return f_name.rsplit('.', maxsplit=1)[0]
    

def process_image(filename: str):
    image = read_raw_file(filename)
    if image is None:
        print("Wystąpił problem z plikiem obrazu ", filename)
        return
    grey = get_greyscale(image)
    thresh = thresholding_inv(grey)
    img = remove_horizontal(thresh, thresh)
    img = thresholding_inv(img)
    text = make_txt(img)
    result_fn = get_result_name(filename)
    txt_filename = os.path.join(RW_TXT_FOLDER, result_fn + ".txt")
    with open(txt_filename, 'w', encoding="utf-8") as stream:
        stream.write(text)

@click.command()
@click.argument("filenames", nargs=-1, required=False)
def main(filenames: list):
    """
    Program przetwarza zeskanowane pliki RW w formacie jpg do plików tekstowych.\n
    Gdy wywołany bez argumentów, przetwarza wszystkie pliki jpg z podkatalogu RW_jpeg a pliki wynikowe zapisuje w podkatalogu RW_txt.
    Jako argumenty wywołania wprowadza się nazwy plików do przetwarzania.\n
    Przykład:\n
    >python rwimage2txt.py       <- przetwarza wszystkie pliki\n
    >python rwimage2txt.py RW_jpeg/Scan_0001.jpg   <- przetwarza tylko konkretny plik.\n
    v1.0.0
    """
    if len(filenames) > 0:
        input_files = []
        for filename in filenames:
            input_files.extend(get_files(filename))
    else:
        test_and_touch_dir(RW_RAW_INPUT_FOLDER)
        input_files = get_files(os.path.join(RW_RAW_INPUT_FOLDER, "*.jp*g"))
    test_and_touch_dir(RW_TXT_FOLDER)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(tqdm(pool.map(process_image, input_files), total=len(input_files), desc="Przetwarzanie obrazu", unit="obraz")) 
    print("Zakończono.")


if __name__ == "__main__":
    main()
