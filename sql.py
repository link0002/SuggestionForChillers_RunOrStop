#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
import pandas as pd
import datetime
pd.set_option("display.max_columns", None)


"""
注意:该连接池只适用于单个线程内
"""


class BasePymysqlPool(object):
    def __init__(self, host, port, user, passwd, db=None, charset="utf8"):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        self.charset = charset
        self.conn = None
        self.cursor = None


class PymysqlPool(BasePymysqlPool):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
            释放连接对象;conn.close()或del conn
    """
    # 连接池对象
    __pool = None

    def __init__(self, conf):
        self.conf = conf
        super(PymysqlPool, self).__init__(**self.conf)
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def __getConn(self):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if PymysqlPool.__pool is None:
            __pool = PooledDB(creator=pymysql,
                              mincached=1,
                              maxcached=20,
                              host=self.host,
                              port=self.port,
                              user=self.user,
                              passwd=self.passwd,
                              db=self.db,
                              use_unicode=True,#use_unicode=False时conversion from bytes to Decimal is not supported
                              charset=self.charset,
                              cursorclass=DictCursor)
        return __pool.connection()

    def getAll(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)

        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = []
        return result

    def getOne(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result

    def getMany(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = []
        return result

    def insertMany(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        return count

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def insert(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()

    def pandas_read(self,sql, index_col=None, coerce_float=False, params=None,
             parse_dates=None, columns=None, chunksize=None):
        return pd.read_sql(sql, con=self._conn, index_col=index_col, coerce_float=coerce_float, params=params,
             parse_dates=parse_dates, columns=columns, chunksize=chunksize)


def timestamp_to_datetime(timestamp_list, ds_type):
    if ds_type == 'datetime':
        datetime_list = []
        for cur_timestamp in timestamp_list:
            cur_datetime = datetime.datetime.combine(cur_timestamp.date(), cur_timestamp.time())
            datetime_list.append(cur_datetime)
        return datetime_list
    else:
        date_list = []
        for cur_timestamp in timestamp_list:
            cur_date = cur_timestamp.date()
            date_list.append(cur_date)
        return date_list



