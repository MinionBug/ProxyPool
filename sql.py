'''提供一个sql的操作接口'''
'''要做成类的样子'''

import sqlite3

def load_pool():
    conn = sqlite3.connect('proxies.db')
    global cursor = conn.cursor()
    cursor.execute('create table proxy (ip varchar(25) primary key, port varchar(6))')

def insert_proxy(ip,port):
    try:
        cursor.execute('insert into proxy (id, name) values (?,?)',(ip,port))
    except Exception as e:
        print (e)

#删除
#查询总数量
#关闭

def del_proxy():
    pass

def close_pool():
    cursor.close()
    conn.commit()
    conn.close()


