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

# HTML 태그 제거 함수
CLEANR = re.compile('<.*?>')

def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext

def getContent(d):
    return random.choice(list(d.keys()))

# 데이터 파일 읽기
with open('search.txt', 'r', encoding='UTF8') as s:
    search = ast.literal_eval(s.read())

with open('doll.txt', 'r', encoding='UTF8') as d:
    doll = ast.literal_eval(d.read())

with open('stamp.txt', 'r', encoding='UTF8') as st:
    stamp = ast.literal_eval(st.read())

# 마스토돈 스트림 리스너 클래스
class dgListener(StreamListener):
    def on_notification(self, notification):
        if notification['type'] == 'mention':
            id = notification['status']['id']
            visibility = notification['status']['visibility']

            # 인형가챠
            if '[체질 해적단]' in notification['status']['content']:
                selected_key = getContent(doll)
                answers = doll[selected_key][0]
                image_name = doll[selected_key][1]
                image = mastodon.media_post(image_name, mime_type="image/png")
                mastodon.status_post(
                    "@" + notification['account']['username'] + "\n" + answers,
                    in_reply_to_id=id,
                    visibility=visibility,
                    media_ids=image["id"]
                )

            # 스탬프가챠
            elif '[체질반 스탬프]' in notification['status']['content']:
                selected_key = getContent(stamp)
                answers = stamp[selected_key][0]
                image_name = stamp[selected_key][1]
                image = mastodon.media_post(image_name, mime_type="image/png")
                mastodon.status_post(
                    "@" + notification['account']['username'] + "\n" + answers,
                    in_reply_to_id=id,
                    visibility=visibility,
                    media_ids=image["id"]
                )

            # 조사
            else:
                content = cleanhtml(notification['status']['content'])
                contents = content.split('[')
                contents = contents[1].split(']')
                keyword = contents[0]
                answers = search[keyword][0]
                if search[keyword][1] != '':
                    image_name = search[keyword][1]
                    image = mastodon.media_post(image_name, mime_type="image/png")
                    mastodon.status_post(
                        "@" + notification['account']['username'] + "\n" + answers,
                        in_reply_to_id=id,
                        visibility=visibility,
                        media_ids=image["id"]
                    )
                else:
                    mastodon.status_post(
                        "@" + notification['account']['username'] + "\n" + answers,
                        in_reply_to_id=id,
                        visibility=visibility
                    )

# HTTP 요청 처리 핸들러
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        mastodon.stream_user(dgListener())

# 서버 실행
port = int(os.getenv('PORT', 80))
print('Listening on port %s' % port)
httpd = socketserver.TCPServer(('', port), Handler)

mastodon.stream_user(dgListener())
httpd.serve_forever()
