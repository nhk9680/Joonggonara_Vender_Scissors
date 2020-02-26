import os
import sys
import time
from winsound import Beep

from selenium import webdriver
# from bs4 import BeautifulSoup
import telegram

# args (for auto restart)
executable = sys.executable
args = sys.argv[:]
args.insert(0, sys.executable)

# telegram
my_token = '1046523902:AAHdt0hYT4Xc5ndpAUaLZ4RQJqkwyt6p7bU'
bot         = telegram.Bot(my_token)
chat_id     = bot.getUpdates()[-1].message.chat.id
# text_tmp    = bot.getUpdates()[-1].message.text

# selenium.webdriver
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument('disable-gpu')
options.add_argument('log-level=1')

driver = webdriver.Chrome(executable_path='D:/chromedriver.exe', options=options)
driver.implicitly_wait(1)

keywords    = ['korea', '210.126', 'koreasatoshi', 'FlightF']
sign        = ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖']

# get article index
driver.get('https://gall.dcinside.com/mgallery/board/lists?id=chartanalysis')
num_old = driver.find_element_by_xpath(
        '//*[@id="container"]/section[1]/article[2]/div[2]/table/tbody/tr[7]/td[1]').text

# bot.sendMessage(chat_id, "test")
# sys.exit()

try:

    t = 0
    while True:
        # activation check
        time.sleep(1)

        now = time.gmtime(time.time())
        print('{:d}시 {:d}분 {:d}초 \t {:s}'.
              format(now.tm_hour + 9, now.tm_min, now.tm_sec, sign[t % 8]), end='\r')

        if t == 8:
            t = 0
        t += 1

        # gather info

        driver.refresh()


        num = driver.find_element_by_xpath(
            '//*[@id="container"]/section[1]/article[2]/div[2]/table/tbody/tr[7]/td[1]').text
        if num == num_old:
            continue
        num_old = num

        name = driver.find_element_by_xpath(
            '//*[@id="container"]/section[1]/article[2]/div[2]/table/tbody/tr[7]/td[4]').text
        title = driver.find_element_by_xpath(
            '//*[@id="container"]/section[1]/article[2]/div[2]/table/tbody/tr[7]/td[3]/a').text


        # check
        for word in keywords:
            if word in name:
                for i in range(0, 5):
                    Beep(4186, 100)

                link = 'https://gall.dcinside.com/mgallery/board/view/?id=chartanalysis&no=' + num + '&page=1'
                print("\n"+title+"\n"+name+"\n"+link+"\n")
                bot.sendMessage(chat_id=chat_id, text=title+"\n"+name+"\n"+link)


except Exception as e:
    print('\n\n{:d}시 {:d}분 {:d}초 \t {:s}'.
          format(now.tm_hour + 9, now.tm_min, now.tm_sec, sign[t % 8]), end='\n')
    print(e)
    # exit
    driver.close()
    os.execvp(executable, args)
