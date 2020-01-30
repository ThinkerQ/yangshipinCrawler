import datetime
import json
import logging
import time

import requests
from bs4 import BeautifulSoup

from service.DB import DB

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logging.getLogger(__name__)

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
}


class Crawler:
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update(headers)
        self.db = DB()
        self.crawl_timestamp = int()

    def run(self):
        # 每隔60秒执行一次 crawler()
        while True:
            logging.info("*** start ***")
            self.crawler()
            self.crawler_comment()
            logging.info("************ Successful ************")
            time.sleep(60)

    def crawler(self):
        # 爬取直播页面人数、title等信息
        while True:
            self.crawl_timestamp = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000)
            logging.info("===crawl_timestamp={0}".format(self.crawl_timestamp))

            try:
                # 武汉火神山医院建设直播-央视频
                r = self.session.get(
                    url='https://m.yangshipin.cn/video?type=2&vid=2001891501&pid=600016618&ptag=4_1.1.0.20230_sina')
            except requests.exceptions.ChunkedEncodingError:
                continue
            soup = BeautifulSoup(r.content, 'html.parser')

            # 解析script模块数据并截取为json数据
            script_content = soup.find('script', attrs={'statesync': 'video'}).text
            script_content = script_content[23:]
            self.all_info_parse(script_content)
            break

    def all_info_parse(self, script_json):
        info = json.loads(script_json)
        payloads = info['payloads']
        share_video = payloads['sharevideo']
        share_video.pop('streams')
        share_video['updateTime'] = self.crawl_timestamp
        # 存储到mongodb
        self.db.insert(collection="FireGodMountain_all", data=share_video)
        logging.info("{0}".format(share_video))

    # 抓取评论信息
    def crawler_comment(self):
        while True:
            # 爬取评论信息
            try:
                # 武汉火神山医院建设直播-央视频
                last_comment_id = '6628616728501886126'
                url = 'https://h5access.yangshipin.cn/web/live_comment_list?vappid=59306155&vsecret=b42702bf7309a179d102f3d51b1add2fda0bc7ada64cb801&raw=1&targetId=1&pid=600016618&lastCommentId={0}'
                request = self.session.get(
                    url.format(last_comment_id))
            except requests.exceptions.ChunkedEncodingError:
                continue
            # 循环抓取评论
            comment_soup = BeautifulSoup(request.content, 'html.parser').text
            comment_json = json.loads(comment_soup)
            data = comment_json['data']
            comments = data['comments']
            for comment in comments:
                if self.db.find_one("FireGodMountain_comment", comment):
                    continue
                self.db.insert("FireGodMountain_comment", comment)
            break
