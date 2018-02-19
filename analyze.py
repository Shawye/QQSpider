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


def get_shuoshuo(num):
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
            print("[%s] get shuoshuo ok, %d in total" % (time.ctime(time.time()), len(con)))
            f.write(str(con))
    return con


def segment(num):
    with open('./analyze/%s.txt' % num, encoding='utf-8') as f:
        content = eval(f.read())
    with open('./analyze/%s-seg.txt' % num, 'w', encoding='utf-8') as wf:
        for con in content:
            con, number = re.subn('[#]', "", con)
            con, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", con)
            wf.write(con)


def curl_md5(src):
    m = hashlib.md5()
    m.update(src.encode('UTF-8'))
    return m.hexdigest()


def get_params(plus_item):
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
    sign = curl_md5(sign_before)
    sign = sign.upper()
    params['sign'] = sign

    return params


def get_text_feel(plus_item):
    # pre-process
    # delete emoji

    # split = re.split('[,，.。:：!！]', i)
    plus_item, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", plus_item)

    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textpolar"  # 情感分析的API地址
    payload = get_params(plus_item)  # 获取请求参数
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
    # Read the whole text.
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
