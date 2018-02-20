import qqspider

if __name__ == '__main__':
    qqspider.init()
    #qqspider.get_friends_list()
    #qqspider.get_all_friends_contents()
    #qqspider.get_given_friend_contents(['601841082'])
    #qqspider.get_shuoshuo(['601841082'])
    qqspider.get_text_feel('601841082')
    qqspider.get_word_cloud('601841082')