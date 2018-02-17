from urllib import parse
import os


def get_cookie_from_file():
    with open('./cookie.txt') as f:
        return f.read().replace('\n', '')


def get_cookie_from_auto():
    pass


cookie = get_cookie_from_file()

header = {'host': 'h5.qzone.qq.com',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'zh,zh-CN;q=0.8,en-US;q=0.5,en;q=0.3',
          'Accept-Encoding': 'gzip, deflate, br',
          'Cookie': cookie,
          'connection': 'keep-alive' }


def get_g_tk():
    p_skey_start = cookie.find('p_skey=')
    p_skey_end = cookie.find(';', p_skey_start)
    p_skey = cookie[p_skey_start+7: p_skey_end]
    h = 5381
    for s in p_skey:
        h += (h << 5) + ord(s)
    return h & 2147483647


g_tk = get_g_tk()


def get_moods_url(host_num):
    params = {"cgi_host": "http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6",
              "code_version": 1,
              "format": "jsonp",
              "g_tk": g_tk,
              "hostUin": host_num,
              "inCharset": "utf-8",
              "need_private_comment": 1,
              "notice": 0,
              "num": 20,
              "outCharset": "utf-8",
              "sort": 0,
              "uin": host_num }
    host = "https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?"
    return host + parse.urlencode(params)


def get_friends_url():
    qq_start = cookie.find('uin=o')
    qq_end = cookie.find(';', qq_start)
    qq_num = cookie[qq_start+5: qq_end]
    if qq_num[0] == 0:
        qq_num = qq_num[1:]
    params = {"uin": qq_num,
              "fupdate": 1,
              "action": 1,
              "g_tk": g_tk}

    host = "https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/right/get_entryuinlist.cgi?"
    return host + parse.urlencode(params)


