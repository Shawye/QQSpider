# QQSpider
```
A python crawler to grab "shuoshuo" from QQ zone

一个python爬虫，用来抓取QQ空间和朋友圈的文字信息，并做相应的分析
```

## Dependency
```
1. python(>3.0)
2. json, hashlib, time, random, re, string (come with)
3. urllib, requests
4. selenium, geckodriver, firefox(>56.0) or Chrome(>?)
5. jieba, scipy, matplotlib, wordcloud, PIL
```

## Info

1. config.json
    > auto:  True: 自动获取cookies, 需要账号密码
    >
    > ​	   False: 手动输入cookies, 建议

    > app_id & app_key: 腾讯AI接口

2. API
    > qqspider.init(): 爬虫的初始参数设置，包括cookies在内

    > qqspider.get_friends_list(): 获取所有好友列表，只需获取一次
    
    > qqspider.get_given_friends_contents(class \<list>): 爬取指定好友(所有信息)，只需获取一次

    > qqspider.get_all_friends_contents(class \<list>): 爬取所有好友(所有信息)，只需获取一次

    > qqspider.get_shuoshuo(class \<list>): 爬取指定好友的说说

    > qqspider.get_photos(class \<list>): 爬取指定好友的个人图片

    > qqspider.get_text_feel(class \<string>): 对指定好友的说说进行情感分析

    > qqspider.get_word_cloud(class \<string>): 生成指定好友说说的词云 

    > qqspider.get_wechat_word_cloud(): 生成微信好友朋友圈词云

3. Others
    > cookies的获取基于selenium提供的自动化headless firefox, 建议手动输入

    > 情感分析基于一定的正则规则进行了初步的过滤，但是仍然会有一些非法字符出现

    > 词云的stopwords采取了stopwords.txt中的内容

4. Wechat
    > WeChatMomentStat: Android平台下的数据导出工具
    
    > link: https://github.com/Chion82/WeChatMomentStat-Android

    > BlueStacks: 蓝叠安卓模拟器, 开启root权限

    > 导出的exported_sns.json替换result目录下的同名文件 

## Usage
1. shuoshuo
```python
init() # Set up "config.json"
get_friends_list(): # Just need once
get_given_friends_contents() or get_all_friends_contents()
get_shuoshuo()
get_text_feel() or get_word_cloud()
```
2. photos
```python
init() # Set up "config.json"
get_friends_list() # Just need once
get_given_friends_contents()
get_photos()
```
3. Wechat
```python
export # Use BlueStacks and WeChatMomentStat
get_wechat_word_cloud()
```


## ScreenShots (Word Cloud)

![](./images/7.PNG) 

![](./images/8.png) 

