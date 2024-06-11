import mariadb


class Connector:
    @staticmethod
    def create_connection():
        connection = mariadb.connect(
            user="fsApi",
            password="UnEGNEyVdsGfp4op6Slmc1",
            host="172.17.0.4",
            port=3306,
            database="fs"
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

    @staticmethod
    def get_file_info_db(identifier):
        try:
            conn = Connector.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT CreateDate, EndDate, SizeGB, FileCount FROM Uploads WHERE Identifier = ?",
                (identifier,)
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return {
                    "create_date": row[0],
                    "end_date": row[1],
                    "size_gb": row[2],
                    "file_count": row[3]
                }
            else:
                return None
        except mariadb.Error as e:
            print(f"Error fetching from database: {e}")
            return None
