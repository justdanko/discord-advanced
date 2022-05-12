import threading
from random import choice, randint
from time import sleep
from threading import Thread
from json import loads
from os import system
from ctypes import windll
from sys import stderr

try:
    import requests
except:
    system('pip install requests')
    import requests
try:
    from loguru import logger
except:
    system('pip install loguru')
    from loguru import logger
try:
    from urllib3 import disable_warnings
except:
    system('pip install urllib3')
    from urllib3 import disable_warnings

disable_warnings()
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <level>{message}</level>")
clear = lambda: system('cls')
print('Telegram Channel - https://t.me/n4z4v0d & https://t.me/earlyberkut\n')
windll.kernel32.SetConsoleTitleW('Discord Bot | by NAZAVOD&EARLY BERKUT')
lock = threading.Lock() 

tokensfolder = str(input('TXT файл с токенами Disocrd: '))
with open(tokensfolder, 'r', encoding='utf-8') as file:
    data = [token.strip() for token in file]

if ':' not in data[0]:
    chat_id = int(input('Введите ChatID Discord: '))
else:
    chat_id = 0

delete_message_after_send = str(input('Удалять сообщение после отправки? (y/N): '))

useproxy = str(input('Использовать proxy? (y/N) !! не проверено !!: '))
if useproxy in ('y', 'Y'):
    proxytype = str(input('Введите тип proxy (http/https/socks4/socks5): '))
    proxyfolder = str(input('Перетяните файл с proxy: '))

fist_msg_delay_type = input('Задержка перед отправкой ПЕРВОГО сообщения. Целое число, либо диапазон (example: 0-20, or 50): ')
if '-' in fist_msg_delay_type:
    delayrange_firstmsg = fist_msg_delay_type.split('-')

every_msg_delay_type = input('Задержка перед отправкой последующих сообщений. Целое число, либо диапазон (example: 0-20, or 50): ')
if '-' in every_msg_delay_type:
    delayrange_everymsg = every_msg_delay_type.split('-')

sleep_when_typing = input('Время имитации печатания. Целое число, либо диапазон (example: 0-20, or 50): ')
if '-' in sleep_when_typing:
    range_typing_msg = sleep_when_typing.split('-')

msg_set = []
proxies_list = []
def rand_msg():
    global msg_set
    if 'msg_set' not in globals() or len(msg_set) < 1:
        msg_set = open('msg.txt', 'r', encoding='utf-8').read().splitlines()
    return(msg_set.pop(randint(0, len(msg_set)-1)))

def getproxy():
    global proxies_list
    if 'proxies_list' not in globals() or len(proxies_list) < 1:
        proxies_list = open(proxyfolder, 'r', encoding='utf-8').read().splitlines()
    return(proxies_list.pop(0))

def mainth(token, first_start, chat_id):
    if first_start == True:
        try:
            if '-' in fist_msg_delay_type:
                first_start_sleeping = randint(int(delayrange_firstmsg[0]), int(delayrange_firstmsg[1]))
            else:
                first_start_sleeping = fist_msg_delay_type
            if ':' in token:
                chat_id = token.split(':')[1]
                token = token.split(':')[0]
            session = requests.Session()
            session.headers['authorization'] = token
            if useproxy in ('y', 'Y'):
                lock.acquire()
                proxystr = getproxy()
                lock.release()
                session.proxies.update({'http': f'{proxytype}://{proxystr}', 'https': f'{proxytype}://{proxystr}'})
            r = session.get('https://discordapp.com/api/users/@me', verify=False)
            username = loads(r.text)['username']
            logger.info(f'Первый запуск для [{username}], сплю {str(first_start_sleeping)} секунд перед первым сообщением')
            sleep(int(first_start_sleeping))
        except Exception as error:
            logger.error(f'Ошибка при первоначальной настройке для [{token}]: {str(error)}')
            succinit = False
        else:
            succinit = True
    session = requests.Session()
    session.headers['authorization'] = token
    while succinit == True:
        first_start = False
        try:
            random_message = str(rand_msg())
            data = {'content': str(random_message), 'tts': False}
            r = session.post(f'https://discord.com/api/v9/channels/{chat_id}/typing', verify=False)
            if '-' in sleep_when_typing:
                time_sleep_typing = int(randint(int(range_typing_msg[0]), int(range_typing_msg[1])))
            else:
                time_sleep_typing = int(sleep_when_typing)
            logger.info(f'Имитирую печатание сообщения для [{username}] в течение {time_sleep_typing} сек')
            sleep(time_sleep_typing)
            r = session.post(
                f'https://discord.com/api/v9/channels/{chat_id}/messages', json=data, verify=False)
            if 'id' in loads(r.text):
                message_id = str(loads(r.text)['id'])
                logger.success(f'Сообщение [{random_message}] от [{username}] успешно отправлено')
                if delete_message_after_send in ('y', 'Y'):
                    r = session.delete(f'https://discord.com/api/v9/channels/{chat_id}/messages/{message_id}', verify=False)
                    if r.status_code == 204:
                        logger.success(f'Сообщение с ID {message_id} и содержимым [{random_message}] от [{username}] успешно удалено')
                    else:
                        logger.error(f'Не удалось удалить сообщение для [{username}], статус ответа: {str(r.status_code)}, содержимое ответа: {str(r.text)}')
            elif 'message' in loads(r.text):
                errormsg = loads(r.text)['message']
                if 'retry_after' in loads(r.text):
                    timesleep = float(loads(r.text)['retry_after'])
                    logger.error(f'Ошибка: {errormsg} для [{username}], сплю {str(timesleep)} секунд')
                    sleep(timesleep)
                    mainth(token, first_start)
                elif errormsg == 'Missing Access':
                    raise Exception('erroraccess')
                else:
                    raise Exception(errormsg)
            else:
                raise Exception(r.text)

            if '-' in every_msg_delay_type:
                time_to_sleep_everymsg = int(randint(int(delayrange_everymsg[0]), int(delayrange_everymsg[1])))
            else:
                time_to_sleep_everymsg = int(every_msg_delay_type)
            logger.info (f'Сплю {str(time_to_sleep_everymsg)} секунд для [{username}]')
            sleep(int(time_to_sleep_everymsg))

        except Exception as error:
            if str(error) == 'erroraccess':
                logger.error(f'Вы не можете отправлять сообщения в канале, выключаю поток для [{username}]')
                succinit = False
            else:
                logger.error(f'Ошибка для [{username}]: {str(error)}')
                pass

clear()
for _ in range(len(data)):
    while data:
        token = data.pop(0)
        first_start = True
        Thread(target=mainth, args=(token, first_start, chat_id,)).start()
