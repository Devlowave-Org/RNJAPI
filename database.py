import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('rnjapi.db')
        self.cursor = self.conn.cursor()

    def create_rnjapi_table(self, table_name):
        create_table = f'''CREATE TABLE IF NOT EXISTS {table_name}(
        id INTEGER PRIMARY KEY,
        name TEXT,
        city TEXT,
        department_nbr TEXT,
        department_name TEXT,
        region TEXT,
        directory_link TEXT UNIQUE NOT NULL,
        short_description TEXT,
        description TEXT,
        website TEXT,
        instagram TEXT,
        facebook TEXT,
        youtube TEXT,
        tiktok TEXT,
        twitter TEXT,
        discord TEXT,
        other_website TEXT,
        email TEXT,
        approval_date INTEGER,
        members_nbr INTEGER,
        last_update INTEGER
        )'''
        self.execute_and_commit(create_table)

    def insert_rnjapi_first_scraper_data(self, data_tuple):
        insert = f"INSERT INTO RNJAPI (id, name, city, department_nbr, department_name, directory_link, region, short_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        self.execute_and_commit_data(insert, data_tuple)

    def update_rnjapi_first_scraper_data(self, data_tuple):
        update = f"UPDATE RNJAPI SET name = ?, city = ?, department_nbr = ?, department_name = ?, directory_link = ?, region = ?, short_description = ? WHERE id = ?"
        self.execute_and_commit_data(update, data_tuple)

    def update_rnjapi_second_scraper_data(self, data_tuple):
        update = f"UPDATE RNJAPI SET description = ?, website = ?, instagram = ?, facebook = ?, youtube = ?, tiktok = ?, twitter = ?, discord = ?, other_website = ?, email = ?, approval_date = ?, members_nbr = ? WHERE id = ?"
        self.execute_and_commit_data(update, data_tuple)

    def update_rnjapi_last_update_column(self, data_tuple):
        update = f"UPDATE RNJAPI SET last_update = ? WHERE id = ?"
        self.execute_and_commit_data(update, data_tuple)

    def select_data(self, column_name, table_name, other_arguments=""):
        return self.cursor.execute(
            f"SELECT {column_name} FROM {table_name} {other_arguments}").fetchall()

    def delete_table(self, table_name):
        delete_table = f"DROP TABLE IF EXISTS {table_name}"
        self.execute_and_commit(delete_table)

    def delete_row(self, table_name, row_id):
        data_tuple = (row_id,)
        delete_row = f"DELETE FROM {table_name} WHERE id= ?"
        self.execute_and_commit_data(delete_row, data_tuple)

    def execute_and_commit(self, sql_command):
        self.cursor.execute(sql_command)
        self.conn.commit()

    def execute_and_commit_data(self, sql_command, data_tuple):
        self.cursor.execute(sql_command, data_tuple)
        self.conn.commit()

    def close(self):
        self.conn.close()
