import json,os,ocrmypdf
import pdfplumber
import re
from collections import namedtuple
import pandas as pd

Line= namedtuple("Line","Doctype Reference Designation Qty Unitprice TotalCHF Sales")

#  All Used regex 
header_re= re.compile(r"(^[A-Z][a-z][\w\s]*[:.][^0])(?<!Mr\.\s)")
desc_re=re.compile(r"(\b([A-Z]+ D|[A-Z]+)\b)([A-Z\s]+)")
ext_re=re.compile(r"(^[A-Z\a-z\d]+\.\d{3}\.\d{3}\.[A-Z0-9]{2})(.*[A-Z])")
num_re=re.compile(r"[0-9\s.]+[0-9\s.]220$")
discount_re= re.compile(r"([A-Za-z\s]+)(.\d+\.\d)")

def extract_key_value_pairs(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        # Extract text from each page
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    # Split the extracted text into lines
    lines = text.split("\n")

    # Initialize variables
    header_data = {}
    table_data = []

    # Extract key-value pairs
    for line in lines:  
        work=desc_re.search(line)
        if work:
            Ref,Designation=work.group(1),work.group(3)
    
        ext=ext_re.search(line)
        if ext:
           Ref,Designation=ext.group(1),ext.group(2)
           
        elif line.startswith("Work"):
            doctype="Work"
        elif line.startswith("Exterior parts"):
            doctype="Exterior parts"

        # Check if it's a key-value pair in the header section
        elif header_re.search(line) and not num_re.search(line):
            key, value = re.split("[.:]",line)
            header_data[key.strip()] = value.strip()
        elif discount_re.search(line) and not num_re.search(line):
            key=discount_re.search(line).group(1)
            value=discount_re.search(line).group(2)
            header_data[key.strip()] = value.strip()

        # Check if it's a row in the table section
        row=num_re.search(line)
        if row and work:
            columns = num_re.search(line).group(0).split()
            table_data.append(Line(doctype,Ref,Designation,*columns))
             
    # Combine header data and table data into a JSON object
    json_data = {
        "header": header_data,
        "table": table_data
    }
    return json_data

# Main script

# os.system(f'ocrmypdf {"sample1.pdf"} input.pdf')
invoice_pdf_path = "input.pdf"

# Extract key-value pairs from the invoice PDF
data = extract_key_value_pairs(invoice_pdf_path)

df = pd.DataFrame(data['table'])

header_row = pd.Series(data['header'])

final_df = pd.concat([header_row.to_frame().T, df], ignore_index=True)
final_df.to_csv("output.csv",index=False)
