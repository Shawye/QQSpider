import qqspider

if __name__ == '__main__':
    # init crawler's settings
    qqspider.init()

    # get friends list
    qqspider.get_friends_list()

    # get all friends' contents
    qqspider.get_all_friends_contents()

    # get specified friends' contents
    qqspider.get_given_friends_contents([''])

    # get specified friends' shuoshuo
    qqspider.get_shuoshuo([''])

    # get specified friends' photos
    qqspider.get_photos([''])

    # analyze specified friends' text feel
    qqspider.get_text_feel('')

    # generate specified friends' word cloud
    qqspider.get_word_cloud('')
