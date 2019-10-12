# -*- coding:utf-8 -*-
import requests
from urllib import parse
import re
import json
import time


# 微博通用工具

class WeiBo:

    @staticmethod
    def getCookie(id):
        data = {
            'cb': 'gen_callback',
            'fp': '{"os":"2","browser":"Chrome72,0,3626,121","fonts":"undefined",'
                  '"screenInfo":"1920*1080*24",'
                  '"plugins":"Portable Document Format::internal-pdf-viewer::Chrome PDF Plugin|::mhjfbmdgcfjbbpaeojofohoefgiehjai::Chrome PDF Viewer|::internal-nacl-plugin::Native Client"}'
        }
        headers = {
            "Referer": "https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=https%3A%2F%2Fweibo.com%2Fu%2F{}%3Fis_all%3D1&domain=.weibo.\
            com&ua=php-sso_sdk_client-0.6.28&_rand=1552102425.6623".format(id)
        }
        res = requests.post("https://passport.weibo.com/visitor/genvisitor", data=data, headers=headers).text
        res = re.findall('window.gen_callback && gen_callback\((.*?)\);', res, re.S)[0]
        res = json.loads(res)
        if res['retcode'] == 20000000:
            t = res['data']['tid']
        res = requests.get(
            'https://passport.weibo.com/visitor/visitor?a=incarnate&t=%s&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.948316066345412' % parse.quote(
                t), headers=headers).text
        res = re.findall('window.cross_domain && cross_domain\((.*?)\);', res, re.S)[0]
        res = json.loads(res)
        if res['retcode'] == 20000000:
            return 'SUB={}; SUBP={}'.format(res['data']['sub'], res['data']['subp'])

    @staticmethod
    def getUser(name):
        res = requests.get('https://s.weibo.com/weibo/%s?topnav=1&wvr=6&b=1' % parse.quote(name)).text
        result = re.findall('<a href="//weibo.com/(.*?)"', res, re.S)
        # print(result)

        return result[0]

    @staticmethod
    def reformatContent(message):
        try:
            content = \
                re.findall('<div class="WB_text W_f14" node-type="feed_list_content" nick-name="(.*?)">(.*?)</div>',
                           message, re.S)[0][1]
        except IndexError:
            content = \
                re.findall('<div class="WB_text W_f14" node-type="feed_list_content" >(.*?)</div>', message, re.S)[
                    0]
        symbols = re.findall('<(.*?)>', content, re.S)
        for symbol in symbols:
            if "img" in symbol:
                img = re.findall('title="\[(.*?)\]"', symbol)[0]
                content = content.replace('<%s>' % symbol, img)
            content = content.replace('<%s>' % symbol, '')
        content = content.replace('&nbsp;', '')
        content = content.replace('\n', '')
        content = content.replace(' ', '')

        return content

    @staticmethod
    def getInfo(name):
        id = WeiBo.getUser(name)
        cookie = WeiBo.getCookie(id)
        headers = {
            "cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        res = requests.get('https://weibo.com/%s?is_all=1' % id, headers=headers).text
        results = re.findall('<script>FM.view\((.*?)\)</script>', res, re.S)
        response = []
        for result in results:
            try:
                result = json.loads(result)
                if 'Pl_Official_MyProfileFeed__' in result['domid']:
                    messages = re.findall('<div class="WB_detail">(.*?)<!-- feed区 大数据tag -->', result['html'], re.S)
                    for message in messages:
                        time = re.findall('fromprofile">(.*?)</a> 来自', message, re.S)[0]
                        content = WeiBo.reformatContent(message)
                        response.append({
                            "time": time,
                            "content": content
                        })
                    if '置顶' in response[0]['content']:
                        response.pop(0)
            except json.decoder.JSONDecodeError:
                continue
        return response

    @staticmethod
    def parse_time(update_time):
        # yue
        month_index = update_time.index("月")
        month = int(update_time[:month_index])
        # day
        day_index = update_time.index("日")
        day = int(update_time[month_index + 1:day_index])

        # house
        index = update_time.index(":")
        hour = int(update_time[index - 2:index])
        minute = int(update_time[index + 1:])
        return month, day, hour, minute

    @staticmethod
    def is_new_info(last_update_time, update_time):
        """
        比较时间，判断是否是新更新的
        :param update_time: * 月 * 日 xx:mm格式
        :return:
        """
        month, day, hour, minute = WeiBo.parse_time(update_time)
        last_month, last_day, last_hour, last_minute = WeiBo.parse_time(last_update_time)
        if month > last_month:
            return True
        elif month == last_month:
            if day > last_day:
                return True
            elif day == last_day:
                if hour > last_hour:
                    return True
                elif hour == last_hour:
                    if minute > last_minute:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        elif month < last_month:
            # 新的一年
            return True
