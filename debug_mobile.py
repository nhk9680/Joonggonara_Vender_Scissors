# -*- coding:utf-8 -*-

import os
import sys
import time
try:
    from winsound import Beep
    executable_path='D:/chromedriver.exe'
except ImportError: #Not Windows, at Linux
    def Beep(freq, duration):
        os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
    executable_path='/usr/lib/chromium-browser/chromedriver'


from selenium import webdriver
# from bs4 import BeautifulSoup
import telegram

# args (for auto restart)
executable = sys.executable
args = sys.argv[:]
args.insert(0, sys.executable)

#telegram

try:
    my_token = '837339362:AAESYsiM7S5qRu4SBGYK-OLhrEgRtPWgDcA' # sender
    bot         = telegram.Bot(my_token)
    # chat_id     = bot.getUpdates()[-1].message.chat.id # receiver
    chat_id = 893357338
except Exception as e:    
    print(chat_id)
    sys.exit()

# text_tmp    = bot.getUpdates()[-1].message.text
text_tmp    = '.'

#selenium.webdriver
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument('disable-gpu')
options.add_argument('log-level=1')

driver = webdriver.Chrome(executable_path=executable_path, options=options)
driver.implicitly_wait(1)

def fopen_r(filename):
    f=open(filename, 'r', encoding='UTF8')
    _list=[]
    while True:
        line=f.readline()
        if not line:
            break
        _list.append(line[:-1])
    f.close()
    return _list

blacklist   = fopen_r("blacklist.txt")
block_user  = fopen_r("block_user.txt")
count       = fopen_r("count.txt")

individual  = int(count[0])
vender      = int(count[1])

keywords    = ['S10']
sign        = ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖']

title_tmp   = ' '
author_tmp  = ' '

#get article index

KT = str(424)
SK = str(339)
LG = str(425)

print("load URL...")

driver.get('https://m.cafe.naver.com/ca-fe/web/cafes/10050146/menus/'+SK)

articleIndex    = 0
# main

postnum_before  = []
title_before    = []
author_before   = []

t=0
while True:

    postnum_current = []
    title_current   = []
    author_current  = []

    postnum_after  = []
    title_after    = []
    author_after   = []    

    driver.refresh()

    print("get board info...")
    
    try:
        for board in driver.find_elements_by_class_name('txt_area'):
            postnum_current.append(board.get_attribute('href')[67:76])
            title_current.append(board.find_element_by_class_name('tit').text)
            author_current.append(board.find_element_by_class_name('ellip').text)
       
    except Exception as e:
        print(e)
        bot.sendMessage(chat_id=chat_id, text=str(e))
        continue

    # initialize
    if t==0:
        postnum_before = postnum_current
        title_before = title_current
        author_before = author_current

        postnum_after = postnum_current
        title_after = title_current
        author_after = author_current

    print("update...")

    for postnum, title, author in zip(postnum_current, title_current, author_current):
        if not (postnum in postnum_before):

            #append to after list
            postnum_after.append(postnum)
            title_after.append(title)
            author_after.append(author)

    #update
    postnum_before = postnum_current
    title_before = title_current
    author_before = author_current

    print("vender check...")

    for postnum, title, author in zip(postnum_after, title_after, author_after):
        vender_flag = False

        
        # check vender by title
        for word in blacklist:
            try:
                if word[0] in title:
                    vender+=1
                    vender_flag = True
                    break
            except Exception as e:
                print(e)
                print('word:',word,'\ntitle:',title)
                bot.sendMessage(chat_id=chat_id, \
                    text=str(e)+"\n\n"+"word: "+word+"\ntitle: "+title)
                break
        
        #check vender by author
        for user in block_user:
            if user in author:
                vender+=1
                vender_flag = True
                break

        if not vender_flag:
            individual += 1
            for keyword in keywords:
                if (keyword in title.upper()) or (keyword in title.lower()):
                    print('\n'+title)
                    for i in range(0, 5):
                        Beep(4186, 100)
                    
                    link='https://cafe.naver.com/joonggonara/'+postnum
                    bot.sendMessage(chat_id=chat_id, text=title+'\n'+author+'\n'+link)
            
            if individual%10 == 0 or vender % 100 == 0:
                count=open("count.txt", 'w')
                count.write(str(individual)+'\n')
                count.write(str(vender)+'\n')
                count.close()

    if t%24==0:
        t=0

        # telegram receive part
        # getUpdates() has 24 hours limit, so discard it when no message in 24h
        try:
            text = bot.getUpdates()[-1].message.text
        except:
            text = '.'

        #check the command
        if text_tmp != text:
            text_tmp = text
            texts = text.split(' ')

            if 'help' in text:
                bot.sendMessage(chat_id=chat_id, text='block [id]\nadd [blacklist]\nex)block gogotaxi\nadd <')
                break

            if texts[0] == 'block':
                f=open("block_user.txt", 'a')
                f.write(texts[1]+"\n")
                f.close()
                block_user.append(texts[1])
                bot.sendMessage(chat_id=chat_id, text='blocked user ' + texts[1])
                print('blocked user ' + texts[1]+'\n')
            elif texts[0] == 'add':
                f=open("blacklist.txt", 'a')
                f.write(texts[1]+"\n")
                f.close()
                blacklist.append([texts[1]])
                bot.sendMessage(chat_id=chat_id, text='add blacklist ' + texts[1])
                print('add blacklist ' + texts[1]+'\n')
            elif texts[0] == 'show':
                bot.sendMessage(chat_id=chat_id, text=str(individual)+str(vender))
                print('show blocked user list')
            else:
                bot.sendMessage(chat_id=chat_id, text='I can\'t understand.\nWhat did you say?')
            print()

    now=time.gmtime(time.time())
    print('{:d}시 {:d}분 {:d}초 {:s}\t{:d} : {:d}\t개인: {:.2f}%\t업자: {:.2f}%'\
        .format(now.tm_hour+9, now.tm_min, now.tm_sec, sign[t%8], \
            individual, vender, \
            individual/(individual+vender)*100, vender/(individual+vender)*100), end='\r')

    time.sleep(1)
    t+=1

count=open("count.txt", 'w')
count.write(str(individual)+'\n')
count.write(str(vender)+'\n')
count.close()

driver.close()
os.execvp(executable, args)
