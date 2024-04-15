import re
import textract
from upload_to_excel import upload_to_excel
import os


def extract_text_from_resume(pdf_file: str) -> str:
    return textract.process(pdf_file).decode("utf-8")


def extract_contact_info(text: str) -> dict:
    contact_info = {}

    # Extracting email addresses using regex
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        contact_info["email"] = email_matches[0]

    # Extracting phone numbers using regex
    phone_pattern = re.compile(
        r"\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{2})[-. ]*(\d{1})[-. ]*(\d{4})(?: *x(\d+))?\b"
    )

    phone_match = phone_pattern.search(text)
    if phone_match:
        phone_number = f"{phone_match.group(2)}-{phone_match.group(3)}{phone_match.group(4)}-{phone_match.group(5)}"
        contact_info["phone"] = phone_number

    return contact_info


def process_files(folder: str, output_file: str):

    data = [["resume_file", "email", "phone", "text"]]
    try:
        for folders in os.listdir(folder):
            if os.path.isdir(f"{folder}/{folders}"):
                for file in os.listdir(f"{folder}/{folders}"):
                    print(file)
                    file_name = os.path.join(f"{folder}/{folders}", file)
                    text = extract_text_from_resume(file_name)
                    contact_info = extract_contact_info(text)
                    data.append(
                        [
                            file,
                            contact_info.get("email", ""),
                            contact_info.get("phone", ""),
                            text.replace("\r", "").replace("\n", " ").replace("\f", ""),
                        ]
                    )
    except Exception as e:
        print(f"An error occurred while parsing pdf: {str(e)}")
        raise e

    upload_to_excel(data, output_file)
