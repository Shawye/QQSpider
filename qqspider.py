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

# global variable statement
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
__config = None


def __read_config():
    con = {}
    try:
        with open('./config.json') as f:
            con = eval(f.read())
    except Exception as e:
        print("[%s] <error> check your json format" % (time.ctime(time.time())))
        print(e)
    return con


def __get_cookie_from_file():
    return __config['cookie']


def __get_cookie_from_auto():
    from selenium import webdriver
    print("[%s] <get cookies> start" % (time.ctime(time.time())))

    # set firefox headless, run in background
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.set_headless()
    driver = webdriver.Firefox(firefox_options=firefox_options)

    url = 'https://qzone.qq.com/'
    driver.get(url)
    # switch frame to login frame, important
    driver.switch_to.frame('login_frame')
    time.sleep(1)
    driver.find_element_by_id('switcher_plogin').click()
    time.sleep(1)
    driver.find_element_by_id('u').send_keys(__config['username'])
    driver.find_element_by_id('p').send_keys(__config['password'])
    time.sleep(1)
    driver.find_element_by_id('login_button').click()
    time.sleep(1)

    cookie = ""
    for item in driver.get_cookies():
        cookie += item["name"] + "=" + item["value"] + "; "
    driver.quit()

    print("[%s] <get cookies> ok" % (time.ctime(time.time())))
    return cookie


def __get_g_tk():
    # get g_tk
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
    # assign statement
    global __cookie, __header, __g_tk, __friends_url, __session, __config
    __config = __read_config()
    if __config['auto']:
        __cookie = __get_cookie_from_auto()
        with open('./config.json') as f:
            con = eval(f.read())
            con['cookie'] = __cookie
            con['auto'] = False
        with open('./config.json', 'w') as wf:
            wf.write(str(con))
    else:
        __cookie = __get_cookie_from_file()
    __header['Cookie'] = __cookie
    __g_tk = __get_g_tk()
    __friends_url = __get_friends_url()
    __session = requests.Session()


def get_friends_list():
    print("[%s] <get friends> start" % (time.ctime(time.time())))
    if not os.path.exists('friends/'):
        os.mkdir('friends/')
    position = 0
    while True:
        url = __friends_url + '&offset=' + str(position)
        __header['Referer'] = 'http://qzs.qq.com/qzone/v8/pages/setting/visit_v8.html'
        print("[%s] <get friends> position: %d" % (time.ctime(time.time()), position))
        res = requests.get(url, headers=__header)
        html = res.text

        # cookie invalid
        if "请先登录" in html:
            print("[%s] <get friends> some error occur" % (time.ctime(time.time())))
            break

        # html[10: -2] may cause a error
        try:
            html = html[10: -2]
            html_dict = dict(eval(html))
            html_data = html_dict["data"]
            html_list = html_dict["data"]["uinlist"]
        except Exception as e:
            print("[%s] <get friends> some error occur" % (time.ctime(time.time())))
            print(e)

        if not len(html_list):
            print("[%s] <get friends> ok" % (time.ctime(time.time())))
            break

        # write initial data crawled from qqzone with format 'json'
        with open('friends/position' + str(position) + '.json', 'w', encoding='utf-8') as f:
            f.write(str(html_data))

        position += 50
        time.sleep(1)

    # get useful data
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
    if not os.path.exists('results/'):
        os.mkdir('results/')
    try:
        with open('friends/numbers.txt', encoding='utf-8') as f:
            numbers_list = eval(f.read())
    except Exception as e:
        print("[%s] <get contents> make sure numbers.txt exists" % (time.ctime(time.time())))
        print(e)

    while numbers_list:
        save = numbers_list[:]
        item = numbers_list.pop()
        qq = item['data']
        print("[%s] <get contents> qq: %s" % (time.ctime(time.time()), qq))
        try:
            __get_each_item(qq)
        # restore the file
        except Exception as e:
            with open('friends/numbers.txt', 'w', encoding='utf-8') as f:
                f.write(str(save))
            print(e)
    else:
        print("[%s] <get contents> ok" % (time.ctime(time.time())))


def get_given_friends_contents(given):
    print("[%s] <get contents> start" % (time.ctime(time.time())))
    if not os.path.exists('results/'):
        os.mkdir('results/')
    try:
        with open('friends/numbers.txt', encoding='utf-8') as f:
            numbers_list = eval(f.read())
    except Exception as e:
        print("[%s] <get contents> make sure numbers.txt exists" % (time.ctime(time.time())))
        print(e)
    numbers = [i['data'] for i in numbers_list]
    for qq in given:
        if qq in numbers:
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
    try:
        with open('./analyze/%s.txt' % num, encoding='utf-8') as f:
            content = eval(f.read())
    except Exception as e:
        print("[%s] <get contents> make sure %s.txt exists" % (num, time.ctime(time.time())))
        print(e)
    if not os.path.exists('analyze/'):
        os.mkdir('analyze/')
    with open('./analyze/%s-seg.txt' % num, 'w', encoding='utf-8') as wf:
        for con in content:
            # replace #
            con, number = re.subn('[#]', "", con)
            # replace [emoji]
            con, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", con)
            wf.write(con)
        print("[%s] <segmentation> qq: %s ok" % (time.ctime(time.time()), num))


def get_shuoshuo(given):
    if not os.path.exists('analyze/'):
        os.mkdir('analyze')
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
    # md5
    m = hashlib.md5()
    m.update(src.encode('utf-8'))
    return m.hexdigest()


def __get_params(plus_item):
    # request timestamp
    t = time.time()
    time_stamp = str(int(t))

    # request a random string
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))

    # config.json
    app_id = __config['app_id']
    app_key = __config['app_key']

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


def get_text_feel(num):
    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textpolar"
    text_url = './analyze/%s.txt' % num
    print("[%s] <get text feel> start" % (time.ctime(time.time())))
    try:
        with open(text_url, encoding='utf-8') as f:
            all_chaps = eval(f.read())
    except Exception as e:
        print("[%s] <get text feel> make sure %s.txt exists" % (time.ctime(time.time()), num))
        print(e)
    valid_count = 0
    for plus_item in all_chaps:
        plus_item, number = re.subn('[#]', "", plus_item)
        plus_item, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", plus_item)
        payload = __get_params(plus_item)  # 获取请求参数
        r = requests.get(url, params=payload)
        if r.json()['ret'] == 0:
            polar = r.json()['data']['polar']
            print('confidence: %d, polar: %s, text: %s' % (r.json()['data']['confd'],
                  '负面' if polar == -1 else '中性' if polar == 0 else '正面', r.json()['data']['text']))
            valid_count += 1
    print("[%s] <get text feel> ok" % (time.ctime(time.time())))
    print("[%s] <get text feel> %d valid, %d in total" % (time.ctime(time.time()), valid_count, len(all_chaps)))


def get_word_cloud(num):
    print("[%s] <get word cloud> start" % (time.ctime(time.time())))
    import jieba
    from scipy.misc import imread
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
    text_url = './analyze/%s-seg.txt' % num
    mask_url = './word/bg.jpg'
    try:
        with open(text_url, encoding='utf-8') as f:
            all_chaps = [chap for chap in f.readlines()]
    except Exception as e:
        print("[%s] <get word cloud> make sure %s-seg.txt exists" % (time.ctime(time.time()), num))
        print(e)
    dictionary = []
    for i in range(len(all_chaps)):
        words = list(jieba.cut(all_chaps[i]))
        dictionary.append(words)

    # flat
    tmp = []
    for chapter in dictionary:
        for word in chapter:
            tmp.append(word.encode('utf-8'))
    dictionary = tmp

    # filter
    unique_words = list(set(dictionary))

    freq = []
    for word in unique_words:
        freq.append((word.decode('utf-8'), dictionary.count(word)))

    # sort
    freq.sort(key=lambda x: x[1], reverse=True)

    # broke_words
    broke_words = []

    try:
        with open('word/stopwords.txt') as f:
            broke_words = [i.strip() for i in f.readlines()]
    except Exception as e:
        broke_words = STOPWORDS

    # remove broke_words
    freq = [i for i in freq if i[0] not in broke_words]

    # remove monosyllable words
    freq = [i for i in freq if len(i[0]) > 1]

    img_mask = imread(mask_url)
    img_colors = ImageColorGenerator(img_mask)

    wc = WordCloud(background_color="white",  # bg color
                   max_words=2000,  # max words
                   font_path=u'./word/SourceHanSans-Regular.otf',
                   mask=img_mask,  # bg image
                   max_font_size=60,  # max font size
                   random_state=42)

    wc.fit_words(dict(freq))

    plt.imshow(wc)
    plt.axis('off')

    print("[%s] <get word cloud> ok" % (time.ctime(time.time())))
    plt.show()
