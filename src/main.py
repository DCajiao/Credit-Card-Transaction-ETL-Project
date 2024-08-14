from database.dbconnection import DB

db = DB()

def execute_query_file(query_file_path):
    try:
        with open(query_file_path, "r") as file:
            query = file.read()
        db.connect()
        result = db.execute(query)
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()


if __name__ == '__main__':
    execute_query_file('../sql/queries/001_view_tables.sql')