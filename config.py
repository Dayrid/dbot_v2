import datetime
import config
import os

TOKEN = 'NzA5NDMwNTA0OTkwMTc5NDI5.XrlypA.s8B7h1NwrYIRHDG4QguqdvEWJkE'
role_id = 426611664943841280
# List of roles and their emojis
ROLES = {
    '⛏️': 744907137582628926, # Minecraft
    '🔫': 744907184860561410, # CS:GO
    '🤡': 744907100051865721, # Dota 2
    '👨‍⚖️': 744907060382269523, # GTA RP
    '🖊️': 452433684906377234, # Standart user role
    }

POST_ID = 744911776499630131

EXCROLES = ()

def wlog(command: str, ctx): # Запись лога в файл, главное напишите название команды и передайте обьект контекста ctx
    now = datetime.datetime.now()
    file = 'details.log'
    path = '/usr/local/bin/bot/'+file
    if not os.path.exists(path):
        o = open(path, 'w+')
        o.close()
    with open(path, 'a+') as logs:
        try:
            logs.write(f'[{now.strftime("%d-%m-%Y|%H:%M:%S")}][COMMAND] {ctx.message.author} used command "{command}"\n')
        except:
            print('Writting file was failed.')
