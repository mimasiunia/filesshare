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

    @staticmethod
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

    @staticmethod
    def update_statistics(file_count, size_gb):
        try:
            conn = Connector.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Statistics SET total_files_uploaded = total_files_uploaded + ?, total_gb_uploaded = total_gb_uploaded + ?",
                (file_count, size_gb)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except mariadb.Error as e:
            print(f"Error updating statistics: {e}")

    def get_expired_files(current_time):
        try:
            conn = Connector.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Identifier FROM Uploads WHERE EndDate < ?", (current_time,)
            )
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            print(f"Found {len(rows)} expired files in database.")
            return [row[0] for row in rows]
        except mariadb.Error as e:
            print(f"Error fetching expired files from database: {e}")
            return []

    @staticmethod
    def delete_upload_record(identifier):
        try:
            conn = Connector.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM Uploads WHERE Identifier = ?", (identifier,)
            )
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Successfully deleted database record for identifier: {identifier}")
        except mariadb.Error as e:
            print(f"Error deleting upload record from database: {e}")