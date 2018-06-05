
import telebot
import requests
import json
import time
from HackNU2018 import constants
from currency_converter import CurrencyConverter
from emoji import emojize

BOLD = '\033[1m'
END = '\033[0m'

bot = telebot.TeleBot(constants.token)

def make_request():
    answer = constants.error_message
    cur_data = json.load(open('cur_data.json'))
    url = 'https://api.skypicker.com/flights?flyFrom=' + cur_data['cityFrom'] + '&to=' + cur_data['cityTo'] + '&dateFrom=' + cur_data['dateFrom'] + \
          '&dateTo=' + cur_data['dateTo'] + '&partner=picky' + '&adults=' + str(cur_data['adults']) + '&children=' +\
          str(cur_data['children']) + '&dtimefrom=' + cur_data['dtimefrom'] +\
          '&dtimeto=' + cur_data['dtimeto']
    req = requests.get(url)
    write_json(req.json())
    req_dict = req.json()
    print(url + "\n" + cur_data['cityTo'])
    if 'data' not in req_dict:
        return answer
    elif len(req_dict['data']) == 0:
        answer = "No avaliable tickets"
    else:
        answer = jsontoString(req_dict['data'][0])
    return answer

def jsontoString(each):
    emm1 = emojize(":credit_card:", use_aliases=True)
    emm2 = emojize(":customs:", use_aliases=True)
    emm3 = emojize(":arrow_upper_right:", use_aliases=True)
    emm4 = emojize(":arrow_lower_right:", use_aliases=True)
    emm5 = emojize(":information_source:", use_aliases=True)
    ticket_url = each['deep_link']
    price = each['price']
    c = CurrencyConverter()
    tem1 = emm2 + "*From airport:* " + each['cityFrom'] + "\n" + emm2 + "*To airport:* " + each['cityTo'] + "\n"
    tem2 = emm3 + "*Time leaving:* " + time.strftime("%D %H:%M", time.gmtime(int(each['dTime']))) + "\n" + emm4 + "*Time arriving:* " + time.strftime("%D %H:%M",time.gmtime(int(each['aTime'])))
    tem3 = emm1 + "*The best Price:* €" + str(price) + " (" + str(c.convert(price, 'EUR', 'USD'))[:6] + " USD)" + "\n"
    answer = tem3 + tem1 + tem2 + "\n" + emm5 + "*For more info:*" + goo_shorten_url(ticket_url) + "\n\n"

    return answer

def translate_text(text):
    req_url = constants.translate_url + 'key=' + constants.translate_key + '&text=' + text + "&lang=en"
    r = requests.post(req_url)
    return r.json()['text'][0]

def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.close()

def log(message, answer):
    print("\n ----------------")
    from datetime import datetime
    print(datetime.now())
    print("Message from {0} {1}. ( id = {2}) \n Text: {3}".format(message.from_user.first_name, message.from_user.last_name,
                                                                  str(message.from_user.id), message.text))
    print("Answer: " + answer)

def goo_shorten_url(url):
    post_url = constants.shortener_url
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    return r.json()['id']


@bot.message_handler(commands=['start', 'help'])
def start_function(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/start', '/end')
    m1 = "Hello, my dear friend!\nI can find the cheapest airline tickets for you!"
    m2 = "You have to just write some information about destinations and date in the given order:\n"
    m3 = "City from you will fly out"
    m4 = "City where you will fly"
    m5 = "Date of the fly or first day of the interval"
    m6 = "Last day of the interval(optional)"
    m7 = "For example:\n_Moscow - Astana - 19/05/2018_  "
    m8 = "_Almaty - Kazan - 16/04/2018 - 25/04/2018_  "
    m9 = "*You can use any language that you want:3*"
    em1 = emojize(":airplane:", use_aliases=True)
    em2 = emojize(":date:", use_aliases=True)
    em3 = emojize(":small_orange_diamond:", use_aliases=True)
    em4 = emojize(":small_blue_diamond:", use_aliases=True)
    em8 = emojize(":arrow_upper_right:", use_aliases=True)
    em9 = emojize(":arrow_lower_right:", use_aliases=True)
    em5 = emojize(":white_check_mark:", use_aliases=True)
    em6 = emojize(":warning:", use_aliases=True)

    sendtext=m1+em1+"\n"+m2+em3+m3+em8+"\n"+em4+m4+em9+"\n"+em3+m5+em2+"\n"+em4+m6+em2+"\n"+m7+em5+"\n"+m8+em5+"\n\n"+em6+m9
    msg = bot.send_message(message.from_user.id, sendtext, reply_markup=user_markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, initial_case_step)

def home_buttons(user_id):
    em7 = emojize(":arrow_forward:", use_aliases=True)
    em8 = emojize(":blush:", use_aliases=True)
    em9 = emojize(":pencil2:", use_aliases=True)
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/start', '/end', '/addPassengers')
    user_markup.row('/next', '/choose_time')
    bot.send_message(user_id,em9+"Now you can choose number of passangers and suitable daytime:\n"
    +em7+"To add passengers press /addpassenger, please \n"+em7+"To choose time press /choose_time, please\n"
    +em7+"If you are single and the daytime is does not matter for you, press /next",reply_markup=user_markup)

@bot.message_handler(commands=['end'])
def end_function(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    emn1 = emojize(":wave:", use_aliases=True)
    emn2 = emojize(":pray:", use_aliases=True)
    emn3 = emojize(":sunrise_over_mountains:", use_aliases=True)
    emn4 = emojize(":tent:", use_aliases=True)
    open('cur_data.json', 'w').close()
    hide_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, "GoodBye, my dear friend! "+emn1+"\n"
     "Thank you for choosing our service! "+emn2+"\n"
     "We wish you safe and confortable flight, and unforgetable travel! "+ emn4+emn3, reply_markup=hide_markup)


@bot.message_handler(commands=['addPassengers'])
def handle_text(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    em11 = emojize(":man:", use_aliases=True)
    em12 = emojize(":baby:", use_aliases=True)
    em13 = emojize(":family:", use_aliases=True)
    em14 = emojize(":leftwards_arrow_with_hook:", use_aliases=True)
    em15 = emojize(":ballot_box_with_check:", use_aliases=True)

    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/addAdult', '/addChild')
    user_markup.row('/done', '/reset')
    bot.send_message(message.from_user.id, "Now add passanger, please! "+em13+
            "\nTo add adult passanger, press /addAdult "+em11+
            "\nTo add child passanger, press /addChild "+em12+
            "\nIf you have already chosen, press /done "+em15+
            "\nIf you mistaken, press /reset to reset values "+em14, reply_markup=user_markup)


@bot.message_handler(commands=['addAdult'])
def handle_text(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    cur_data = json.load(open('cur_data.json'))
    cur_data['adults'] = cur_data['adults'] + 1
    write_json(cur_data, 'cur_data.json')
    bot.send_message(message.from_user.id, 'Adults: ' + str(cur_data['adults']) + "; Children: " + str(cur_data['children'])+";")

@bot.message_handler(commands=['addChild'])
def handle_text(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    cur_data = json.load(open('cur_data.json'))
    cur_data['children'] = cur_data['children'] + 1
    write_json(cur_data, 'cur_data.json')
    bot.send_message(message.from_user.id, 'Adults: ' + str(cur_data['adults']) + "; Children: " + str(cur_data['children'])+";")

@bot.message_handler(commands=['reset'])
def handle_text(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    cur_data = json.load(open('cur_data.json'))
    cur_data['children'] = 0
    cur_data['adults'] = 1
    write_json(cur_data, 'cur_data.json')
    bot.send_message(message.from_user.id, 'Adults: ' + str(cur_data['adults']) + '; Children: ' + str(cur_data['children'])+";")

@bot.message_handler(commands=['done'])
def handle_text(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    cur_data = json.load(open('cur_data.json'))
    cur_data['id'] = 0
    write_json(cur_data, 'cur_data.json')
    answer = make_request()
    bot.send_message(message.from_user.id, answer, parse_mode="Markdown")
    home_buttons(message.from_user.id)

@bot.message_handler(commands=['next'])
def handle_text(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    answer = "No more tickets to search! Please press /start button";
    cur_data = json.load(open('cur_data.json'))
    cur_data['id'] = cur_data['id'] + 1
    write_json(cur_data, 'cur_data.json')
    req_dict = json.load(open('answer.json'))
    if len(req_dict['data']) <= cur_data['id']:
        pass
    else:
        answer = jsontoString(req_dict['data'][cur_data['id']])
    #answer = make_request()
    bot.send_message(message.from_user.id, answer, parse_mode="Markdown")

@bot.message_handler(commands=['choose_time'])
def choosing_function(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('morning', 'afternoon')
    user_markup.row('evening', 'night')
    user_markup.row('/start', '/end')
    msg = bot.send_message(message.from_user.id, "Now you have to choose suitable time for you:\n"
        "Send time interval by differing them by *hyphen*!\n"
        "_Example: 20:00-23:30_\n"
        "*You can just choose the on of the following variants:*\n"
        "_Morning(6:00-12:00)_\n"
        "_Afternoon(12:00-18:00)_\n"
        "_Evening (18:00-24:00)_\n"
        "_Night(00:00-6:00)_\n", reply_markup=user_markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, choose_time_step)

def choose_time_step(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    if message.text == "/start":
        home_buttons(message.from_user.id)
    elif message.text == "/end":
        end_function(message)
    else:
        if message.text == "morning":
            tfrom = '06:00'
            tito = '12:00'
        elif message.text == "afternoon":
            tfrom = '12:00'
            tito = '18:00'
        elif message.text == "evening":
            tfrom = '18:00'
            tito = '00:00'
        elif message.text == "night":
            tfrom = '00:00 '
            tito = '06:00'
        elif len(message.text.split('-'))!=2:
            tfrom = '00:00'
            tito = '00:00'
        else:
            tfrom, tito = message.text.split('-')

        tfrom = " ".join(tfrom.split())
        tito = " ".join(tito.split())
        cur_data = json.load(open('cur_data.json'))
        cur_data['dtimefrom'] = tfrom
        cur_data['dtimeto'] = tito
        cur_data['id'] = 0
        write_json(cur_data, 'cur_data.json')
        answer = make_request()
        bot.send_message(message.from_user.id, answer,parse_mode="Markdown")
        home_buttons(message.from_user.id)


def initial_case_step(message):
    bot.send_chat_action(message.from_user.id,'typing')
    if message.text == "/start":
        start_function(message)
        return
    elif message.text == "/end":
        end_function(message)
        return
    answer = constants.tryagain_message
    if message.text == "Hello" or message.text == "Привет" or message.text == "Пока" or message.text == "Bye":
        answer = message.text
    elif len(message.text) > 10:
        checker = True


        if len(message.text.split("-")) == 4:
            cityFrom, cityTo, dateFrom, dateTo = message.text.split("-")
            checker = False
        elif len(message.text.split("-"))== 3:
            cityFrom, cityTo, dateFrom = message.text.split("-")
            dateTo = dateFrom
            checker = False

        if(checker == False):
            cityFrom = " ".join(cityFrom.split())
            cityTo = " ".join(cityTo.split())
            dateFrom = " ".join(dateFrom.split())
            dateTo = " ".join(dateTo.split())
            cityFrom = translate_text(cityFrom)
            cityTo = translate_text(cityTo)
            data = {"cityFrom":cityFrom, "cityTo":cityTo, "dateFrom":dateFrom, "dateTo":dateTo,
                    "dtimefrom":'00:00', "dtimeto":"00:00", "adults":1,"children":0,
                    "id":0}
            write_json(data, filename='cur_data.json')
            answer = make_request()

    else:
        answer = constants.tryagain_message
    msg = bot.send_message(message.from_user.id, answer, parse_mode="Markdown")
    if len(answer)>50:
        home_buttons(message.from_user.id)
    else:
        start_function(message)
    log(message, answer)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
