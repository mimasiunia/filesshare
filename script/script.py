import mariadb
import os
import time


class Connector:
    @staticmethod
    def create_connection():
        connection = mariadb.connect(
            user="fsApi",
            password="UnEGNEyVdsGfp4op6Slmc1",
            host="172.17.0.2",
            port=3306,
            database="fs"
        )
        return connection

    @staticmethod
    def get_expired_uploads():
        try:
            conn = Connector.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Identifier FROM Uploads WHERE EndDate < NOW()"
            )
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            return [row[0] for row in rows]
        except mariadb.Error as e:
            print(f"Error fetching expired uploads: {e}")
            return []

    @staticmethod
    def delete_upload_db(identifier):
        try:
            conn = Connector.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM Uploads WHERE Identifier = ?",
                (identifier,)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except mariadb.Error as e:
            print(f"Error deleting from database: {e}")


def delete_folder(identifier, base_path='data'):
    folder_path = os.path.join(base_path, identifier)
    if os.path.exists(folder_path):
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(folder_path)
        print(f"Deleted folder: {folder_path}")
    else:
        print(f"Folder {folder_path} does not exist")

def clean_expired_uploads():
    print("Starting cleanup process")
    expired_uploads = Connector.get_expired_uploads()
    for identifier in expired_uploads:
        print(f"Deleting upload with identifier: {identifier}")
        delete_folder(identifier)
        Connector.delete_upload_db(identifier)
        print(f"Deleted upload {identifier} and its folder")
    print("Cleanup process completed")


if __name__ == "__main__":
    while True:
        clean_expired_uploads()
        time.sleep(30)  # seconds
