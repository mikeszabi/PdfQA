# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 09:54:04 2023

@author: Szabi
"""

import os

FILE_DIR=r'./docs'

file_names = [os.path.join(FILE_DIR,f) for f in os.listdir(FILE_DIR) if f.lower().endswith('.pdf')]


from PyPDF2 import PdfReader

for file_name in file_names:

    reader = PdfReader(file_name)
    
    # printing number of pages in pdf file
    print(f"{file_name} : {len(reader.pages)}")
      
    # getting a specific page from the pdf file
    page = reader.pages[0]
      
    # extracting text from page
    text = page.extract_text().replace('\n','')[0:100]
    print(text)


# with fitz.open(file_name) as doc:  # open document
#     text = chr(12).join([page.get_text() for page in doc])
    
# doc = fitz.open(file_name)

# outtext = open("output.txt", "wb")
# outtext.write(page.get_text().encode("utf8"))
# outtext.close()