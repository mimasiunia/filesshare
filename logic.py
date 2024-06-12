import os
import random
import string
import datetime
from db import Connector


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

        Connector.insert_new_upload_db(identifier, create_date, end_date, size_gb, file_count)

        # Update statistics
        Connector.update_statistics(file_count, size_gb)

        return {"identifier": identifier, "error": None}
    except Exception as e:
        return {"identifier": None, "error": str(e)}


def get_folder_size(folder):
    total_size = 0
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
            file_count += 1
    return total_size / (1024 ** 3), file_count  # Return size in GB


def get_statistics():
    try:
        conn = Connector.create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT total_files_uploaded, total_gb_uploaded FROM Statistics"
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            return {
                "total_files_uploaded": row[0],
                "total_gb_uploaded": row[1]
            }
        else:
            return {
                "total_files_uploaded": 0,
                "total_gb_uploaded": 0.0
            }
    except Exception as e:
        print(f"Error fetching statistics from database: {e}")
        return {
            "total_files_uploaded": 0,
            "total_gb_uploaded": 0.0
        }



def generate_identifier(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def validate_identifier(identifier):
    return len(identifier) == 12 and identifier.isalnum()


def get_file_info(identifier):
    return Connector.get_file_info_db(identifier)


def get_folder_path(identifier, upload_folder):
    folder_path = os.path.join(upload_folder, identifier)
    return folder_path if os.path.exists(folder_path) else None
