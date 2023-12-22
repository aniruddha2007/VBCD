import csv
from flask import request, session, redirect, url_for, flash
from functools import wraps
import chardet
import codecs
import io
from modules.contacts import Contact, db
from io import BytesIO
import sqlite3


# mapping of CSV headers to database columns
csv_to_db_mapping = {
    "First Name": "first_name",
    "Last Name": "last_name",
    "E-mail Address": "email_address",
    "E-mail 2 Address": "email_address_2",
    "Business Phone": "business_phone",
    "Mobile Phone": "mobile_phone",
    "Other Phone": "other_phone",
    "Primary Phone": "primary_phone",
    "Business Fax": "business_fax",
    "Job Title": "job_title",
    "Company": "company",
    "Business Street": "business_address",
    "Business City": "business_city",
    "Business State": "business_state",
    "Business Postal Code": "business_zip",
    "Business Country/Region": "business_country",
    "Personal Web Page": "personal_website",
    "Web Page": "web_page",
    "Birthday": "birthday",
    "Notes": "notes",
}

# mapping of CSV headers to database columns
csv_to_db_mapping_zh = {
    "名字": "first_name",
    "全名": "first_name",
    "姓氏": "last_name",
    "電子郵件地址": "email_address",
    "電子郵件 2 地址": "email_address_2",
    "商務電子郵件": "email_address",
    "商務電話": "business_phone",
    "行動電話": "mobile_phone",
    "其他電話": "other_phone",
    "主要電話": "primary_phone",
    "商務傳真": "business_fax",
    "職稱": "job_title",
    "公司": "company",
    "商務地址-(街/路)": "business_address",
    "商務地址-(市)": "business_city",
    "商務地址-(州/省)": "business_state",
    "商務地址-(郵遞區號)": "business_zip",
    "商務地址-(國家/地區)": "business_country",
    "個人網站": "personal_website",
    "商務網址": "web_page",
    "網頁": "web_page",
    "生日": "birthday",
    "附註": "notes",
}


def load_csv_to_db(csv_file, use_chinese_mapping=False):
    csv_reader = csv.DictReader(csv_file)

    # Extract tag from the file name (modify this part according to your needs)
    file_name = request.files["csvFile"].filename
    tag = file_name.split(".")[0]

    # Choose the appropriate mapping based on use_chinese_mapping
    current_mapping = csv_to_db_mapping_zh if use_chinese_mapping else csv_to_db_mapping

    for row in csv_reader:
        row = {key.lstrip("\ufeff"): value for key, value in row.items()}
        mapped_row = {
            current_mapping.get(key, key.lstrip("\ufeff")): row[key] for key in row
        }

        # Filter out keys that are not present in the Contact class
        valid_keys = [key for key in mapped_row.keys() if hasattr(Contact, key)]
        filtered_row = {key: mapped_row[key] for key in valid_keys}

        try:
            # Use **filtered_row to unpack the dictionary into keyword arguments
            contact = Contact(tag=tag, **filtered_row)
            db.session.add(contact)
        except Exception as e:
            # Log the error
            logging.error(f"Error adding contact: {e}, Data: {row}")


# Function to detect and convert encoding
def detect_and_convert_encoding(content):
    result = chardet.detect(content)
    detected_encoding = result["encoding"]

    if detected_encoding.lower() != "utf-8":
        try:
            content = content.decode(detected_encoding, errors="replace").encode(
                "utf-8"
            )
            return content
        except Exception as e:
            print(f"Error converting to UTF-8: {e}")
            return None
    else:
        return content


def load_csv(file):
    # Check the encoding of the uploaded CSV file
    detected_encoding = check_csv_encoding(file)

    # If the encoding is not UTF-8, convert the content
    if detected_encoding.lower() != "utf-8":
        utf8_content = convert_to_utf8(file, detected_encoding)
        print("File converted to UTF-8")
        return utf8_content
    else:
        # If the file is already in UTF-8 encoding, just read and return the content
        file.seek(0)  # Reset the file position to the beginning
        content = file.read()
        return content


def check_csv_encoding(file):
    # Reset the file position to the beginning
    file.seek(0)

    # Read a portion of the content to allow chardet to detect the encoding
    raw_content = file.read(1024)

    detector = chardet.universaldetector.UniversalDetector()
    detector.feed(raw_content)
    detector.close()

    detected_encoding = detector.result["encoding"]

    try:
        # Try to decode a small portion of the content to validate the encoding
        file.seek(0)
        file_content = file.read(1024).decode(detected_encoding)
    except UnicodeDecodeError as e:
        # If a decoding error occurs, print an error message and handle accordingly
        print(f"Error decoding content: {e}")
        # You might want to replace or skip problematic bytes here
        detected_encoding = "utf-8"  # Assume UTF-8 if decoding fails

    return detected_encoding


def convert_to_utf8(file, detected_encoding):
    # Reset the file position to the beginning
    file.seek(0)

    try:
        # Read the content with the detected encoding
        content = file.read().decode(detected_encoding)
    except UnicodeDecodeError as e:
        # If a decoding error occurs, print an error message and handle accordingly
        print(f"Error decoding content: {e}")
        # You might want to replace or skip problematic bytes here
        content = file.read().decode(
            "utf-8", errors="ignore"
        )  # Ignore errors during decoding

    # Return the content as a BytesIO object
    return BytesIO(content.encode("utf-8"))


# DO NOT EDIT THIS FUNCTION
def load_csv_to_db_DO_NOT_EDIT(csv_file, use_chinese_mapping=False):
    # Set up basic logging configuration
    logging.basicConfig(level=logging.DEBUG)

    csv_reader = csv.DictReader(csv_file)

    # Extract tag from the file name (modify this part according to your needs)
    file_name = request.files["csvFile"].filename
    tag = file_name.split(".")[0]

    # Choose the appropriate mapping based on use_chinese_mapping
    current_mapping = csv_to_db_mapping_zh if use_chinese_mapping else csv_to_db_mapping

    # Debugging: Print the current_mapping
    # current_mapping = csv_to_db_mapping_zh

    for row in csv_reader:
        row = {key.lstrip("\ufeff"): value for key, value in row.items()}
        mapped_row = {
            current_mapping.get(key, key.lstrip("\ufeff")): row[key] for key in row
        }

        # Filter out keys that are not present in the Contact class
        valid_keys = [key for key in mapped_row.keys() if hasattr(Contact, key)]
        filtered_row = {key: mapped_row[key] for key in valid_keys}

        try:
            # Use **filtered_row to unpack the dictionary into keyword arguments
            contact = Contact(tag=tag, **filtered_row)
            db.session.add(contact)
        except Exception as e:
            # Log the error
            logging.error(f"Error adding contact: {e}, Data: {row}")


# initializing the database for login and register
def init_db():
    with sqlite3.connect("login.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
                       CREATE TABLE IF NOT EXISTS users(
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           username TEXT NOT NULL,
                           password TEXT NOT NULL
                           )
                        """
        )
        connection.commit()


# login required function
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" in session:
            return view(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for("login"))

    return wrapped_view
