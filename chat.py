from chatterbot import ChatBot


bot = ChatBot(
    'Sakura'
)

def r(s):return bot.get_response(s).text

while True:
    i = input('>>> ').strip()
    if i != 'exit':
        print(r(i))
    else:
        break