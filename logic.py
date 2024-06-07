import os
import random
import string
import datetime
from db import insert_new_upload_db


def generate_identifier(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_folder_size(folder):
    total_size = 0
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
            file_count += 1
    return total_size / (1024 ** 3), file_count  # Return size in GB


def save_files(files, upload_folder):
    identifier = generate_identifier()
    save_path = os.path.join(upload_folder, identifier)
    os.makedirs(save_path, exist_ok=True)

    try:
        for file in files:
            file.save(os.path.join(save_path, file.filename))

        size_gb, file_count = get_folder_size(save_path)
        create_date = datetime.datetime.now()
        end_date = create_date + datetime.timedelta(days=28)

        insert_new_upload_db(identifier, create_date, end_date, size_gb, file_count)

        return {"identifier": identifier, "error": None}
    except Exception as e:
        return {"identifier": None, "error": str(e)}
