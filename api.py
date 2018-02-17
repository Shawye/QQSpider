import hashlib
import time
import random
import string
from urllib.parse import quote
import requests


class tencentAPI(object):
    @staticmethod
    def curl_md5(src):
        m = hashlib.md5()
        m.update(src.encode('UTF-8'))
        return m.hexdigest()

    def get_params(self, plus_item):
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
        sign = self.curl_md5(sign_before)
        sign = sign.upper()
        params['sign'] = sign

        return params

    def get_text_feel(self, plus_item):
        url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textpolar"  # 情感分析的API地址
        payload = self.get_params(plus_item)  # 获取请求参数
        r = requests.get(url, params=payload)
        return r.json()
