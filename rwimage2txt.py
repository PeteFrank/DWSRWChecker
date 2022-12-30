import glob
import cv2
import pytesseract


RW_RAW_INPUT_FOLDER = "/home/piotr/msr/ocr/RW_scan/"
RW_TEMP_FOLDER = "/home/piotr/msr/ocr/RW_temp/"
RW_TXT_FOLDER = "/home/piotr/msr/ocr/RW_txt/"


def get_files(path):
    return glob.glob(path + "*raw600.jpg")


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
    return f_name.rsplit('_', maxsplit=1)[0]


def main():
    input_files = get_files(RW_RAW_INPUT_FOLDER)
    print(input_files)
    for file in input_files:
        image = read_raw_file(file)
        if image is None:
            print("There is a problem with image file", file)
            continue
        grey = get_greyscale(image)
        thresh = thresholding_inv(grey)
        img = remove_horizontal(thresh, thresh)
        img = thresholding_inv(img)
        text = make_txt(img)
        xml_data = make_xml(img)
        result_fn = get_result_name(file)
        tmp_filename = RW_TEMP_FOLDER + result_fn
        cv2.imwrite(tmp_filename + "img.jpg", img)
        # cv2.imwrite(tmp_filename + "thresh.jpg", thresh)
        txt_filename = RW_TXT_FOLDER + result_fn + ".txt"
        with open(txt_filename, 'w') as stream:
            stream.write(text)
        xml_filename = RW_TXT_FOLDER + result_fn + ".xml"
        with open(xml_filename, 'wb') as stream:
            stream.write(xml_data)
        print(txt_filename + " written.")
    print("Finished.")


if __name__ == "__main__":
    main()

    # image = cv2.imread("/home/piotr/msr/ocr/testgimp600.tif")
# image = cv2.imread("out_thresh.jpg")
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Remove horizontal
# horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25,1))
# detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
# cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnts = cnts[0] if len(cnts) == 2 else cnts[1]
# for c in cnts:
#     cv2.drawContours(image, [c], -1, (255,255,255), 2)

# Repair image
# repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,6))
# result = 255 - cv2.morphologyEx(255 - image, cv2.MORPH_CLOSE, repair_kernel, iterations=1)

# custom_config = r"--oem 3 --psm 6 -l pol"
# with open("result.txt", "a") as stream:
#     stream.write(pytesseract.image_to_string(image, config=custom_config))

# cv2.imwrite("lr_thresh.jpg", thresh)
# cv2.imwrite("lr_detected_lines.jpg", detected_lines)
# cv2.imwrite("lr_image.jpg", image)
# cv2.imwrite("lr_result.jpg", result)

# cv2.imshow('thresh', thresh)
# cv2.imshow('detected_lines', detected_lines)
# cv2.imshow('image', image)
# cv2.imshow('result', result)
# cv2.waitKey()
