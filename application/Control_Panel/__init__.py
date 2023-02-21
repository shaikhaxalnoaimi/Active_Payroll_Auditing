from flask import Blueprint
blueprint = Blueprint(
    'home_blueprint',
    __name__,
    url_prefix=''

)





# create connection to the db
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# # print(BASE_DIR)
# # string2 = BASE_DIR.replace('\\n', ' ')
# # print(string2)
#
# # db_path1 = os.path.join("/NAO-Payroll/application/", "nao_db.sqlite3")
# db_path = os.path.join(BASE_DIR, "nao_db.sqlite3")
# # r'a\\nb'.replace('\\\\', '\\')
# print(db_path)
# # print(db_path1)
