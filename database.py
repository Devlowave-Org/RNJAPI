import sqlite3
import re
from constants import *


def is_valid_table(table_name):
    pattern = fr"^{BASE_TABLE_NAME}{DATE_FORMAT_REGEX}"
    string = table_name
    match = re.search(pattern, string)
    return True if match else False


def is_valid_column(column_name):
    return True if column_name in COLUMNS else False


class Database:
    def __init__(self, bdd_path):
        self.conn = sqlite3.connect(bdd_path, timeout=10, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def select_tables_name(self):
        self.cursor.execute("SELECT name FROM sqlite_schema WHERE type='table';")
        tables = self.cursor.fetchall()
        table_names = [table[0] for table in tables]
        return table_names

    def select_data_column(self, table_name, column_name):
        if is_valid_table(table_name) and is_valid_column(column_name):
            return self.cursor.execute(f"SELECT {column_name} FROM {table_name} ORDER BY id").fetchall()
        else:
            print("invalid table name or column name")

    def select_data_with_id(self, column_name, table_name, id_nbr):
        if is_valid_table(table_name) and is_valid_column(column_name):
            return self.cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE ID = ?", (id_nbr,)).fetchall()
        else:
            print("invalid table name or column name")

    def select_all_data_with_id(self, table_name, id_nbr):
        if is_valid_table(table_name):
            return self.cursor.execute(f"SELECT * FROM {table_name} WHERE ID = ?", (id_nbr,)).fetchone()
        else:
            print("invalid table name")

    def delete_table(self, table_name):
        if is_valid_table(table_name):
            delete_table = f"DROP TABLE IF EXISTS {table_name}"
            self.execute(delete_table)
        else:
            print("invalid table name")

    def delete_row(self, table_name, row_id):
        if is_valid_table(table_name):
            data_tuple = (row_id,)
            delete_row = f"DELETE FROM {table_name} WHERE id= ?"
            self.execute_data(delete_row, data_tuple)
        else:
            print("invalid table name")

    def execute(self, sql_command):
        self.cursor.execute(sql_command)

    def execute_data(self, sql_command, data_tuple):
        self.cursor.execute(sql_command, data_tuple)

    def executemany(self, sql_command, data_tuple):
        self.cursor.executemany(sql_command, data_tuple)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
