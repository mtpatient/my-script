import datetime
import json
import random
import time
from apscheduler.schedulers.background import BlockingScheduler

import requests

# 环境：python3, APScheduler 具体环境准备请百度

# 用户token：app 抓包获取
token = ""
# app 抓包查看
devCode = ""  
# 用以角色签到
uid = 10000000 # 角色uid, 填你自己的角色uid
serverId = 1000  # 服务器id 星火服:1000  信标服: ?

gameId = 2  # 游戏id 战双: 2 鸣潮? 3
model = "Mi 13"  # 手机型号，可改可不改


# 每日执行时间点, 在这基础上随机等待0-30分钟
hour = 6  # 时
minute = 30  # 分
second = 0  # 秒

job_defaults = {
    'coalesce': True,
    'misfire_grace_time': None
}

scheduler = BlockingScheduler(job_defaults=job_defaults)


def post(url: str, data: dict):
    url = 'https://api.kurobbs.com' + url

    headers = {
        "osVersion": "Android",
        "lang": "zh-Hans",
        "countryCode": "CN",
        "source": "android",
        "version": "2.0.0",
        "versionCode": "2000",
        "token": token,
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "api.kurobbs.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.11.0",
        "Content-Length": "60",
        "model": model,
        "devCode": devCode
    }

    res = requests.post(url, data=data, headers=headers)

    return json.loads(res.text)


# 库街区签到
def sign_community():
    url = "/user/signIn"
    post_data = {
        "gameId": gameId
    }

    return post(url, data=post_data)


# 浏览帖子
def view_post():
    url = '/forum/getPostDetail'
    post_data = {
        "isOnlyPublisher": 0,
        "postId": 1213879409601040384,
        "showOrderType": 2
    }

    return post(url, data=post_data)


# 点赞
def like_post(operate: int):
    url = '/forum/like'

    post_data = {
        "forumId": 3,
        "gameId": 2,
        "likeType": 1,
        "operateType": operate,
        "postCommentId": 0,
        "postCommentReplyId": 0,
        "postId": 1213879409601040384,
        "postType": 1,
        "toUserId": 10015960,
    }

    return post(url, data=post_data)


# 角色签到
def sign_role():
    url = "/encourage/signIn/"

    month = datetime.datetime.today().month
    reqMonth = ''
    if month < 10:
        reqMonth = '0' + str(month)

    post_data = {
        "gameId": gameId,
        "serverId": serverId,
        "roleId": uid,
        "reqMonth": reqMonth
    }

    return post(url, data=post_data)


# 分享
def share():
    url = '/encourage/level/shareTask'

    post_data = {
        "gameId": gameId
    }

    return post(url, post_data)


@scheduler.scheduled_job('cron', hour=hour, minute=minute, second=second)
def t_comm():
    time.sleep(random.randint(0, 30) * 60)
    time.sleep(random.randint(0, 59))
    while True:
        try:
            print("执行用户签到，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            comm = sign_community()
            print(comm)
            if comm['msg'] == '请勿重复签到' or comm['success'] is True:
                print('用户签到成功！当前时间：', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
                break
        except:
            print("无网络，执行用户签到失败，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            time.sleep(120)
            continue


@scheduler.scheduled_job('cron', hour=hour, minute=minute, second=second)
def t_role():
    time.sleep(random.randint(0, 30) * 60)
    time.sleep(random.randint(0, 59))
    while True:
        try:
            print("执行角色签到，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            role = sign_role()
            print(role)
            if role['msg'] == '请勿重复签到' or role['success'] is True:
                print('角色签到成功！当前时间：', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
                break
        except:
            print("无网络，执行角色签到失败，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            time.sleep(120)
            continue


@scheduler.scheduled_job('cron', hour=hour, minute=minute, second=second)
def t_like():
    num = random.randint(6, 9)
    count = 0
    while True:
        try:
            print("执行点赞，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            like_1 = like_post(1)
            print(like_1)
            time.sleep(10)
            print("取消点赞，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            like_2 = like_post(2)
            print(like_2)
            if like_1['success'] is True and like_2['success'] is True:
                count = count + 1

            if count > num:
                break

        except:
            print("无网络，执行点赞失败，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            time.sleep(120)
            continue


@scheduler.scheduled_job('cron', hour=hour, minute=minute + 1, second=second)
def t_share():
    while True:
        try:
            print("执行分享，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            s = share()
            print(s)
            if s["success"] is True:
                break
        except:
            print("无网络，执行分享失败，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            time.sleep(120)
            continue


@scheduler.scheduled_job('cron', hour=hour, minute=minute - 1, second=second)
def t_view():
    num = random.randint(4, 5)
    count = 0
    while True:
        try:
            print("执行浏览帖子，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            view = view_post()
            print(view)
            if view["success"] is True:
                count = count + 1

            if count > num:
                break

        except:
            print("无网络，执行浏览帖子失败，当前时间：", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            time.sleep(120)
            continue


if __name__ == '__main__':
    scheduler.start()
