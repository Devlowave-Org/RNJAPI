import sqlite3


# ATTENTION : PROTECTION ANTI FAILLE SQL A CODER : LISTE BLANCHE
class Database:
    def __init__(self, bdd_path):
        self.conn = sqlite3.connect(bdd_path)
        self.cursor = self.conn.cursor()

    def select_data(self, column_name, table_name, id_nbr):
        return self.cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE ID = ?", (id_nbr,)).fetchall()

    def select_all_data(self, table_name, id_nbr):
        return self.cursor.execute(f"SELECT * FROM {table_name} WHERE ID = ?", (id_nbr,)).fetchone()

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

    def executemany_and_commit_data(self, sql_command, data_tuple):
        self.cursor.executemany(sql_command, data_tuple)
        self.conn.commit()

    def close(self):
        self.conn.close()
