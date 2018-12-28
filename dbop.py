import pymysql
import random
import string
from datetime import datetime
from xml_generate import generate_user_records
from faker import Faker
from datetime import datetime


class DB:
    def __init__(self, DB_conf):
        self.database = pymysql.connect(**DB_conf)
        self.cursor = self.database.cursor()
        sql1 = '''create table if not exists user_info(
            account   varchar(20) not null,
            nickname  varchar(20) not null,
            password  varchar(20) not null,
            birthday  DATE ,
            gender    SMALLINT ,
            email     varchar(40),
            ulevel    SMALLINT ,
            join_date DATETIME,
            uidentity SMALLINT,
            PRIMARY KEY (account),
            CHECK((gender = 0 or gender = 1)
            and ulevel BETWEEN 1 and 100
            and (uidentity = 0 or uidentity = 1 or uidentity = 2 )
              )
            )    
        '''
        self.cursor.execute(sql1)
        sql2 = '''create table if not exists sec_info(
            section_number  INT not null,
            section_name    VARCHAR(40) not null,
          PRIMARY KEY(section_number)
        )
        '''
        self.cursor.execute(sql2)
        sql3 = '''create table if not exists post_info(
            post_number INT not null,
            section_number INT not null,
            account    varchar(20) not null,
            nickname   varchar(20) not null,
            post_title varchar(50),
            post_content text,
            post_time DATETIME,
            click_number  INT,
            reply_number  INT,
            last_reply_time  DATETIME,
            last_reply_account VARCHAR(20),
            PRIMARY KEY(post_number),
            FOREIGN KEY(section_number) REFERENCES sec_info(section_number) on DELETE CASCADE on UPDATE CASCADE,
            FOREIGN KEY(account) REFERENCES user_info(account) on DELETE CASCADE on UPDATE CASCADE,
            FOREIGN KEY(last_reply_account) REFERENCES user_info(account) on DELETE CASCADE on UPDATE CASCADE
        )
        '''

        self.cursor.execute(sql3)
        sql4 = '''create table if not exists reply_info(
            post_number INT not null,
            reply_floor INT not null,
            account   VARCHAR (20) not null,
            nickname  VARCHAR(20) not null,
            reply_title VARCHAR(50),
            reply_content text,
            reply_time  DATETIME not null,
            like_num  INT,
            PRIMARY KEY(post_number,reply_floor),
            FOREIGN KEY(post_number) REFERENCES post_info(post_number) on DELETE CASCADE on UPDATE CASCADE,
            FOREIGN KEY(account) REFERENCES user_info(account) on DELETE CASCADE on UPDATE CASCADE
        )
        '''
        self.cursor.execute(sql4)
        sql5 = '''create table if not exists moderator_info(
            section_number INT,
            account VARCHAR (20),
            PRIMARY KEY(section_number,account),
            FOREIGN KEY(section_number) REFERENCES sec_info(section_number)on DELETE CASCADE on UPDATE CASCADE,
            FOREIGN KEY(account) REFERENCES user_info(account)on DELETE CASCADE on UPDATE CASCADE
        ) 
        '''
        self.cursor.execute(sql5)
     #   sql6 = '''create table if not exists recentpost_info(
     #       account VARCHAR (20),
     #       post_number INT,
     #       post_time DATETIME,
     #       PRIMARY KEY(account,post_number),
     #       FOREIGN KEY(account) REFERENCES user_info(account)on DELETE CASCADE on UPDATE CASCADE,
     #       FOREIGN KEY(post_number) REFERENCES post_info(post_number)on DELETE CASCADE on UPDATE CASCADE
     #   )
      #  '''
        #为了实现触发器，增加管理员信箱
        sql8 = '''create table if not exists dba_mailbox(
        sender VARCHAR(20),
        content text,
        if_read SMALLINT,
        tag_time datetime,
        check(if_read = 0 or if_read = 1)
        )
        '''
        self.cursor.execute(sql8)
        # 创建触发器 语法检查ok
        sql9 = '''create trigger warn_WaterUser after insert on post_info 
        for each row 
        BEGIN 
        DECLARE countt INT;
        set countt=(select count(*) from post_info WHERE (
        TIMESTAMPDIFF(MINUTE,post_time,new.post_time)<=10));
        if (countt>10)
        THEN
          insert into dba_mailbox(sender,content,if_read,tag_time) values('systems',new.account,0,new.post_time); 
             end if;   
        END '''

        sql_d = "DROP TRIGGER IF EXISTS warn_WaterUser;"
        self.cursor.execute(sql_d)
        self.database.commit()
        self.cursor.execute(sql9)
        self.database.commit()

    def query_top10_clicktimes(self):  # 找出全站点击数前10的帖子
        sql = '''
                select post_number,section_name,post_title,nickname,
                click_number,reply_number,post_time,last_reply_time
                from post_info,sec_info
                where post_info.section_number = sec_info.section_number
                order by click_number DESC
              '''
        try:
            self.cursor.execute(sql)
        except:
            self.database.rollback()
        res = self.cursor.fetchmany(10)
        return res

    def query_top10_replytimes(self):  # 找出全站回复数前10 的帖子
        sql = '''
                select post_number,section_name,post_title,nickname,
                click_number,reply_number,post_time,last_reply_time
                from post_info,sec_info
                where post_info.section_number = sec_info.section_number
                order by reply_number DESC
              '''
        try:
            self.cursor.execute(sql)
        except:
            self.database.rollback()
        res = self.cursor.fetchmany(10)
        return res

    def query_insec_userinfo(self, sec_num, sort_method):  # 按板块查找此板块用户的信息，sort_method = 0,发帖总数排； =1，回帖总数排；
        sql_1 = "select user_info.account,user_info.nickname,user_info.birthday,\
        user_info.gender,user_info.email,user_info.ulevel,user_info.join_date, \
        count(post_info.post_number) as count_post from user_info NATURAL INNER JOIN post_info\
        WHERE post_info.section_number = '%s'\
        GROUP BY user_info.account,user_info.nickname,user_info.birthday,\
        user_info.gender,user_info.email,user_info.ulevel,user_info.join_date\
        ORDER BY count_post DESC " % \
                (sec_num)  # 这个句子对应按发帖总数排

        sql_2 = "select user_info.account,user_info.nickname,user_info.birthday,\
        user_info.gender,user_info.email,user_info.ulevel,user_info.join_date,\
        count(*) as count_reply from user_info NATURAL INNER JOIN reply_info\
        WHERE reply_info.post_number IN (SELECT post_number from post_info WHERE section_number = '%s')\
        GROUP BY  user_info.account,user_info.nickname,user_info.birthday,\
        user_info.gender,user_info.email,user_info.ulevel,user_info.join_date\
        ORDER BY count_reply DESC" % \
                (sec_num)  # 这个句子对应按回复总数排

        if sort_method == 0:
            try:
                self.cursor.execute(sql_1)
                self.database.commit()
            except:
                self.database.rollback()
            ret = self.cursor.fetchall()
            return ret
        else:
            try:
                self.cursor.execute(sql_2)
                self.database.commit()
            except:
                self.database.rollback()
            ret = self.cursor.fetchall()
            return ret

    def find_hottest_post(self):
        # MySQL中，timestampdiff：时间小的放在前边
        sql1 = '''create temporary table hottest(
        section_number  INT,
        post_number INT,
        PRIMARY KEY(section_number,post_number)
        )
        '''  # 临时表 因为MySQL不支持with语句
        self.cursor.execute(sql1)
        self.database.commit()

        sql_secnum = "select count(*) from sec_info"  # 找出板块总数
        self.cursor.execute(sql_secnum)
        sec_num = self.cursor.fetchone()[0]
        for i in range(sec_num):  # 对于每个板块开始找
            sql2 = "select section_number,post_number, \
        TIMESTAMPDIFF(year,post_time,last_reply_time) as dy,\
        TIMESTAMPDIFF(month,post_time,last_reply_time) as dm,\
        TIMESTAMPDIFF(DAY,post_time,last_reply_time) as dd,\
        TIMESTAMPDIFF(HOUR,post_time,last_reply_time) as dh,\
        TIMESTAMPDIFF(MINUTE,post_time,last_reply_time) as di,\
        TIMESTAMPDIFF(SECOND,post_time,last_reply_time) AS ds from post_info\
        WHERE section_number = %s \
        ORDER BY dy DESC,dm DESC,dd DESC, dh DESC,di DESC,ds DESC " % \
                   (i)  # 按照热度也就是时间差排序
            self.cursor.execute(sql2)
            ins_tmp = self.cursor.fetchone()  # 拿出时间差最长的那个也就是热度最高的帖子
            sql_ins = "insert into hottest values(%s,%s)" % \
                      ins_tmp[0:2]  # 插入临时表
            self.cursor.execute(sql_ins)
            self.database.commit()
        sql_3 = '''select distinct section_number,post_number,nickname 
        from hottest NATURAL INNER JOIN reply_info
        ORDER BY section_number ASC,post_number ASC
        '''  # 去重列出所有该帖子的昵称
        self.cursor.execute(sql_3)
        ret = self.cursor.fetchall()

        sql_d = "DROP TEMPORARY TABLE IF EXISTS hottest"  # 删临时表
        self.cursor.execute(sql_d)
        self.database.commit()
        return ret

    def find_morethan_avg(self):
        sql_secnum = "select count(*) from sec_info"  # 计算板块数
        self.cursor.execute(sql_secnum)
        sec_num = self.cursor.fetchone()[0]

        # 返回点击数大于全站平均点击数的帖子，按section和post-number升序
        sql_avgclick = "select avg(click_number) from post_info"
        self.cursor.execute(sql_avgclick)
        avgc = [self.cursor.fetchone()[0]]
        avgct = tuple(avgc)
        sql1 = "select post_number,section_number,account,post_title,click_number \
                 from post_info where( click_number > %s)  \
               order BY  section_number ASC,click_number DESC" % \
               (avgc[0])
        self.cursor.execute(sql1)
        ret10 = self.cursor.fetchall()  # >avg的帖子
        ret1 = []
        for itrr in ret10:
            ret1.append(itrr + avgct)

        # 建立临时表
        sql_tmp1 = '''create temporary table user_tmp(
                    section_number int,
                    account varchar(20) not null,
                    count_reply int,
                    avg_reply int
                    )
                    '''
        self.cursor.execute(sql_tmp1)
        self.database.commit()
        for i in range(sec_num):
            # 拿出这个板块每个用户的回帖总数
            sql_avgrpl = "select account,count(*) from reply_info \
                         where(post_number in (select post_number from post_info where section_number = %s))\
                         group by account" % \
                         (i)

            # 插入tmp1： user_tmp表中
            self.cursor.execute(sql_avgrpl)
            tt = [i]
            tt1 = tuple(tt)
            avgrpl = self.cursor.fetchall()
            avgrpl2 = []
            for itr in avgrpl:
                avgrpl2.append(tt1 + itr)
            sql_avgrpl_ins = "insert into user_tmp(section_number,account,count_reply) values(%s,%s,%s)"
            self.cursor.executemany(sql_avgrpl_ins, avgrpl2)
            self.database.commit()

            # 聚合出该板块的平均回复数
            sql_avgrpl1 = "select avg(count_reply) from user_tmp \
                          where section_number = %s" % (i)
            self.cursor.execute(sql_avgrpl1)
            avgrpl_i = self.cursor.fetchone()[0]

            # 更新临时表中avg列
            sql_upd = "update user_tmp set avg_reply = %s  \
                      where section_number = %s" % \
                      (avgrpl_i, i)
            self.cursor.execute(sql_upd)
            self.database.commit()
        # 最后找出回复数大于该板块平均回复数的
        sql2 = "select section_number,account,nickname,count_reply,avg_reply  \
               from user_tmp NATURAL INNER JOIN user_info  where count_reply > avg_reply"
        self.cursor.execute(sql2)
        ret2 = self.cursor.fetchall()
        sql3 = "DROP TEMPORARY TABLE IF EXISTS user_tmp"
        self.cursor.execute(sql3)
        self.database.commit()
        return ret1, ret2

    def find_post_A_morethan_B(self, A, B):
        # a,b 为section_number
        # 搞两个临时表比较，最后返回结果
        sql1 = "select account,count(*) from post_info \
               where section_number = %s \
               GROUP BY account" % (A)
        sql2 = "select account,count(*) from post_info \
               where section_number = %s \
               GROUP BY account" % (B)
        sql_tmpta = '''create temporary table usera(
        account VARCHAR(20),
        countA  int
        )'''
        sql_tmptb = '''create temporary table userb(
                account VARCHAR(20),
                countB  int
                )'''
        self.cursor.execute(sql_tmpta)
        self.database.commit()
        self.cursor.execute(sql_tmptb)
        self.database.commit()

        self.cursor.execute(sql1)
        md1 = self.cursor.fetchall()
        sqlins1 = "insert into usera values(%s,%s)"
        self.cursor.executemany(sqlins1, md1)
        self.database.commit()

        self.cursor.execute(sql2)
        md2 = self.cursor.fetchall()
        sqlins2 = "insert into userb values(%s,%s)"
        self.cursor.executemany(sqlins2, md2)
        self.database.commit()

        sqlret = '''select * from usera NATURAL INNER JOIN userb \
                where(countA>countB)
        '''
        self.cursor.execute(sqlret)
        ret = self.cursor.fetchall()
        sql_del = "DROP TEMPORARY TABLE IF EXISTS usera"
        sql_del1 = "DROP TEMPORARY TABLE IF EXISTS userb"
        self.cursor.execute(sql_del)
        self.cursor.execute(sql_del1)
        self.database.commit()
        return ret

    def get_person_ConcretInfo(self, accountp):
        # 近期：最近十天
        Username = accountp
        sql1 = "select birthday,gender,ulevel from user_info where account = '%s'" % (accountp)
        self.cursor.execute(sql1)
        temp = self.cursor.fetchone()
        Birthday = str(temp[0])
        nowtime = datetime.now()
        Age = int(nowtime.year) - int(Birthday[0:4])
        if (int(nowtime.month) < int(Birthday[5:7])):
            Age -= 1
        elif (int(nowtime.month) == int(Birthday[5:7]) and int(nowtime.day) < int(Birthday[8:])):
            Age -= 1
        Gender = temp[1]
        Ulevel = temp[2]
        nowtime = str(nowtime)[:-7]  # 截断秒之后
        BasicInfo = [Gender, Age, Ulevel, Birthday]
        sql2 = "select * from post_info  \
               where account = '%s' and TIMESTAMPDIFF(day,post_time,'%s')<=10 \
               order by UNIX_TIMESTAMP(post_time) DESC" % \
               (accountp, nowtime)
        self.cursor.execute(sql2)
        Posts = self.cursor.fetchall()
        sql3 = "select * from reply_info \
               where account = '%s' and TIMESTAMPDIFF(day,reply_time,'%s')<=10 \
               order by UNIX_TIMESTAMP(reply_time) DESC" % \
               (accountp, nowtime)
        self.cursor.execute(sql3)
        Replies = self.cursor.fetchall()
        generate_user_records(Username, BasicInfo, Posts, Replies)
        # return Username,BasicInfo,Posts,Replies

    def insert_user_info(self, account, password, nickname,
                         birthday, gender, email,
                         ulevel, join_date, uidentity):
        check_sql = "select count(*) from user_info WHERE account = '%s'" % (account)
        # print(check_sql)
        self.cursor.execute(check_sql)
        result = self.cursor.fetchall()[0][0]
        self.database.commit()
        # print(result)
        if result == 0:
            sql = '''
                  insert into user_info(account,password,nickname,birthday,gender,email,ulevel,join_date,uidentity)
                  values('%s','%s','%s','%s','%s','%s','%s','%s','%s')
                  ''' % (account, password, nickname, birthday, gender, email, ulevel, join_date, uidentity)
            print(sql)
            self.cursor.execute(sql)
            self.database.commit()
            return True
        else:
            return False

    def login_check(self, account, password):
        check_sql = "select password from user_info WHERE account = '%s'" % (account)
        result = self.cursor.execute(check_sql)
        res_pwd = self.cursor.fetchall()
        if len(res_pwd) == 0:
            print("未查询到账号%s" % (account))
            return False
        else:
            print("查询到账号%s，您提供的密码为%s，实际密码为%s" % (account, password, res_pwd))
            print(res_pwd)
            return res_pwd[0][0] == password

    def query_user_info(self, account):
        sql = "select * from user_info where account = '%s'" % (account)
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.database.commit()
        return result

    def query_all_section_info(self):
        section_sql = '''
            select section_number,section_name
            from sec_info
        '''
        self.cursor.execute(section_sql)
        sec_info = self.cursor.fetchall()
        sec_post_num = []
        for row in sec_info:
            post_sql = '''
                select count(*) from post_info where section_number = %s
            ''' % (row[0])
            self.cursor.execute(post_sql)
            res = self.cursor.fetchall()[0][0]
            sec_post_num.append(res)
        res_info = zip(sec_info, sec_post_num)
        return res_info

    def query_this_section_info(self, section_number):
        sql = '''
            select post_number,post_title,nickname,
            click_number,reply_number,post_time,last_reply_time
            from post_info
            where section_number = %s
            order by post_time DESC ,last_reply_time DESC 
        ''' % (section_number)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def query_all_post(self):
        sql = '''
                select post_number,section_name,post_title,nickname,
                click_number,reply_number,post_time,last_reply_time
                from post_info,sec_info
                where post_info.section_number = sec_info.section_number
                order by post_time DESC ,last_reply_time DESC 
                '''
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def query_this_post(self, post_number):
        sql1 = '''
            select click_number from post_info
            where post_number = '%s'
        ''' % (post_number)
        self.cursor.execute(sql1)
        click_number = self.cursor.fetchall()[0][0] + 1
        sql2 = '''
            update post_info
            set click_number = %s
            where post_number = '%s'
        ''' % (click_number, post_number)
        self.cursor.execute(sql2)
        post_sql = '''
            select * from post_info
            where post_number = %s
        ''' % (post_number)
        self.cursor.execute(post_sql)
        post_res = self.cursor.fetchall()
        reply_sql = '''
            select * from reply_info
            where post_number = %s
            order by reply_floor asc
        ''' % (post_number)
        # print(res)
        self.cursor.execute(reply_sql)
        reply_res = self.cursor.fetchall()
        return post_res, reply_res

    # 该函数已经过修改以产生更加真实的数据
    def generate_data(self):
        # 随机生成一些用户
        fake = Faker("zh_CN")
        dtime = '{}-{}-{}-{}-{}-{}'
        dtime2 = '{}-{}-{}'
        sql = '''
              insert into user_info(account,nickname,password,birthday,gender,ulevel,email,uidentity,join_date) 
              values(%s,%s,%s,%s,%s,%s,%s,%s,%s)
             '''
        init_acc = 'account_'
        init_nic = 'nickname_'
        in_arr = []
        in_arr_mod = []
        for i in range(200):
            randpwd = random.randint(100000, 999999)
            randpwd = str(randpwd)
            Y1 = random.randint(1990, 2000)  # 发帖时间  xjb搞随机
            M1 = random.randint(1, 12)
            D1 = random.randint(1, 28)
            gd = str(random.randint(0, 1))
            ulevel = str(random.randint(1, 100))
            uidentity = str(random.randint(0, 2))
            join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            in_arr.append(
                (init_acc + str(i), fake.name(), randpwd, dtime2.format(Y1, M1, D1), gd, ulevel,
                 fake.email(), uidentity, join_date))
            if uidentity == "1":
                randsec = random.randint(0,9)
                in_arr_mod.append((randsec,init_acc + str(i),))
        self.cursor.executemany(sql, in_arr)
        self.database.commit()
        sql_md = '''insert into moderator_info(section_number,account)
        values(%s,%s)
        '''
        print("用户生成完毕")
        # 随机生成一些版块
        in_arr.clear()
        sql = 'insert into sec_info(section_number,section_name) values(%s,%s)'
        for i in range(10):
            in_arr.append((str(i), fake.city_name()))
        self.cursor.executemany(sql, in_arr)
        self.database.commit()
        print("板块生成完毕")
        ##随机生成发帖的人 点击数
        in_arr.clear()
        in_arr1 = []
        sql = '''insert into post_info(post_number,section_number,account,
                  nickname,post_title,post_content,post_time,click_number,reply_number,last_reply_time) 
                  values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        sql_replypost = '''insert into reply_info(post_number,reply_floor,account,
                          nickname,reply_content,reply_time,like_num) values(%s,%s,%s,%s,%s,%s,%s)'''
        ct_pnum = 0
        for i in range(10):  # section num
            print(i)
            num_post = random.randint(200, 500)
            for j in range(1, num_post + 1):
                ct_pnum += 1
                Y1 = random.randint(2000, 2005)  # 发帖时间  xjb搞随机
                M1 = random.randint(1, 3)
                D1 = random.randint(1, 10)
                H1 = random.randint(0, 3)
                i1 = random.randint(0, 15)
                S1 = random.randint(0, 15)
                title_len = random.randint(5, 10)
                post_title = fake.text(max_nb_chars=title_len, ext_word_list=None)
                content_len = random.randint(800, 1400)
                post_content = fake.text(max_nb_chars=content_len, ext_word_list=None)
                post_content.replace("\n", "<br>")
                # 随机生成发帖人
                an = random.randint(0, 199)
                self.cursor.execute(sql, (str(ct_pnum), str(i), init_acc + str(an), init_nic + str(an),
                                          post_title, post_content,
                                          dtime.format(Y1, M1, D1, H1, i1, S1),
                                          str(random.randint(200, 10000)), str(0),
                                          dtime.format(Y1, M1, D1, H1, i1, S1)))
                # print(dtime.format(Y1, M1, D1, H1, i1, S1))
                self.database.commit()
                last_rep = [Y1, M1, D1, H1, i1, S1]
                # 生成对应的回帖数据
                floor_num = random.randint(5, 10)
                in_arr1.clear()
                for t in range(1, floor_num + 1):
                    a_reply = random.randint(0, 199)  # 回帖人和回帖时间
                    YT1 = last_rep[0] + random.randint(0, 1)
                    MT1 = min(last_rep[1] + random.randint(0, 1),12)
                    DT1 = min(last_rep[2] + random.randint(0, 2),28)
                    HT1 = min(last_rep[3] + random.randint(0, 2),23)
                    iT1 = min(last_rep[4] + random.randint(0, 5),59)
                    ST1 = min(last_rep[5] + random.randint(0, 5),59)
                    content_len = random.randint(100, 300)
                    reply_content = fake.text(max_nb_chars=content_len, ext_word_list=None)
                    like_num = random.randint(10, 50)
                    in_arr1.append(
                        (str(ct_pnum), str(t), init_acc + str(a_reply), init_nic + str(a_reply), reply_content,
                         dtime.format(YT1, MT1, DT1, HT1, iT1, ST1), like_num))
                    last_rep = [YT1, MT1, DT1, HT1, iT1, ST1]
                self.cursor.executemany(sql_replypost, in_arr1)
                self.database.commit()
                sql_upd = "UPDATE post_info SET last_reply_time ='%s' WHERE post_number = '%s' " % \
                          (dtime.format(last_rep[0], last_rep[1], last_rep[2], last_rep[3], last_rep[4], last_rep[5]),
                           str(ct_pnum))
                self.cursor.execute(sql_upd)
                self.database.commit()
        print("帖子与回复信息生成完毕")
        self.update_reply_number()
        self.update_nikename()
        self.cursor.executemany(sql_md, in_arr_mod)
        self.database.commit()
        print("版主生成完毕")
        print("数据生成全部完成")

    # 由于生成数据的函数没有处理replynum，这里进行处理
    def update_reply_number(self):
        sql = '''
            update post_info
            set reply_number = (
              select count(*) from reply_info
              where reply_info.post_number = post_info.post_number
            )
        '''
        self.cursor.execute(sql)
        self.database.commit()

    def update_nikename(self):
        post_sql = '''
            update post_info
            set nickname = (
              select nickname from user_info
              where post_info.account = user_info.account
            )
        '''
        reply_sql = '''
            update reply_info
            set nickname = (
              select nickname from user_info
              where reply_info.account = user_info.account
            )
        '''
        self.cursor.execute(post_sql)
        self.cursor.execute(reply_sql)
        self.database.commit()

    def insert_reply_content(self, account, post_number, reply_content, reply_time):
        sql1 = '''
            select count(*) from reply_info
            where post_number = %s
        ''' % (post_number)
        self.cursor.execute(sql1)
        reply_floor = self.cursor.fetchall()[0][0] + 1
        sql2 = '''
            select nickname from user_info
            where account = '%s'
        ''' % (account)
        self.cursor.execute(sql2)
        nickname = self.cursor.fetchall()[0][0]
        sql3 = '''
            insert into reply_info
            (post_number,reply_floor,account,nickname,reply_content,reply_time,like_num)
            VALUES 
            (%s,%s,'%s','%s','%s','%s',%s)
        ''' % (post_number, reply_floor, account, nickname, reply_content, reply_time, 0)
        # print(sql3)
        self.cursor.execute(sql3)
        sql4 = '''
            update post_info
            set last_reply_time = '%s' 
            where post_number = %s 
        ''' % (reply_time, post_number)
        self.cursor.execute(sql4)
        sql5 = '''
            select reply_number from post_info
            where post_number = '%s'
        ''' % (post_number)
        self.cursor.execute(sql5)
        reply_number = self.cursor.fetchall()[0][0] + 1
        sql5 = '''
            update post_info
            set reply_number = %s
            where post_number = '%s'
        ''' % (reply_number, post_number)
        self.cursor.execute(sql5)
        self.database.commit()

    def query_section_info(self):
        sql = '''
            select * from sec_info
        '''
        self.cursor.execute(sql)
        section = self.cursor.fetchall()
        self.database.commit()
        return section

    def query_one_section(self,sec_num):
        sql='''select * from sec_info where section_number= '%s'
        ''' %(sec_num)
        self.cursor.execute(sql)
        ret = self.cursor.fetchone()
        self.database.commit()
        return ret

    def insert_post(self, section_number, account, post_title,
                    post_content, post_time):
        sql1 = '''
            select max(post_number) from post_info
        '''
        self.cursor.execute(sql1)
        post_number = self.cursor.fetchall()[0][0] + 1
        sql2 = '''
            select nickname from user_info
            where account = '%s'
        ''' % (account)
        self.cursor.execute(sql2)
        nickname = self.cursor.fetchall()[0][0]
        sql3 = '''
            insert into post_info
            (post_number,section_number,account,nickname,post_title,
            post_content,post_time,click_number,reply_number,last_reply_time)
            values
            (%s,%s,'%s','%s','%s','%s','%s',%s,%s,'%s')
        ''' % (post_number, section_number, account, nickname, post_title,
               post_content, post_time, 0, 0, post_time)
        self.cursor.execute(sql3)
        self.database.commit()
      #  sql4='''insert into recentpost_info
      #    (account,post_number,post_time)values('%s',%s,'%s')
      #  ''' % (account, post_number, post_time)
      #  self.cursor.execute(sql4)
      #  self.database.commit()
        return post_number

    def query_search_post(self, keyWord):
        sql = '''
            select post_number,section_name,post_title,nickname,
            click_number,reply_number,post_time,last_reply_time
            from post_info,sec_info
            where post_info.section_number = sec_info.section_number
              and post_info.post_title like '%s'
            order by post_time DESC ,last_reply_time DESC 
        ''' % ('%' + keyWord + '%')
        self.cursor.execute(sql)
        search_res = self.cursor.fetchall()
        self.database.commit()
        return search_res

    def query_search_user(self, keyWord):
        sql = '''
            select account,nickname,birthday,gender,
            email,ulevel,join_date,uidentity
            from user_info
            where account like '%s' or nickname like '%s'
        ''' % ('%' + keyWord + '%', '%' + keyWord + '%')
        self.cursor.execute(sql)
        search_res = self.cursor.fetchall()
        self.database.commit()
        return search_res

    def update_likenum(self,post_number,floor_number):
        sql = '''update reply_info set like_num = like_num + 1 
        where post_number = '%s' and reply_floor = '%s'
        ''' %(str(post_number),str(floor_number))
        self.cursor.execute(sql)
        self.database.commit()

    def insert_moderator_info(self,account,section_number):
        sql='''insert into moderator_info(section_number,account) 
        values('%s','%s')
        ''' %(section_number,account)
        self.cursor.execute(sql)
        self.database.commit()

    def get_user_identity(self,account):
        sql ='''select uidentity from user_info 
        where account = '%s'
        ''' %(account)
        self.cursor.execute(sql)
        ret = self.cursor.fetchone()[0]
        return ret

    def get_moderator_sec(self,account):
        sql = '''select section_number from moderator_info where account='%s'
        ''' %(account)
        self.cursor.execute(sql)
        ret = str(self.cursor.fetchone()[0])
        return ret

    def delete_post(self,post_number):
        sql='''delete from post_info where post_number = '%s'
        ''' %(post_number)
        self.cursor.execute(sql)
        self.database.commit()

    def delete_user(self,account):
        sql = '''delete from user_info where account='%s'
        ''' %(account)
        self.cursor.execute(sql)
        self.database.commit()

    def change_section_name(self,section_number,new_name):
        sql='''update sec_info set section_name='%s'
        where section_number='%s'
        ''' %(new_name,section_number)
        self.cursor.execute(sql)
        self.database.commit()

    def delete_reply(self,post_number,floor_number,account):
        sql1 = '''
            select account from post_info
            WHERE post_number = '%s'
        '''%(post_number)
        self.cursor.execute(sql1)
        self.database.commit()
        post_account = self.cursor.fetchall()[0][0]
        print(1)
        if post_account != account:
            return False
        print(2)
        sql='''delete from reply_info 
        where post_number='%s' and reply_floor='%s'
        '''%(post_number,floor_number)
        self.cursor.execute(sql)
        self.database.commit()
        #还得更新比他小的
        sql2 = '''update reply_info set reply_floor=reply_floor-1
        where post_number = '%s' and reply_floor > '%s'
        ''' %(post_number,floor_number)
        self.cursor.execute(sql2)
        self.database.commit()
        # 减少帖子楼层数
        sql3 = '''
            update post_info
            set reply_number = (
              select count(*) from reply_info
              where post_number = %s
            ) 
            WHERE post_number = %s
        '''%(post_number,post_number)
        self.cursor.execute(sql3)
        self.database.commit()
        print("删除陈宫")
        return True

    def fetch_adminmail(self):
        sql = '''select * from dba_mailbox'''
        self.cursor.execute(sql)
        self.database.commit()
        ret = self.cursor.fetchall()
        sql2 = '''select count(*) from dba_mailbox where if_read=0'''
        self.cursor.execute(sql2)
        self.database.commit()
        read_tag = int(self.cursor.fetchone()[0])
        return ret,read_tag

    def delete_adminmail(self,tag_time):
        sql = '''delete from dba_mailbox where tag_time='%s'
        ''' %(tag_time)
        self.cursor.execute(sql)
        self.database.commit()

    def read_adminmail(self,tag_time):
        sql = '''update dba_mailbox set if_read=1 where tag_time='%s'
        ''' % (tag_time)
        self.cursor.execute(sql)
        self.database.commit()

from bbs import *

if __name__ == '__main__':
    db_con = DB(DB_conf)
    db_con.generate_data()
    # db_con.update_reply_number()
    # fake = Faker("zh_CN")
    # print(fake.text(max_nb_chars=2000, ext_word_list=None))
