from flask import *
from dbop import DB
from xml_parser import parse_xml
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
sys.path.insert(0, 'F:\DB_HW')

registerTip = '<div class="alert alert-info">请填写所有信息进行注册，不得为空</div>'
registerWarn = '<div class="alert alert-warning">有信息未被填写，请重填</div>'
registerSucc = '<div class="alert alert-success">恭喜您注册成功，请点击上方按钮进行登录</div>'
registerFail = '<div class="alert alert-danger">您的账号已经被注册，请选择其他的账号并重新填写信息</div>'

loginTip = '<div class="alert alert-info">请填写账号密码进行登录</div>'
loginWarn = '<div class="alert alert-warning">有信息未被填写，请重填</div>'
loginFail = '<div class="alert alert-danger">您的账号不存在或密码不正确！登录失败</div>'
colName = ("account", "nickname", "password", "birthday", "gender", "email", "ulevel", "join_date", "uidentity")
realName = ('账号', "昵称", "密码", "生日", "性别", "电子邮件", "等级", "注册时间", "身份")

postTip = '<div class="alert alert-info">请填写所有信息以发表帖子，不得为空</div>'
postWarn = '<div class="alert alert-warning">有信息未被填写，请重填</div>'

searchTip = '<div class="alert alert-info">请填写关键词以搜索，不得为空</div>'
searchWarn = '<div class="alert alert-warning">有信息未被填写，请重填</div>'
searchSucc = '<div class="alert alert-success">查询结束，以下是查询结果</div>'

adminTips = ['<div class="alert alert-info">对不起，你不是bbs管理员</div>',
             '<div class="alert alert-info">欢迎进入管理界面</div>',
             '<div class="alert alert-info">添加新用户成功</div>',
             '<div class="alert alert-info">删除帖子成功</div>',
             '<div class="alert alert-info">删除用户成功</div>',
             '<div class="alert alert-info">对不起，你不是版主</div>',
             '<div class="alert alert-info">删除回复成功</div>',
             '<div class="alert alert-info">请填写新的板块名称</div>',
             '<div class="alert alert-info">板块名称修改成功</div>']
searchHotTips = '<div class="alert alert-info">具体用户信息请单独查询</div>'

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
    else:   #mode_sec的cookies，-1代表普通用户，-2 代表管理员，其他情况代表该版对应的版主
        info = db_con.query_user_info(account)
        uid = db_con.get_user_identity(account)
        if(uid==0):
            response = make_response(redirect('show_person_info'))
            response.set_cookie('account', account)
            response.set_cookie('uid',str(uid))
            response.set_cookie('mode_sec',str(-1))
            return response
        elif(uid==1):
            moderator_sid = db_con.get_moderator_sec(account)
            response = make_response(redirect('Moderator'))
            response.set_cookie('account', account)
            response.set_cookie('uid', str(uid))
            response.set_cookie('mode_sec',moderator_sid)
            return response
        else:
            response = make_response(redirect('Admin'))
            response.set_cookie('account', account)
            response.set_cookie('uid', str(uid))
            response.set_cookie('mode_sec',str(-2))
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

#操作之后统一跳回到个人信息 不管是管理员还是普通用户无效点击 zjy
@app.route('/show_person_info_back/<int:signum>',methods=['post','get'])
def show_person_info_back(signum):
    account = request.cookies.get('account')
    info = db_con.query_user_info(account)
    return render_template('person_info_back.html',content=zip(realName,info[0]),提示=adminTips[signum])

#管理员添加用户
@app.route('/admin_adduser')
def admin_adduser():
    secinfo = db_con.query_section_info()
    return render_template('admin_adduser.html',提示=registerTip,secs=secinfo)

#管理员添加用户表单
@app.route('/admin_adduser',methods=['post'])
def admin_adduer_form():
    secinfo = db_con.query_section_info()
    form = request.form
    # 处理信息不全的情况
    for item in form:
        if form[str(item)] == '':
            return render_template('admin_adduser.html',
                                   提示=registerWarn,secs=secinfo)
    # 格式化各种信息
    account, password, nickname, birthday, email = form['account'], form['password'], form['nickname'], form[
        'birthday'], form['email']
    gender = form.getlist('gender')
    gender = transform_gender(gender[0])
    Identity = form.getlist('identity')
    Identity = int(Identity[0])
    admin_sec = -1
    if Identity == 1:
        admin_sec = form.getlist('adminsec')[0]
        admin_sec = admin_sec[0]

    join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = db_con.insert_user_info(account, password, nickname, birthday, gender, email, ulevel=initLevel,
                                     join_date=join_date, uidentity=Identity)
    if not result:
        return render_template("admin_adduser.html",提示=registerFail,secs=secinfo)
    else:
        if Identity!=1:
            return render_template('admin_page.html',提示=adminTips[2])
        else:
            db_con.insert_moderator_info(account,admin_sec)
            return render_template('admin_page.html',提示=adminTips[2])

#管理员邮箱
@app.route('/admin_mailbox',methods=['post','get'])
def admin_mailbox():
    ret,_ = db_con.fetch_adminmail()
    return render_template('admin_mail.html',content = ret)

@app.route('/admin_readmail/<tag_time>',methods=['post','get'])
def admin_readmail(tag_time):
    db_con.read_adminmail(tag_time)
    return redirect(url_for('admin_mailbox'))

@app.route('/admin_delete_mail/<tag_time>',methods=['post','get'])
def admin_delete_mail(tag_time):
    db_con.delete_adminmail(tag_time)
    return redirect(url_for('admin_mailbox'))

#管理员界面
@app.route('/Admin',methods=['post','get'])
def Admin():
    account = request.cookies.get('account')
    _,read_tag = db_con.fetch_adminmail()
    info = db_con.query_user_info(account)
    if int(info[0][8]) != 2:
        return redirect(url_for('show_person_info_back',signum=0))
    else:
        return render_template('admin_page.html',提示=adminTips[1],read_tag=read_tag)

#版主界面
@app.route('/Moderator',methods=['post','get'])
def Moderator():
    account = request.cookies.get('account')
    uid = request.cookies.get('uid')
    if uid != '1':
        return redirect(url_for('show_person_info_back',signum=5))
    else:
        mod_sec = request.cookies.get('mode_sec')
        sec_info = db_con.query_one_section(mod_sec)
        return render_template('moderator_page.html',sec_info = sec_info)

# 展示个人信息页面
@app.route('/show_person_info')
def show_person_info():
    account = request.cookies.get('account')
    # print(account)
    info = db_con.query_user_info(account)
    return render_template('person_info.html', content=zip(realName, info[0]))

#展示查询的用户最近个人信息
@app.route('/show_person_concretinfo/<accountp>',methods=['get','post'])
def show_person_concretinfo(accountp):
    fpath = db_con.get_person_ConcretInfo(accountp)
    bs, ps, rs = parse_xml()
    return render_template('show_person_concretinfo.html',account=accountp,
                                                        bs=bs,
                                                        ps=ps,
                                                        rs=rs)

#由于自己的登陆是带着cookie的，因此单写一个看自己的最近动态
@app.route('/show_person_concretinfo_s')
def show_person_concretinfo_s():
    account = request.cookies.get('account')
    fpath = db_con.get_person_ConcretInfo(account)
    bs, ps, rs = parse_xml()
    return render_template('show_person_concretinfo.html', account=account,
                           bs=bs,
                           ps=ps,
                           rs=rs)

# 展示版块页面
@app.route('/show_section')
def show_all_section():
    section_info = db_con.query_all_section_info()
    return render_template('show_section.html', content=section_info)

#分页展示板块
@app.route('/show_this_section_parti/<section_number>/<section_name>/<int:pnum>',methods=['post','get'])
def show_this_section_parti(section_number,section_name,pnum):
    content = db_con.query_this_section_info(section_number)
    pnum-=1
    Len = len(content)
    Len = (Len // 20) + 1
    if pnum + 1 < Len:
        content = content[20*pnum:20*(pnum+1)]
    else:
        content = content[20*pnum:]
    return render_template('show_this_section.html',content=content,
                           section_number=section_number,
                           section_name=section_name,
                           mode_sec=request.cookies.get('mode_sec'),
                           Len=Len,
                           pnum=pnum + 1)

# 展示某个版块上面的帖子
@app.route('/show_this_section/<section_info>', methods=['post', 'get'])
def show_this_section(section_info):

    section_number, section_name = \
        section_info.split('-')[0], section_info.split('-')[1]
    # print(section_number, section_name)
    '''
    content = db_con.query_this_section_info(section_number)
    return render_template('show_this_section.html',
                           content=content,
                           section_number=section_number,
                           section_name=section_name,
                           mode_sec = request.cookies.get('mode_sec'))
    '''
    return redirect(url_for('show_this_section_parti',section_number=section_number,
                            section_name=section_name,pnum=1))

#分页展示
@app.route('/show_all_post_parti/<int:pnum>',methods=['post', 'get'])
def show_all_post_parti(pnum):
    content = db_con.query_all_post()
    pnum -=1
    Len = len(content)
    Len = (Len // 20) + 1
    if pnum + 1 < Len:
        content = content[20*pnum:20*(pnum+1)]
    else:
        content = content[20*pnum:]
    return render_template('show_all_post_parti.html',content=content,
                           Len = Len,
                           pnum = pnum+1)

# 展示所有帖子
@app.route('/show_all_post')
def show_all_post():
    '''
    content = db_con.query_all_post()
    return render_template('show_all_post.html',
                           content=content)
    '''
    return redirect(url_for('show_all_post_parti',pnum=1))


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

#点赞更新
@app.route('/update_like_num', methods=['post','get'])
def update_like_num():
    pnum = request.args.get('post_number')
    fnum = request.args.get('floor_number')
    db_con.update_likenum(pnum,fnum)
    lnum = request.args.get('like_number')
    lnum = int(lnum)
    return str(lnum+1)

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
                               提示=searchTip,
                               uid=request.cookies.get('uid'))
    # 参数不是None，说明在返回搜索结果
    else:
        return render_template('search_post.html',
                               提示=tip,
                               content=data,
                               uid=request.cookies.get('uid'))


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
    if(request.cookies.get('uid')==0):
        if keyWord == '':
            search_res = (('无', '无', '无', '无', '无', '无', '无', '无'),)
            return search_post(searchWarn, search_res)
        search_res = db_con.query_search_post(keyWord)
        if len(search_res) == 0:
            search_res = (('无', '无', '无', '无', '无', '无', '无', '无'),)
        return search_post(searchSucc, search_res)
    else: #版主或管理员有权利删帖  到html其实判断了如果不是admin 即使是版主也没有删除权限
        if keyWord == '':
            search_res = (('无', '无', '无', '无', '无', '无', '无', '无','无'),)
            return search_post(searchWarn, search_res)
        search_res = db_con.query_search_post(keyWord)
        if len(search_res) == 0:
            search_res = (('无', '无', '无', '无', '无', '无', '无', '无','无'),)
        return search_post(searchSucc, search_res)

#对应要求的高级搜索功能1：分板块检索用户
@app.route('/search_query_insec',methods=['post','get'])
def search_query_insec(ret_content = -1,content=None,res_sec='-1'):
    secinfo = db_con.query_section_info()
    if ret_content==-1:
        return render_template('search_query_insec.html',secs=secinfo,提示=searchTip,
                               mode_sec=request.cookies.get('mode_sec'),res_sec=res_sec)
    else:
        return render_template('search_query_insec.html',secs=secinfo,提示=searchSucc,
                               content=content,mode_sec=request.cookies.get('mode_sec'),
                               res_sec=res_sec)

#对应处理高级搜索1表单
@app.route('/search_query_insec_form',methods=['post','get'])
def search_query_insec_form():
    sort_method = int(request.form.getlist('sort_method')[0])
    section_number = request.form.getlist('block_choose')[0][0] #str
    user_info = db_con.query_insec_userinfo(section_number,sort_method)
    if (request.cookies.get('uid') == 0):
        if len(user_info) == 0:
            user_info = (('无', '无', '无', '无', '无', '无', '无', '无'),)
        return search_query_insec(1, user_info,res_sec=section_number)
    else:  # 版主或管理员有权利删帖  到html其实判断了如果不是admin 即使是版主也没有删除权限
        if len(user_info) == 0:
            user_info = (('无', '无', '无', '无', '无', '无', '无', '无', '无'),)
        return search_query_insec(1, user_info,res_sec=section_number)

#对应高级搜索功能2：板块中热度最高的帖子和对应的回复用户，这个直接把所有板块对应的一个热度最高的帖子和回复用户一起返回
#管理员在这里就别有删除动作了，逻辑上不太好，帖子信息和用户信息都有
@app.route('/find_hottest_post',methods=['post','get'])
def find_hottest_post():
    ret = db_con.find_hottest_post()    #(snum,pnum,nickname)
    return render_template('find_hottest_post.html',ret_info=ret,提示=searchHotTips)

#对应高级搜索功能3：两种大于平均的帖子查询 分页的
@app.route('/find_morethan_avg1_parti/<int:pnum>',methods=['post','get'])
def find_morethan_avg1_parti(pnum):
    ret1, _ = db_con.find_morethan_avg()
    pnum = pnum-1
    Len = len(ret1)
    Len = (Len // 20) + 1
    if pnum + 1 < Len:
        ret1 = ret1[20*pnum:20*(pnum+1)]
    else:
        ret1 = ret1[20*pnum:]
    return render_template('find_morethan_avg1.html',ret1=ret1,
                           Len=Len,pnum=pnum+1,uid=request.cookies.get('uid'))

@app.route('/find_morethan_avg1/',methods=['post','get'])
def find_morethan_avg1():
    return redirect(url_for('find_morethan_avg1_parti',pnum=1))

@app.route('/find_morethan_avg2_parti/<int:pnum>',methods=['post','get'])
def find_morethan_avg2_parti(pnum):
    _, ret1 = db_con.find_morethan_avg()
    pnum = pnum - 1
    Len = len(ret1)
    Len = (Len // 20) + 1
    if pnum + 1 < Len:
        ret1 = ret1[20 * pnum:20 * (pnum + 1)]
    else:
        ret1 = ret1[20 * pnum:]
    return render_template('find_morethan_avg2.html', ret1=ret1,
                           Len=Len, pnum=pnum + 1,uid=request.cookies.get('uid'))

@app.route('/find_morethan_avg2',methods=['post','get'])
def find_morethan_avg2():
    return redirect(url_for('find_morethan_avg2_parti',pnum=1))

#对应高级搜索4：发帖数板块A>B的用户
@app.route('/find_post_A_morethan_B_form',methods=['post','get'])
def find_post_A_morethan_B_form():
    blockA = request.form.getlist('block_chooseA')[0][0]
    blockB = request.form.getlist('block_chooseB')[0][0]
    ret = db_con.find_post_A_morethan_B(blockA,blockB)
    if (request.cookies.get('uid') == 0):
        if len(ret) == 0:
            ret = (('无', '无', '无', '无', '无', '无', '无', '无'),)
        return find_post_A_morethan_B(1, ret)
    else:  # 版主或管理员有权利删帖  到html其实判断了如果不是admin 即使是版主也没有删除权限
        if len(ret) == 0:
            ret = (('无', '无', '无', '无', '无', '无', '无', '无', '无'),)
        return find_post_A_morethan_B(1, ret)

@app.route('/find_post_A_morethan_B',methods=['post','get'])
def find_post_A_morethan_B(ret_content=-1,content=None):
    secinfo = db_con.query_section_info()
    if ret_content == -1:
        return render_template('find_post_A_morethan_B.html',secs=secinfo,提示=searchTip,
                               uid=request.cookies.get('uid'))
    else:
        return render_template('find_post_A_morethan_B.html',secs=secinfo,提示=searchSucc,
                               content=content,uid=request.cookies.get('uid'))


#删除帖子
@app.route('/delete_post/<post_number>',methods=['get','post'])
def delete_post(post_number):
    db_con.delete_post(post_number)
    return render_template('search_post.html',
                               提示=adminTips[3],
                               uid=request.cookies.get('uid'))

#删除评论
@app.route('/delete_reply/<post_number>/<floor_number>',methods=['post','get'])
def delete_reply(post_number,floor_number):
    account = request.cookies['account']
    db_con.delete_reply(post_number,floor_number,account)
    return redirect(url_for('show_this_post',post_number=post_number))


# 进入搜索用户的页面，逻辑同上
@app.route('/search_user', methods=['get', 'post'])
def search_user(tip=None, data=None):
    if tip is None and data is None:
        return render_template('search_user.html',
                               提示=searchTip,
                               uid=request.cookies.get('uid'))
    else:
        return render_template('search_user.html',
                               提示=tip,
                               content=data,
                               uid=request.cookies.get('uid'))

# 搜索用户
@app.route('/search_user_form', methods=['get', 'post'])
def search_user_form():
    # 处理刷新的情况，这时没有关键词
    try:
        keyWord = request.form['keyWord']
    except:
        return search_post()
    if (request.cookies.get('uid') == 0):
        if keyWord == '':
            search_res = (('无', '无', '无', '无', '无', '无', '无', '无'),)
            return search_user(searchWarn, search_res)
        search_res = db_con.query_search_user(keyWord)
        if len(search_res) == 0:
            search_res = (('无', '无', '无', '无', '无', '无', '无', '无'),)
        return search_user(searchSucc, search_res)
    else:
        if keyWord == '':
            search_res = (('无', '无', '无', '无', '无', '无', '无', '无','无'),)
            return search_user(searchWarn, search_res)
        search_res = db_con.query_search_user(keyWord)
        if len(search_res) == 0:
            search_res = (('无', '无', '无', '无', '无', '无', '无', '无','无'),)
        return search_user(searchSucc, search_res)

#修改板块名称
@app.route('/change_name/<section_number>')
def change_name(section_number):
    return render_template('moderator_changename.html',section_number=section_number,提示=adminTips[7])

@app.route('/change_name_dbop/<section_number>',methods=['post','get'])
def change_name_dbop(section_number):
    try:
        keyWord = request.form['keyWord']
    except:
        # 重进进入搜索页面
        return search_post()
    if keyWord=='':
        return render_template('moderator_changename.html', section_number=section_number, 提示=searchWarn)
    else:
        db_con.change_section_name(section_number,keyWord)
        return render_template('moderator_changename.html', section_number=section_number, 提示=adminTips[8])


#删除用户
@app.route('/delete_user/<account>',methods=['get','post'])
def delete_user(account):
    db_con.delete_user(account)
    return render_template('search_user.html',
                           提示=adminTips[4],
                           uid=request.cookies.get('uid')
                           )

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
    app.run()
