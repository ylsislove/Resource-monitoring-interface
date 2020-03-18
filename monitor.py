#!/usr/bin/env python
#coding=utf-8
import inspect
import time
import sys
import socket
import psutil
import MySQLdb as mysql
# 定时任务
from apscheduler.schedulers.blocking import BlockingScheduler

EXPAND = 1024 * 1024

class mon:
    def __init__(self):
        self.data = {}
        self.old_bytes_sent = psutil.net_io_counters().bytes_sent
        self.old_bytes_recv = psutil.net_io_counters().bytes_recv

    def getTime(self):
        return int(time.time())

    def getHost(self):
        return socket.gethostbyname(socket.gethostname())

    def getMemTotal(self):
        mem = psutil.virtual_memory()
        return int(mem.total / EXPAND)

    def getMemUsage(self, noBufferCache=True):
        mem = psutil.virtual_memory()
        return int(mem.used / EXPAND)

    def getMemFree(self, noBufferCache=True):
        mem = psutil.virtual_memory()
        return int(mem.total / EXPAND - mem.used / EXPAND)

    def getMemPercent(self):
        mem = psutil.virtual_memory()
        return float(mem.percent)

    def getCpuPercent(self):
        return float(psutil.cpu_percent())

    def getNetSent(self):
        netinfo = psutil.net_io_counters()
        up = netinfo.bytes_sent - self.old_bytes_sent
        self.old_bytes_sent = netinfo.bytes_sent
        return up

    def getNetRecv(self):
        netinfo = psutil.net_io_counters()
        down = netinfo.bytes_recv - self.old_bytes_recv
        self.old_bytes_recv = netinfo.bytes_recv
        return down

    def runAllGet(self):
        #自动获取mon类里的所有getXXX方法，用XXX作为key，getXXX()的返回值作为value，构造字典
        for fun in inspect.getmembers(self, predicate=inspect.ismethod):
            if fun[0][:3] == 'get':
                self.data[fun[0][3:]] = fun[1]()
        return self.data

def job():
    data = m.runAllGet()
    # print(data)
    try:
        sql = "insert into stat(time, host, mem_free, mem_usage, mem_total, mem_percent, cpu_percent, network_sent, network_recv) \
                values (%d, '%s', %d, %d, %d, %f, %f, %d, %d)" % (int(data['Time']), data['Host'], data['MemFree'], data['MemUsage'], 
                data['MemTotal'], float(data['MemPercent']), float(data["CpuPercent"]), data["NetSent"], data["NetRecv"])
        ret = c.execute(sql)
    except mysql.IntegrityError:
        pass

def clear():
    now = int(time.time())
    try:
        # 每隔一个小时，清理一个小时前的数据
        sql = "delete from stat where time < %d - 3600" % now
        ret = c.execute(sql)
    except mysql.IntegrityError:
        pass

def heartbeat():
    # print("{} 正在监听中...".format(str(time.ctime())))
    sys.stdout.write("\r{} 正在监听中...".format(str(time.ctime())))
    sys.stdout.flush()


# 连接数据库
db = mysql.connect(user='root', passwd='root123456', db='falcon', charset='utf8')
db.autocommit(True)
c = db.cursor()
# 创建监听程序对象
m = mon()

if __name__ == "__main__":
    heartbeat()
    # 这里是定时任务
    scheduler = BlockingScheduler()
    # 间隔1s查询当前状态
    scheduler.add_job(job, 'interval', seconds=1)
    # 每隔1个小时，清理1个小时前的数据
    scheduler.add_job(clear, 'interval', seconds=3600)
    # 每隔1分钟，打印当前监听程序是否在线
    scheduler.add_job(heartbeat, 'interval', seconds=60)
    scheduler.start()
