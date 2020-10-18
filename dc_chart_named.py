import os
import sys
import time
from winsound import Beep

from selenium import webdriver
# from bs4 import BeautifulSoup
import telegram

url = 'https://m.dcinside.com/board/electronicmoney'

# args (for auto restart)
executable = sys.executable
args = sys.argv[:]
args.insert(0, sys.executable)

with open("telegram.txt", "r") as f:
    lines = f.readlines()
my_token = lines[0][:-1]     # sender, -1: remove \n
chat_id = lines[1]      # receiver


# telegram
try:
    bot = telegram.Bot(my_token)
    # chat_id     = bot.getUpdates()[-1].message.chat.id
except Exception as e:
    print(chat_id)
    sys.exit()

# selenium.webdriver
options = webdriver.ChromeOptions()
# options.add_argument('headless')
# options.add_argument('window-size=1920x1080')
# options.add_argument('disable-gpu')
options.add_argument('log-level=1')

# mobile emulation
mobile_emulation = {'deviceName': "iPhone X"}
options.add_experimental_option("mobileEmulation", mobile_emulation)

driver = webdriver.Chrome(executable_path='D:/chromedriver.exe', options=options)
driver.implicitly_wait(1)

keywords    = ['FlightF', '워뇨띠']
sign        = ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖']

# get article index
driver.get(url)

def boardXpath(n):
    return f'/html/body/div/div/div/section[3]/ul[2]/li[{n}]/div/a[1]'

def get_board_info(n):
    board = {
        'url': driver.find_element_by_xpath(boardXpath(n)).get_attribute('href'),
        'num': driver.find_element_by_xpath(boardXpath(n)).get_attribute('href').split('/')[-1],
        'name': driver.find_element_by_xpath(boardXpath(1)+'/ul/li[2]').text,
        'title': driver.find_element_by_xpath(boardXpath(1)+'/span/span[2]').text
    }
    return board


# num_old = get_board_info(1)['num']

boardnum_old = set()
board_list = []
for i in range(5):
    board_list.append(get_board_info(i+1))
    boardnum_old.add(board_list[i]['num'])


# bot.sendMessage(chat_id, "test")
# sys.exit()

try:
    t = 0
    while True:
        # activation check
        time.sleep(10)
        now = time.gmtime(time.time())
        print('{:d}시 {:d}분 {:d}초 \t {:s}'.
              format(now.tm_hour + 9, now.tm_min, now.tm_sec, sign[t % 8]), end='\r')
        if t == 8:
            t = 0
        t += 1

        driver.refresh()

        boardnum = set()
        board_list = []
        for i in range(5):
            board_list.append(get_board_info(i + 1))
            boardnum.add(board_list[i]['num'])

        if boardnum == boardnum_old:
            continue
        boardnum.remove(min(boardnum))
        boardnum_old = boardnum

        # check
        for board in board_list:
            name = board['name']
            for word in keywords:
                if word in name:
                    for i in range(0, 5):
                        Beep(4186, 100)

                    link = url + board['num']
                    print("\n"+board['title']+"\n"+name+"\n"+link+"\n")
                    bot.sendMessage(chat_id=chat_id, text=board['title']+"\n"+name+"\n"+link)


except Exception as e:
    print('\n\n{:d}시 {:d}분 {:d}초 \t {:s}'.
          format(now.tm_hour + 9, now.tm_min, now.tm_sec, sign[t % 8]), end='\n')
    print(e)
    # exit
    driver.close()
    os.execvp(executable, args)
