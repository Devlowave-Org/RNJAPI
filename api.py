from flask import Flask
from flask_restful import Api, Resource
from database import *
from constants import *
from utils import *

app = Flask(__name__)
api = Api(app)


def get_last_table_name():
    database = Database(TABLE_PATH)
    table_names = database.select_tables_name()
    database.close()
    dates = [table_name.replace(BASE_TABLE_NAME, "") for table_name in table_names]
    most_recent_date = get_most_recent_date(dates)
    most_recent_table_name = f"{BASE_TABLE_NAME}{most_recent_date}"
    return most_recent_table_name


class Column(Resource):

    @staticmethod
    def get(column_name):
        table_name = get_last_table_name()
        database = Database(TABLE_PATH)
        id_tuple = database.select_data_column(table_name, "id")
        items_tuple = database.select_data_column(table_name, column_name)
        database.close()
        items_dict = {id_nbr[0]: item[0] for id_nbr, item in zip(id_tuple, items_tuple)}
        return items_dict


api.add_resource(Column, "/column/<string:column_name>")


class Row(Resource):

    @staticmethod
    def get(id_nbr):
        table_name = get_last_table_name()
        database = Database(TABLE_PATH)
        items_tuple = database.select_all_data_with_id(table_name, id_nbr)
        items_dict = lists_to_dict(COLUMNS, items_tuple)
        database.close()
        return items_dict


api.add_resource(Row, "/row/<string:id_nbr>")

if __name__ == "__main__":
    app.run(debug=False)
