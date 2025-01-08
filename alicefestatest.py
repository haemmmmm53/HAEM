#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import http.server
import socketserver
import script
import re
import random
import ast

from http import HTTPStatus
from mastodon import Mastodon
from mastodon.streaming import StreamListener


# 마스토돈 계정 세팅

BASE = 'https://orbitof.kr'

m = Mastodon(
    client_id="-",
    client_secret="-",
    access_token="-",
    api_base_url=BASE
)

print('성공적으로 로그인 되었습니다.')

# 마스토동 계정 세팅 끝



def getContent(d):
    r = random.choice(d.Keys())
    script = d[r][0]
    image = d[r][1]


class dgListener(StreamListener):
    anwers = ''
    with open('search.txt', 'r') as search:
        ast.literal_eval(search.read())
    
    with open('doll.txt', 'r') as doll:
        ast.literal_eval(doll.read())

    with open('stamp.txt', 'r') as stamp:
        ast.literal_eval(stamp.read())

    def on_notification(self, notification):
        if notification['type'] == 'mention':
            id = notification['status']['id']
            visibility = notification['status']['visibility']
            got = cleanhtml(notification['status']['content'])

            if got.__contains__('[') is False or got.__contains__(']') is False:
                pass

            keyword = got[got.find('[')+1:got.find(']')]

            # 인형가챠
            if keyword == '인형가챠':
                answers = search[keyword][0]
                image_name = search[keyword][1]
                image = mastodon.media_post(image_name, mime_type = "image/png")
                mastodon.status_post("@" + notification['account']['username'] + "\n" + 
                                    answers, in_reply_to_id = id, 
                                    visibility = visibility, media_ids=image["id"])
                pass

            # 스탬프가챠
            if keyword == '스탬프가챠':
                answers = search[keyword][0]
                image_name = search[keyword][1]
                image = mastodon.media_post(image_name, mime_type = "image/png")
                mastodon.status_post("@" + notification['account']['username'] + "\n" + 
                                    answers, in_reply_to_id = id, 
                                    visibility = visibility, media_ids=image["id"])
                pass

            # 조사
            else: 
                answers = search[keyword][0]
                if search[keyword][1] != '':
                    image_name = search[keyword][1]
                    image = mastodon.media_post(image_name, mime_type = "image/png")
                    mastodon.status_post("@" + notification['account']['username'] + "\n" + 
                                        answers, in_reply_to_id = id, 
                                        visibility = visibility, media_ids=image["id"])
                else:
                    mastodon.status_post("@" + notification['account']['username'] + "\n" + 
                                        answers, in_reply_to_id = id, 
                                        visibility = visibility)




class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        # msg = 'Hello! you requested %s' % (self.path)
        mastodon.stream_user(dgListener())
        # self.wfile.write(msg.encode())

port = int(os.getenv('PORT', 80))
print('Listening on port %s' % (port))
httpd = socketserver.TCPServer(('', port), Handler)

mastodon.stream_user(dgListener())

httpd.serve_forever()
