from flask import Flask
from dbop import DB
import sys
DB_conf = {
    'host' :'localhost',
    'user' : 'root',
    'password' : '123456',
    'database' : 'jrbbs',
    'port' : 3306,
    'charset' :'utf8mb4'
}
sys.path.insert(0,'F:\DB_HW')
app = Flask(__name__)


@app.route('/')
def hello_world():
    db_con = DB(DB_conf)
    return '<h1>Hello World!mygd</h1>'

if __name__ == '__main__':
    app.run()
