import glob
import cv2
import pytesseract
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor


RW_RAW_INPUT_FOLDER = "RW_jpeg/"
RW_TEMP_FOLDER = "RW_temp/"
RW_TXT_FOLDER = "RW_txt/"


def get_files(path):
    return glob.glob(os.path.join(path, "Scan_*.jpg"))


def read_raw_file(filename: str):
    try:
        return cv2.imread(filename)
    except FileNotFoundError:
        print("File" + filename + "not found.")
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


def make_data(image):
    custom_config = r"--oem 3 --psm 6 -l pol+osd"
    return pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)


def make_xml(image):
    custom_config = r"--oem 3 --psm 6 -l pol+osd"
    return pytesseract.image_to_alto_xml(image, config=custom_config)


def get_result_name(filename: str):
    f_name = filename.rsplit('/', maxsplit=1)[1]
    return f_name.rsplit('.', maxsplit=1)[0]
    

def process_image(filename: str):
    image = read_raw_file(filename)
    if image is None:
        print("There is a problem with image file", filename)
        return
    grey = get_greyscale(image)
    thresh = thresholding_inv(grey)
    img = remove_horizontal(thresh, thresh)
    img = thresholding_inv(img)
    text = make_txt(img)
    result_fn = get_result_name(filename)
    # tmp_filename = RW_TEMP_FOLDER + result_fn
    # cv2.imwrite(tmp_filename + "img.jpg", img)
    # cv2.imwrite(tmp_filename + "thresh.jpg", thresh)
    txt_filename = os.path.join(RW_TXT_FOLDER, result_fn + ".txt")
    with open(txt_filename, 'w') as stream:
        stream.write(text)

def main():
    input_files = get_files(RW_RAW_INPUT_FOLDER)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(tqdm(pool.map(process_image, input_files), total=len(input_files), desc="Images processing", unit="image")) 
    print("Finished.")


if __name__ == "__main__":
    main()
