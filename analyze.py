import os
import time

class analyze(object):
    def __init__(self):
        pass

    def get_shuoshuo(self, num):
        files = [i for i in os.listdir('results/%s'%num) if i.endswith(".txt")]
        con = []
        for item in files:
            with open('results/%s/'%num + item, encoding='utf-8') as f:
                msglist = eval(f.read())['msglist']
                for i in msglist:
                    if i['conlist'] is None:
                        continue
                    else:
                        for j in i['conlist']:
                            if 'con' in j.keys():
                                con.append(j['con'])
        else:
            with open('analyze/%s.txt'%num, 'w', encoding='utf-8') as f:
                print("[%s] get shuoshuo ok, %d in total" % (time.ctime(time.time()), len(con)))
                f.write(str(con))
        return con