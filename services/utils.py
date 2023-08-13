import time
from fastapi import HTTPException
import openai
import re
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import io
import zipfile
import os
import shutil
import base64
import requests
from PIL import Image




def upload_and_save_file(uploaded_file, dest, output_filename=""):
    if output_filename == "":
        output_filename = get_current_time_stamp() + '.' + file_extension(uploaded_file.filename)
    
    file_location = dest + str(output_filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(uploaded_file.file.read())
    return file_location

def get_current_time_stamp():
    time_stamp = time.time()
    time_stamp = str(time_stamp).split('.')
    return str(time_stamp[0]) + str(time_stamp[1])

def file_extension(filename):
    f_arr = filename.split('.')
    return filename.split('.')[len(f_arr)-1]


def file_basename(filename):
    return filename.split('.')[0]

def check_extension(filename, allows='*'):
    if allows == '*':
        pass
    else:
        ext = file_extension(filename)
        if ext not in allows:
            raise HTTPException(status_code=500, detail="extension  is not allowed. ")
        


def get_response_from_gpt(prompt):
    openai.api_key = "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"
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": prompt}
    ]
    )
    return completion.choices[0].message["content"]



def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    output_stream = io.StringIO()
    converter = TextConverter(resource_manager, output_stream, laparams=None)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = output_stream.getvalue()
    converter.close()
    output_stream.close()
    return text


def remove_personal_info(text):
    # Remove phone numbers
    text = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove addresses (assuming US addresses)
    text = re.sub(r'\b\d{1,5}\s+[\w\s]+\s+(?:APT\s)?\w*\d*\b', '', text)
    text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '', text) # Remove IP addresses
    text = re.sub(r'\b(0?[1-9]|1[0-2])[-\/](0?[1-9]|[12][0-9]|3[01])[-\/]\d{2,4}\b', '', text)

    
    return text



def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

    return output_path




def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
    except Exception as e:
        pass


def raise_error(code=500, detail=""):
    raise HTTPException(status_code=code, detail=detail)



def file_to_base64(file_path):
    with open(file_path, "rb") as file:
        file_content = file.read()
        base64_content = base64.b64encode(file_content)
        return base64_content.decode("utf-8")  # Convert bytes to string



def delete_file(file_path):
    try:
        os.remove(file_path)
        return 1
    except OSError as error:
        return 0
    

def delete_path(path):
    if os.path.isfile(path):
        os.remove(path)
        return 1
    elif os.path.isdir(path):
        shutil.rmtree(path)
        return 1
    else:
        return 0


def convert_url_to_file(url, file_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    else:
        raise HTTPException(status_code=500, detail="failed to convert URL to file.")



def compress_png(input_path, output_path, quality=85):
    try:
        # Open the PNG image
        image = Image.open(input_path)
        
        # Save the image with reduced quality
        image.save(output_path, "PNG", quality=quality, optimize=True)
        
        print(f"Compressed PNG saved to {output_path}")
    except Exception as e:
        print(f"Error: {e}")