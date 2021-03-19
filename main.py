#!/usr/bin/env python
# --coding:utf-8--

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import path
from threading import Timer
import time
import datetime
import json
import requests
from urllib import request, parse

APP_ID = "cli_a080528f7df0d009"
APP_SECRET = "asVEUWdGHCKFvjRRucSwRnWEiNYNR5F5"
APP_VERIFICATION_TOKEN = "OzzXd5aHj3TkFVtJkdg1kelrcESO3onQ"


def get_tenant_access_token():
    url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal/"
    headers = {
        "Content-Type": "application/json"
    }
    req_body = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }

    data = bytes(json.dumps(req_body), encoding='utf8')
    req = request.Request(url=url, data=data, headers=headers, method='POST')
    try:
        response = request.urlopen(req)
    except Exception as e:
        print(e.read().decode())
        return ""

    rsp_body = response.read().decode('utf-8')
    rsp_dict = json.loads(rsp_body)
    code = rsp_dict.get("code", -1)
    if code != 0:
        print("get tenant_access_token error, code =", code)
        return ""
    return rsp_dict.get("tenant_access_token", "")


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        # 解析请求 body
        req_body = self.rfile.read(int(self.headers['content-length']))
        obj = json.loads(req_body.decode("utf-8"))
        print('-------->')
        # 校验 verification token 是否匹配，token 不匹配说明该回调并非来自开发平台
        token = obj.get("token", "")
        if token != APP_VERIFICATION_TOKEN:
            print("verification token not match, token =", token)
            self.response(json.dumps({}))
            return

        # 根据 type 处理不同类型事件
        type = obj.get("type", "")
        if "url_verification" == type:  # 验证请求 URL 是否有效
            self.handle_request_url_verify(obj)
        elif "event_callback" == type:  # 事件回调
            # 获取事件内容和类型，并进行相应处理，此处只关注给机器人推送的消息事件
            event = obj.get("event")
            if event.get("type", "") == "message":
                self.handle_message(event)
                return
        print('------>')
        return

    def handle_request_url_verify(self, post_obj):
        # 原样返回 challenge 字段内容
        challenge = post_obj.get("challenge", "")
        rsp = {'challenge': challenge}
        self.response(json.dumps(rsp))
        return

    def handle_message(self, event):
        # 此处只处理 text 类型消息，其他类型消息忽略
        msg_type = event.get("msg_type", "")
        if msg_type != "text":
            print("unknown msg_type =", msg_type)
            self.response("")
            return

        access_token = get_tenant_access_token()
        if access_token == "":
            self.response("")
            return

        text = event.get("text")
        # 机器人 echo 收到的消息
        send_message(access_token, event.get('open_chat_id'), '')

        if '值日生' in text:
            send_message(access_token, event.get('open_chat_id'), find_today_cleaner())

        if 'help' in text:
            send_message(access_token, event.get('open_chat_id'), '''
@我 print DeviceId,deviceName,comment
''')
        if 'print' in text:
            print(text.split('print ').pop().split(','))
            arr = text.split('print ').pop().split(',')
            while len(arr) < 3:
                arr.append('')
            [no, name, comment] = arr
            send_message(access_token, event.get("open_chat_id"), '打印内容:' + no + ',' + name + ',' + comment)
            response = requests.request(url='http://localhost/printLabel.php', method='POST', data={
                'sizeX': 50,
                'sizeY': 30,
                'info1': 'innerken.com',
                'info2': '017658146029',
                'deviceId': no,
                'deviceName': name,
                'comment': comment,
                'postOp': 'print'
            })
            print(response.text)

        self.response("")
        return

    def response(self, body):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(body.encode())


def send_message(token, chat_id, text):
    url = "https://open.larksuite.com/open-apis/message/v4/send/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }
    req_body = {
        "chat_id": chat_id,
        "msg_type": "text",
        "content": {
            "text": text
        }
    }
    data = bytes(json.dumps(req_body), encoding='utf8')
    req = request.Request(url=url, data=data, headers=headers, method='POST')
    try:
        response = request.urlopen(req)
    except Exception as e:
        print(e.read().decode())
        return

    rsp_body = response.read().decode('utf-8')
    rsp_dict = json.loads(rsp_body)
    code = rsp_dict.get("code", -1)
    if code != 0:
        print("send message error, code = ", code, ", msg =", rsp_dict.get("msg", ""))


def get_group(token):
    url = "https://open.larksuite.com/open-apis/chat/v4/list"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }
    req = request.Request(url=url, headers=headers, method='GET')
    try:
        response = request.urlopen(req)
    except Exception as e:
        print(e.read().decode())
        return
    rsp_body = response.read().decode('utf-8')
    rsp_dict = json.loads(rsp_body)
    code = rsp_dict.get("code", -1)
    if code != 0:
        print("send message error, code = ", code, ", msg =", rsp_dict.get("msg", ""))
    return rsp_dict['data']['groups']


def check_time_with_pattern(pattern):
    now = datetime.datetime.now()
    if ':' in pattern:
        [h, m, s] = pattern.split(':')
        print(now.hour, now.minute, now.second)
        return now.hour == int(h) and now.minute == int(m) and now.second == int(s)
    else:
        return now.minute % int(pattern) == 0 and now.second == 0


def find_today_cleaner():
    response = requests.get("http://localhost:8013/employee/today")
    return response.text


def find_and_send_today_cleaner(token):
    _token = token[0]
    info = find_today_cleaner()
    print(info)
    groups = get_group(_token)

    for g in groups:
        print('正在向' + g['name'] + '发送消息:')
        chat = info
        send_message(_token, g['chat_id'], chat)


def update_token(token):
    print("Old Token--->" + token[0])
    token[0] = get_tenant_access_token()
    print("New Token--->" + token[0])


period_tasks = [
    {
        'pattern': '10:30:0',
        'task': find_and_send_today_cleaner
    },
    {
        'pattern': '5',
        'task': update_token
    }
]


def period_task(token):
    _token = token[0]
    for task in period_tasks:
        if check_time_with_pattern(task['pattern']):
            print('Running task at ' + task['pattern'])
            task['task'](token)
    Timer(1, period_task, kwargs={'token': token}).start()


def get_time_now():
    return time.asctime(time.localtime(time.time()))


def run():
    token = get_tenant_access_token()
    period_task([token])
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print("start.....")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
