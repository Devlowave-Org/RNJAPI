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
        directory_link TEXT UNIQUE,
        short_description TEXT,
        description TEXT,
        email TEXT,
        approval_date INTEGER,
        mumbers_nbr INTEGER,
        instagram INTEGER,
        discord INTEGER,
        facebook INTEGER,
        youtube INTEGER,
        other_networks TEXT,
        website TEXT,
        last_AllJa_update INTEGER,
        last_JaPage_update INTEGER
        )'''
        self.execute_and_commit(create_table)



    def insert_rnjapi_all_ja_data(self, data_tuple):
        insert = f'''INSERT INTO RNJAPI (id, name, city, department_nbr, department_name, directory_link, region, short_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        self.cursor.execute(insert, data_tuple)
        self.conn.commit()

    def update_rnjapi_all_ja_data(self, data_tuple):
        update = f'''UPDATE RNJAPI SET name = ?, city = ?, department_nbr = ?, department_name = ?, directory_link = ?, region = ?, short_description = ? WHERE id = ?'''
        self.cursor.execute(update, data_tuple)
        self.conn.commit()

    def select_data(self, column_name, table_name, other_arguments=""):
        return self.cursor.execute(
            f'''SELECT {column_name} FROM {table_name} {other_arguments}''').fetchall()

    def delete_table(self, table_name):
        delete_table = f'''DROP TABLE IF EXISTS {table_name}'''
        self.execute_and_commit(delete_table)

    def execute_and_commit(self, sql_command):
        self.cursor.execute(sql_command)
        self.conn.commit()

    def close(self):
        self.conn.close()



