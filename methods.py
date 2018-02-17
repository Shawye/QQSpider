import requests
import time
import base
import os
import sys
import json


class get_infos(object):
    def __init__(self):
        self.header = base.header
        self.url = base.get_friends_url()
        self.position = 0
        self.g_tk = base.get_g_tk()
        self.session = requests.Session()

    def get_friends(self):
        print("[%s] <get friends> start" % (time.ctime(time.time())))
        while True:
            url = self.url + '&offset=' + str(self.position)
            self.header['Referer'] = 'http://qzs.qq.com/qzone/v8/pages/setting/visit_v8.html'
            print("[%s] <get friends> position: %d" % (time.ctime(time.time()), self.position))
            res = requests.get(url, headers=self.header)
            html = res.text

            if "请先登录" in html:
                print("[%s] <get friends> some error occur" % (time.ctime(time.time())))
                break

            html = html[10: -2]
            html_dict = dict(eval(html))
            html_data = html_dict["data"]
            html_list = html_dict["data"]["uinlist"]

            if not len(html_list):
                print("[%s] <get friends> ok" % (time.ctime(time.time())))
                break

            with open('friends/position' + str(self.position) + '.json', 'w', encoding='utf-8') as f:
                f.write(str(html_data))

            self.position += 50
            time.sleep(1)

    @staticmethod
    def get_numbers():
        print("[%s] <get numbers> start" % (time.ctime(time.time())))
        friends = [i for i in os.listdir('friends') if i.endswith("json")]
        numbers = []
        for item in friends:
            with open('friends/' + item, encoding='utf-8') as f:
                con = eval(f.read())["uinlist"]
                for i in con:
                    numbers.append(i)
        else:
            with open('numbers', 'w', encoding='utf-8') as f:
                print("[%s] <get numbers> ok, %d in total" % (time.ctime(time.time()), len(numbers)))
                f.write(str(numbers))


class get_contents(object):
    def __init__(self):
        self.position = 0
        self.session = requests.Session()
        self.header = base.header
        self.g_tk = base.g_tk

    def get_each_item(self, num):
        self.header['Referer'] = 'http://user.qzone.qq.com/' + num
        if not os.path.exists('results/' + num):
            os.mkdir('results/' + num)
        url_base = base.get_moods_url(num)
        self.position = 0
        while True:
            print("[%s] <get contents> qq: %s position: %d" % (time.ctime(time.time()), num, self.position))
            url = url_base + "&pos=%d" % self.position
            res = self.session.get(url, headers=self.header)
            con = res.text
            con = con[10: -2]
            con_dict = json.loads(con)
            if con_dict["msglist"] is None or con_dict['usrinfo']["msgnum"] == 0:
                break
            if con_dict["subcode"] == -4001:
                sys.exit()

            with open('results/' + num + '/' + str(self.position) + '.txt', 'w', encoding='utf-8') as f:
                f.write(str(con_dict))

            self.position += 20
            time.sleep(1)

    def get_total(self):
        print("[%s] <get contents> start" % (time.ctime(time.time())))
        with open('numbers', encoding='utf-8') as f:
            numbers_list = eval(f.read())

        while numbers_list:
            save = numbers_list[:]
            item = numbers_list.pop()
            qq = item['data']
            print("[%s] <get contents> qq: %s" % (time.ctime(time.time()), qq))

            try:
                self.get_each_item(qq)
            except Exception as e:
                with open('numbers', 'w', encoding='utf-8') as f:
                    f.write(str(save))
        else:
            print("[%s] <get contents> ok" % (time.ctime(time.time())))

    def get_given(self, given):
        print("[%s] <get contents> start" % (time.ctime(time.time())))
        with open('numbers', encoding='utf-8') as f:
            numbers_list = eval(f.read())
        for i in range(len(numbers_list)):
            item = numbers_list[i]
            qq = item['data']
            if int(qq) in given:
                print("[%s] <get contents> qq: %s" % (time.ctime(time.time()), qq))

                try:
                    self.get_each_item(qq)
                except Exception as e:
                    continue
            else:
                continue
        else:
            print("[%s] <get contents> ok" % (time.ctime(time.time())))



