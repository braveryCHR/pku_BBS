import pymysql
import sys
import os


class DB:
    def __init__(self,DB_conf):
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
        sql2='''create table if not exists sec_info(
            section_number  INT not null,
            section_name    VARCHAR(40) not null,
            count_post_number INT ,
            avg_reply_number DOUBLE ,
            avg_click_number DOUBLE ,
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
            FOREIGN KEY(section_number) REFERENCES sec_info(section_number),
            FOREIGN KEY(account) REFERENCES user_info(account),
            FOREIGN KEY(account) REFERENCES user_info(account)
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
            FOREIGN KEY(post_number) REFERENCES post_info(post_number),
            FOREIGN KEY(account) REFERENCES user_info(account)
        )
        '''
        self.cursor.execute(sql4)
        sql5 = '''create table if not exists moderator_info(
            section_number INT,
            account VARCHAR (20),
            PRIMARY KEY(section_number,account),
            FOREIGN KEY(section_number) REFERENCES sec_info(section_number),
            FOREIGN KEY(account) REFERENCES user_info(account)
        ) 
        '''
        self.cursor.execute(sql5)
        sql6 = '''create table if not exists recentpost_info(
            account VARCHAR (20),
            post_time DATETIME,
            post_number INT,
            PRIMARY KEY(account,post_time),
            FOREIGN KEY(account) REFERENCES user_info(account),
            FOREIGN KEY(post_number) REFERENCES post_info(post_number)
        )
        '''
        self.cursor.execute(sql6)
        sql7 = '''create table if not exists recentreply_info(
            account VARCHAR(20),
            reply_time DATETIME,
            post_number INT,
            reply_floor INT,
            PRIMARY KEY(account,reply_time),
            FOREIGN KEY(account) REFERENCES user_info(account),
            FOREIGN KEY(post_number) REFERENCES post_info(post_number)
        )
        '''
        self.cursor.execute(sql7)

