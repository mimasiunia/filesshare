import mariadb


class Connector:
    @staticmethod
    def create_connection():
        connection = mariadb.connect(
            user="your_user",
            password="your_password",
            host="your_host",
            port=3306,
            database="your_database"
        )
        return connection

    @staticmethod
    def insert_new_upload_db(identifier, create_date, end_date, size_gb, file_count):
        try:
            conn = Connector.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Uploads (Identifier, CreateDate, EndDate, SizeGB, FileCount) VALUES (?, ?, ?, ?, ?)",
                (identifier, create_date, end_date, size_gb, file_count)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except mariadb.Error as e:
            print(f"Error inserting into database: {e}")


def insert_new_upload_db(identifier, create_date, end_date, size_gb, file_count):
    Connector.insert_new_upload_db(identifier, create_date, end_date, size_gb, file_count)
def get_file_info_db(identifier, create_date, end_date, size_gb, file_count):
    Connector.insert_new_upload_db(identifier, create_date, end_date, size_gb, file_count)