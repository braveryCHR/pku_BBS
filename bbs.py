from flask import *
from dbop import DB
import sys
import time
from datetime import datetime

DB_conf = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'jrbbs',
    'port': 3306,
    'charset': 'utf8mb4'
}
sys.path.insert(0, 'D:\OneDrive - pku.edu.cn\程序\pku_BBS')

registerTip = '<div class="alert alert-info">请填写所有信息进行注册，不得为空</div>'
registerWarn = '<div class="alert alert-warning">有信息未被填写，请重填</div>'
registerSucc = '<div class="alert alert-success">恭喜您注册成功，请点击上方按钮进行登录</div>'
registerFail = '<div class="alert alert-danger">您的账号已经被注册，请选择其他的账号并重新填写信息</div>'

loginTip = '<div class="alert alert-info">请填写账号密码进行登录</div>'
loginWarn = '<div class="alert alert-warning">有信息未被填写，请重填</div>'
loginFail = '<div class="alert alert-danger">您的账号不存在或密码不正确！登录失败</div>'
colName = ("account", "nickname", "password", "birthday", "gender", "email", "ulevel", "join_date", "uidentity")
realName = ('账号', "昵称", "密码", "生日", "性别(0男1女)", "电子邮件", "等级", "注册时间", "身份(0用户1版主)")

postTip = '<div class="alert alert-info">请填写所有信息以发表帖子，不得为空</div>'
postWarn = '<div class="alert alert-warning">有信息未被填写，请重填</div>'

searchTip = '<div class="alert alert-info">请填写关键词以搜索，不得为空</div>'
searchWarn = '<div class="alert alert-warning">有信息未被填写，请重填</div>'
searchSucc = '<div class="alert alert-success">查询结束，以下是查询结果</div>'

# 定义一些常量
initLevel = 1
boy = 0
girl = 1
user = 0
master = 1
admin = 2

db_con = DB(DB_conf)

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = '加密Session所需的密钥'


def transform_gender(gender):
    if gender == "男生":
        return 0
    return 1


# 进入主页，此时设置了cookie！
@app.route('/')
def index():
    resp = make_response(render_template('index.html'))
    resp.set_cookie('account', '', expires=0)
    return resp


# 进入登入界面
@app.route('/login')
def login():
    return render_template('login.html',
                           提示=loginTip)


# 检查登录的账号密码
@app.route('/login', methods=['post'])
def login_form():
    form = request.form
    # 处理信息不完整的情况
    for item in form:
        if form[str(item)] == '':
            return render_template('login.html',
                                   提示=loginWarn)
    # 检验账号密码
    account, password = form['account'], form['password']
    result = db_con.login_check(account, password)
    if not result:
        return render_template('login.html', 提示=loginFail)
    else:
        info = db_con.query_user_info(account)
        response = make_response(redirect('show_person_info'))
        response.set_cookie('account', account)
        return response


# 进入注册界面
@app.route('/register')
def register():
    return render_template('register.html',
                           提示=registerTip)


# 检验注册表单信息
@app.route('/register', methods=['post'])
def register_form():
    form = request.form
    # 处理信息不全的情况
    for item in form:
        if form[str(item)] == '':
            return render_template('register.html',
                                   提示=registerWarn)
    # 格式化各种信息
    account, password, nickname, birthday, email = form['account'], form['password'], form['nickname'], form[
        'birthday'], form['email']
    gender = form.getlist('gender')
    gender = transform_gender(gender[0])
    join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # print(account, password, nickname, birthday, gender, email, initLevel, join_date, user)
    result = db_con.insert_user_info(account, password, nickname, birthday, gender, email, ulevel=initLevel,
                                     join_date=join_date, uidentity=user)
    # 处理结果
    if result:
        return render_template('login.html',
                               提示=registerSucc)
    else:
        return render_template('register.html',
                               提示=registerFail)


# 展示个人信息页面
@app.route('/show_person_info')
def show_person_info():
    account = request.cookies.get('account')
    # print(account)
    info = db_con.query_user_info(account)
    return render_template('person_info.html', content=zip(realName, info[0]))


# 展示版块页面
@app.route('/show_section')
def show_all_section():
    section_info = db_con.query_all_section_info()
    return render_template('show_section.html', content=section_info)


# 展示某个版块上面的帖子
@app.route('/show_this_section/<section_info>', methods=['post', 'get'])
def show_this_section(section_info):
    section_number, section_name = \
        section_info.split('-')[0], section_info.split('-')[1]
    # print(section_number, section_name)
    content = db_con.query_this_section_info(section_number)
    return render_template('show_this_section.html',
                           content=content,
                           section_number=section_number,
                           section_name=section_name)


# 展示所有帖子
@app.route('/show_all_post')
def show_all_post():
    content = db_con.query_all_post()
    return render_template('show_all_post.html',
                           content=content)


# 展示某个帖子的内容
@app.route('/show_this_post/<post_number>', methods=['post', 'get'])
def show_this_post(post_number):
    try:
        # print(post_number)
        post_content, reply_content = db_con.query_this_post(post_number)
        # print(content)
        return render_template('show_this_post.html',
                               post_title=post_content[0][4],
                               nickname=post_content[0][3],
                               post_time=post_content[0][6],
                               post_content=post_content[0][5],
                               reply_content=reply_content,
                               post_number=post_number)
    # 找不到帖子就404
    except:
        return render_template('404.html')


# 点击前十的帖子
@app.route("/show_click_top10_post", methods=['post', 'get'])
def show_click_top10_post():
    content = db_con.query_top10_clicktimes()
    return render_template('show_top10_post.html',
                           content=content,
                           title="点击数前十的热帖")


# 回复前十的帖子
@app.route("/show_reply_top10_post", methods=['post', 'get'])
def show_reply_top10_post():
    content = db_con.query_top10_replytimes()
    return render_template('show_top10_post.html',
                           content=content,
                           title="回复数前十的热帖")


# 在某个帖子下面进行回复
@app.route('/show_this_post_reply', methods=['post', 'get'])
def reply_form():
    account = request.cookies['account']
    form = request.form
    post_number, reply_content = form['post_number'].split('-')[1], \
                                 form['reply_content']
    reply_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_con.insert_reply_content(account, post_number, reply_content, reply_time)
    # 回复之后重新进入该帖子来刷新
    return redirect('/show_this_post/' + str(post_number))


# 发帖页面
@app.route('/send_one_post')
def send_one_post():
    section_info = db_con.query_section_info()
    return render_template('send_one_post.html',
                           section=section_info,
                           提示=postTip)


# 处理发帖的表单
@app.route('/send_one_post', methods=['get', 'post'])
def post_form():
    form = request.form
    section_number, post_title, \
    post_content, account = \
        form['section'].split('-')[0], form['post_title'], \
        form['post_content'], request.cookies['account']
    # 处理信息不全的情况
    if post_title == '' or post_content == '':
        section_info = db_con.query_section_info()
        return render_template('send_one_post.html',
                               section=section_info,
                               提示=postWarn)
    post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # print(section_number,post_title,post_content,account)
    post_number = db_con.insert_post(section_number, account, post_title, post_content, post_time)
    # 发帖成功后进入该帖子
    return redirect('show_this_post/' + str(post_number))


# 进入搜索帖子页面
@app.route('/search_post', methods=['get', 'post'])
def search_post(tip=None, data=None):
    # 设置两个参数来区分不同情况
    # 两参数都是None，说明在进入该页面
    if tip is None and data is None:
        return render_template('search_post.html',
                               提示=searchTip)
    # 参数不是None，说明在返回搜索结果
    else:
        return render_template('search_post.html',
                               提示=tip,
                               content=data)


# 搜索帖子
@app.route('/search_form', methods=['get', 'post'])
def search_form():
    # 处理刷新的情况，这时没有关键词
    try:
        keyWord = request.form['keyWord']
    except:
        # 重进进入搜索页面
        return search_post()
    # 无论说明情况，都使用search_post进入页面，区别在于参数
    if keyWord == '':
        search_res = (('无', '无', '无', '无', '无', '无', '无', '无'),)
        return search_post(searchWarn, search_res)
    search_res = db_con.query_search_post(keyWord)
    if len(search_res) == 0:
        search_res = (('无', '无', '无', '无', '无', '无', '无', '无'),)
    return search_post(searchSucc, search_res)


# 进入搜索用户的页面，逻辑同上
@app.route('/search_user', methods=['get', 'post'])
def search_user(tip=None, data=None):
    if tip is None and data is None:
        return render_template('search_user.html',
                               提示=searchTip)
    else:
        return render_template('search_user.html',
                               提示=tip,
                               content=data)


# 搜索用户
@app.route('/search_user_form', methods=['get', 'post'])
def search_user_form():
    # 处理刷新的情况，这时没有关键词
    try:
        keyWord = request.form['keyWord']
    except:
        return search_post()
    if keyWord == '':
        search_res = (('无', '无', '无', '无', '无', '无', '无', '无'),)
        return search_user(searchWarn, search_res)
    search_res = db_con.query_search_user(keyWord)
    if len(search_res) == 0:
        search_res = (('无', '无', '无', '无', '无', '无', '无', '无'),)
    return search_user(searchSucc, search_res)


def before_request():
    import glob
    files = glob.glob('uploaded_files/*')
    session['files'] = files


# 处理404和500
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html'), 500


if __name__ == '__main__':
    app.before_request(before_request)
    app.run(host='0.0.0.0', port=5008)
