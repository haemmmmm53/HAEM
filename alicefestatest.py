#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import http.server
import socketserver
import re
import random
import ast

from http import HTTPStatus
from mastodon import Mastodon
from mastodon.streaming import StreamListener


# 마스토돈 계정 세팅

BASE = 'https://orbitof.kr'

mastodon = Mastodon(
    client_id="VO0wPbh3fTBD0n0R4WzRytEB1Uzswpg9Xe3M3YlmS1E",
    client_secret="OqYxGei3y8GBdUvNfOBEUBfmz5QHkpcDTwWNSyTdHIo",
    access_token="EfL5tQB6-vS2AFX0aM3He-CaiHKHqvnIXIxyO5nuNI0",
    api_base_url=BASE
)

print('성공적으로 로그인 되었습니다.')

# 마스토동 계정 세팅 끝

CLEANR = re.compile('<.*?>')

def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext

def getContent(d):
    r = random.choice(d.Keys())
    script = d[r][0]
    image = d[r][1]


class dgListener(StreamListener):
    anwers = ''
    with open('search.txt', 'r') as s:
        search = ast.literal_eval(s.read())
    
    with open('doll.txt', 'r') as d:
        doll = ast.literal_eval(d.read())

    with open('stamp.txt', 'r') as st:
        stamp = ast.literal_eval(st.read())

    def on_notification(self, notification):
        if notification['type'] == 'mention':
            id = notification['status']['id']
            visibility = notification['status']['visibility']

            # 인형가챠
            if '[인형가챠]' in notification['status']['content']:
                answers = doll[keyword][0]
                image_name = doll[keyword][1]
                image = mastodon.media_post(image_name, mime_type = "image/png")
                mastodon.status_post("@" + notification['account']['username'] + "\n" + 
                                    answers, in_reply_to_id = id, 
                                    visibility = visibility, media_ids=image["id"])
                pass

            # 스탬프가챠
            if '[스탬프가챠]' in notification['status']['content']:
                answers = stamp[keyword][0]
                image_name = stamp[keyword][1]
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
