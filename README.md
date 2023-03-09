A packet of scripts for verifying the compliance of RW and WZ documents. 

WZ is abbreviation of Wydanie Zaopatrzenia in polish (material release receipt). RW is abbreviation of Rozchód Wewnętrzny in polish (goods issue). These are some kind of storage documentation.
In this particular case, RW data comes from scanned paper documents, WZ data comes from excel workbook where each WZ document has been placed on separate sheet. Verification results which show differences between corresponding RW and WZ documents have form of tables displayed on stdout.

Because of confidential data, input and output files are not attached.

A Packet conatins four scripts. Each of them is resposible for part of data processing.

# rwimage2txt.py:
Script uses a tesseract OCR engine library for extracting RW data from scanned documents to text files. Output directory is ./RW_txt/

Usage example:

processing whole jpeg files from ./RW_jpeg/ directory:
>python rwimage2txt.py

processing single or list of jpeg files:
    >python rwimage2txt.py RW_jpeg/Scan_0001.jpg
    or
    >python rwimage2txt.py RW_jpeg/Scan_*.jpg

# decodetxt2rw.py
Script process text files created by rwimage2txt.py script using regular expressions. Results of this process are saved to files  containing json formatted RW data. Output directory is ./RW_json/

Usage example:

processing whole files from ./RW_txt/ directory and print report if --report or -r option is used:
    >python decodetxt2rw.py
    or
    >python decodetxt2rw.py --report

processing single or list of .txt files from specified directory and print report if --report or -r option is used:
    >python rwimage2txt.py -r RW_txt/Scan_0001.txt


# decodexls2wz.py
Script exctracts WZ data from excel workbook containing set of WZ documents. Another excel workbook cantaining assortment list is used for indexing purposes. Results of this process are saved to files containing json formatted WZ data. Output directory is ./WZ_json/

Usage example:
    >python decodexls2wz.py "DWS_xls/asortyment.xls" "DWS_xls/DWSygn.xls


# rwchecker.py
Main script for checking and verifying of set of WZ and RW documents. Script uses input data placed in ./RW_json/ and ./WZ_json/ directories.

Usage example:
results sent to stdout:
    >python rwchecker.py
results sent to output_file.txt     
    >python rwchecker.py > output_file.txt
