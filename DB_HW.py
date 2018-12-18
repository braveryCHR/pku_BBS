from flask import Flask
from dbop import DB
from flask import render_template,redirect,url_for
from flask import request
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
    #db_con.generate_data()

    #g = db_con.query_insec_userinfo(3,0)
    #rstr = ''
    #for row in g:
    #    for tmp in row:
    #        rstr = rstr + str(tmp) + ' '
    #    rstr = rstr + '<br>'
    #rstr = '<h1>' + rstr + ' ' + '</h1>'

    return '<h1> hello </h1>'

@app.route('/login',methods=['GET','POST'])
def login():
    db_con = DB(DB_conf)
    if(request.method == 'POST'):
        temp = db_con.login_check(request.form['username'],request.form['password'])
        if temp == None:
            return '<h1>Invalid account or Error password</h1>'
        else:
            return  render_template('home.html',user=request.form['username'])
    return render_template('login_test.html')

if __name__ == '__main__':
    app.run()
