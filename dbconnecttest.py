import pymysql

NAME = 'miksi$company_ask_csv_app'
USER = 'miksi'
PASSWORD = 'MiksiAI2023!'
HOST = 'miksi.mysql.pythonanywhere-services.com'
PORT = '3306'
db = pymysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=NAME )

print("db: ", db)