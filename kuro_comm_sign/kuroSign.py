import datetime
import json
import logging
import random
import time
from apscheduler.schedulers.background import BlockingScheduler

import requests
import configparser

con = configparser.ConfigParser()

con.read('config.ini', encoding='utf-8')

config = dict(con.items('section'))

token = config["token"]
devCode = config["devcode"]
uid = config["uid"]
serverId = config["serverid"]
gameId = config["gameid"]
model = config["model"]
hour = config["hour"]
minute = config["minute"]
second = config["second"]

job_defaults = {
    'coalesce': True,
    'misfire_grace_time': None
}

scheduler = BlockingScheduler(job_defaults=job_defaults)

logging.basicConfig(filename='log.txt',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO,
                    encoding='utf-8')


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
def view_post(postId):
    url = '/forum/getPostDetail'
    post_data = {
        "isOnlyPublisher": 0,
        "postId": postId,
        "showOrderType": 2
    }

    return post(url, data=post_data)


# 点赞
def like_post(bbs, operate: int):
    url = '/forum/like'

    post_data = {
        "forumId": 3,
        "gameId": 2,
        "likeType": 1,
        "operateType": operate,
        "postCommentId": 0,
        "postCommentReplyId": 0,
        "postId": bbs[0],
        "postType": bbs[1],
        "toUserId": bbs[2],
    }

    return post(url, data=post_data)


# 获取帖子列表
def get_post_list():
    url = '/forum/list'
    post_data = {
        "forumId": 2,
        "gameId": 2,
        "pageIndex": 1,
        "pageSize": 20,
        "searchType": 3,
        "timeType": 0,
        "topicId": 0,
    }

    post_list = []

    for p in post(url, post_data)["data"]["postList"]:
        post_list.append((p["postId"], p["postType"], p["userId"]))

    return post_list


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
    while True:
        try:
            logging.info('执行用户签到!')
            comm = sign_community()
            if comm['msg'] == '请勿重复签到' or comm['success'] is True:
                logging.info('用户签到成功！')
                break
        except:
            logging.error('执行用户签到失败！')
            time.sleep(120)
            continue


@scheduler.scheduled_job('cron', hour=hour, minute=minute, second=second)
def t_role():
    while True:
        try:
            logging.info("执行角色签到!")
            role = sign_role()
            if role['msg'] == '请勿重复签到' or role['success'] is True:
                logging.info('角色签到成功！')
                break
        except:
            logging.error("无网络，执行角色签到失败")
            time.sleep(120)
            continue


@scheduler.scheduled_job('cron', hour=hour, minute=minute, second=second)
def t_view_like():
    count = 0
    while True:
        try:
            for bbs in get_post_list():
                view = view_post(bbs[0])
                time.sleep(2)
                like_1 = like_post(bbs, 1)
                time.sleep(3)
                like_2 = like_post(bbs, 2)
                if view['success'] is True and like_1["success"] is True and like_2['success'] is True:
                    count = count + 1

            if count >= 10:
                logging.info('每日任务：浏览、点赞完成！')
                break

        except:
            logging.error("无网络，每日任务：浏览、点赞失败!")
            time.sleep(120)
            continue


@scheduler.scheduled_job('cron', hour=hour, minute=minute, second=second)
def t_share():
    while True:
        try:
            logging.info("执行分享!")
            s = share()
            if s["success"] is True:
                logging.info('分享成功！')
                break
        except:
            logging.error("无网络，执行分享失败！")
            time.sleep(120)
            continue


if __name__ == '__main__':
    scheduler.start()
