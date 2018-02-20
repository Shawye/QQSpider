import requests
import time
import sys
import json
from urllib import parse
import os
import hashlib
import time
import random
import re
import string
from urllib.parse import quote
import requests
from os import path
from scipy.misc import imread
import matplotlib.pyplot as plt
import codecs
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

__cookie = None
__header = {'host': 'h5.qzone.qq.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh,zh-CN;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': None,
            'connection': 'keep-alive'}
__g_tk = None
__friends_url = None
__session = None


def __get_cookie_from_file():
    with open('./cookie.txt') as f:
        return f.read().replace('\n', '')


def __get_cookie_from_auto():
    pass


def __get_g_tk():
    start = __cookie.find('p_skey=')
    end = __cookie.find(';', start)
    key = __cookie[start + 7: end]
    h = 5381
    for s in key:
        h += (h << 5) + ord(s)
    return h & 2147483647


def __get_moods_url(num):
    params = {"cgi_host": "http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6",
              "code_version": 1,
              "format": "jsonp",
              "g_tk": __g_tk,
              "hostUin": num,
              "inCharset": "utf-8",
              "need_private_comment": 1,
              "notice": 0,
              "num": 20,
              "outCharset": "utf-8",
              "sort": 0,
              "uin": num}
    host = "https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?"
    return host + parse.urlencode(params)


def __get_friends_url():
    qq_start = __cookie.find('uin=o')
    qq_end = __cookie.find(';', qq_start)
    qq_num = __cookie[qq_start + 5: qq_end]
    if qq_num[0] == 0:
        qq_num = qq_num[1:]
    params = {"uin": qq_num,
              "fupdate": 1,
              "action": 1,
              "g_tk": __g_tk}
    host = "https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/right/get_entryuinlist.cgi?"
    return host + parse.urlencode(params)


def init():
    global __cookie, __header, __g_tk, __friends_url, __session
    __cookie = __get_cookie_from_file()
    __header['Cookie'] = __cookie
    __g_tk = __get_g_tk()
    __friends_url = __get_friends_url()
    __session = requests.Session()


def get_friends_list():
    print("[%s] <get friends> start" % (time.ctime(time.time())))
    position = 0
    while True:
        url = __friends_url + '&offset=' + str(position)
        __header['Referer'] = 'http://qzs.qq.com/qzone/v8/pages/setting/visit_v8.html'
        print("[%s] <get friends> position: %d" % (time.ctime(time.time()), position))
        res = requests.get(url, headers=__header)
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

        with open('friends/position' + str(position) + '.json', 'w', encoding='utf-8') as f:
            f.write(str(html_data))

        position += 50
        time.sleep(1)
    print("[%s] <get numbers> start" % (time.ctime(time.time())))
    friends = [i for i in os.listdir('friends') if i.endswith("json")]
    numbers = []
    for item in friends:
        with open('friends/' + item, encoding='utf-8') as f:
            con = eval(f.read())["uinlist"]
            for i in con:
                numbers.append(i)
    else:
        with open('friends/numbers.txt', 'w', encoding='utf-8') as f:
            print("[%s] <get numbers> ok, %d in total" % (time.ctime(time.time()), len(numbers)))
            f.write(str(numbers))


def __get_each_item(num):
    __header['Referer'] = 'http://user.qzone.qq.com/' + num
    if not os.path.exists('results/' + num):
        os.mkdir('results/' + num)
    url_base = __get_moods_url(num)
    position = 0
    while True:
        print("[%s] <get contents> qq: %s position: %d" % (time.ctime(time.time()), num, position))
        url = url_base + "&pos=%d" % position
        res = __session.get(url, headers=__header)
        con = res.text
        con = con[10: -2]
        con_dict = json.loads(con)
        if con_dict["msglist"] is None or con_dict['usrinfo']["msgnum"] == 0:
            break
        if con_dict["subcode"] == -4001:
            sys.exit()

        with open('results/' + num + '/' + str(position) + '.txt', 'w', encoding='utf-8') as f:
            f.write(str(con_dict))

        position += 20
        time.sleep(1)


def get_all_friends_contents():
    print("[%s] <get contents> start" % (time.ctime(time.time())))
    with open('friends/numbers.txt', encoding='utf-8') as f:
        numbers_list = eval(f.read())

    while numbers_list:
        save = numbers_list[:]
        item = numbers_list.pop()
        qq = item['data']
        print("[%s] <get contents> qq: %s" % (time.ctime(time.time()), qq))

        try:
            __get_each_item(qq)
        except Exception as e:
            with open('friends/numbers.txt', 'w', encoding='utf-8') as f:
                f.write(str(save))
    else:
        print("[%s] <get contents> ok" % (time.ctime(time.time())))


def get_given_friend_contents(given):
    print("[%s] <get contents> start" % (time.ctime(time.time())))
    with open('friends/numbers.txt', encoding='utf-8') as f:
        numbers_list = eval(f.read())
    for i in range(len(numbers_list)):
        item = numbers_list[i]
        qq = item['data']
        if qq in given:
            print("[%s] <get contents> qq: %s" % (time.ctime(time.time()), qq))

            try:
                __get_each_item(qq)
            except Exception as e:
                continue
        else:
            continue
    else:
        print("[%s] <get contents> ok" % (time.ctime(time.time())))


def __segment(num):
    print("[%s] <segmentation> qq: %s start" % (time.ctime(time.time()), num))
    with open('./analyze/%s.txt' % num, encoding='utf-8') as f:
        content = eval(f.read())
    with open('./analyze/%s-seg.txt' % num, 'w', encoding='utf-8') as wf:
        for con in content:
            con, number = re.subn('[#]', "", con)
            con, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", con)
            wf.write(con)
        print("[%s] <segmentation> qq: %s ok" % (time.ctime(time.time()), num))


def get_shuoshuo(given):
    for num in given:
        print("[%s] <get shuoshuo> qq: %s start" % (time.ctime(time.time()), num))
        files = [i for i in os.listdir('results/%s' % num) if i.endswith(".txt")]
        con = []
        for item in files:
            with open('results/%s/' % num + item, encoding='utf-8') as f:
                msglist = eval(f.read())['msglist']
                for i in msglist:
                    if i['conlist'] is None:
                        continue
                    else:
                        for j in i['conlist']:
                            if 'con' in j.keys():
                                con.append(j['con'])
        else:
            with open('analyze/%s.txt' % num, 'w', encoding='utf-8') as f:
                print("[%s] <get shuoshuo> qq: %s ok, %d in total" % (time.ctime(time.time()), num, len(con)))
                f.write(str(con))
        __segment(num)


def __curl_md5(src):
    m = hashlib.md5()
    m.update(src.encode('UTF-8'))
    return m.hexdigest()


def __get_params(plus_item):
    # 请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效
    t = time.time()
    time_stamp = str(int(t))

    # 请求随机字符串，用于保证签名不可预测
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))

    # 应用标志，这里修改成自己的id和key
    app_id = '1106662237'
    app_key = 'tR3QPnWnYEDl5qlG'

    params = {'app_id': app_id,
              'text': plus_item,
              'time_stamp': time_stamp,
              'nonce_str': nonce_str,
              'sign': ''
              }
    sign_before = ''
    for key in sorted(params):
        if params[key] != '':
            # 键值拼接过程value部分需要URL编码，URL编码算法用大写字母，例如%E8，而不是小写%e8。quote默认的大写。
            sign_before += key + '=' + quote(params[key]) + '&'
            # 将应用密钥以app_key为键名，组成URL键值拼接到字符串sign_before末尾
    sign_before += 'app_key=' + app_key

    # 对字符串S进行MD5运算，将得到的MD5值所有字符转换成大写，得到接口请求签名
    sign = __curl_md5(sign_before)
    sign = sign.upper()
    params['sign'] = sign

    return params


def get_text_feel(plus_item):
    # pre-process
    # delete emoji

    # split = re.split('[,，.。:：!！]', i)
    plus_item, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", plus_item)

    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textpolar"  # 情感分析的API地址
    payload = __get_params(plus_item)  # 获取请求参数
    r = requests.get(url, params=payload)
    return r.json()


def get_wordcloud(num):
    __basePath = './word'
    __fileNamePath = u'./analyze/' + num + '-seg.txt'
    __stopWordPath = u'./word/stopwords.txt'
    __imagePath = u'./word/bg.jpg'
    __ttfPath = u'./word/SourceHanSans-Regular.otf'
    d = path.dirname(__file__)
    # UTF8_2_GBK(__fileNamePathO, __fileNamePathN)
    # Read the whol text.
    text = open(path.join(d, __fileNamePath), encoding='utf-8').read()

    # read the mask / color image
    # taken from http://jirkavinse.deviantart.com/art/quot-Real-Life-quot-Alice-282261010
    alice_coloring = imread(path.join(d, __imagePath))

    wc = WordCloud(background_color="black",
                   max_words=2000,
                   mask=alice_coloring,
                   stopwords=STOPWORDS.add("said"),
                   max_font_size=40,
                   random_state=42,
                   font_path=__ttfPath)
    # generate word cloud
    wc.generate(text)

    # create coloring from image
    image_colors = ImageColorGenerator(alice_coloring)

    # show
    # plt.imshow(wc)
    # plt.axis("off")
    # plt.show()
    # recolor wordcloud and show
    # we could also give color_func=image_colors directly in the constructor
    plt.imshow(wc.recolor(color_func=image_colors))
    plt.axis("off")
    plt.show()
    # plt.imshow(alice_coloring, cmap=plt.cm.gray)
    # plt.axis("off")
    # plt.show()

