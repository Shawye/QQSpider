import methods
import analyze
import api
import time
import re

if __name__ == '__main__':

    # a = methods.get_infos()
    # a.get_friends()
    #a.get_numbers()
    #l = [877458971]
    #b = methods.get_contents()
    #b.get_given(l)
    c = analyze.analyze()
    l = c.get_shuoshuo('877458971')
    d = api.tencentAPI()
    for i in l:
        result, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", i)
