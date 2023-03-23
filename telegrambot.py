from telebot.async_telebot import AsyncTeleBot
import validators
import time
from dnevnikru import Dnevnik
from dateutil.parser import parse
from dnevnikru.parsers import Parser
from dnevnikru.parsers import DataOfState
from dnevnikru.parsers import Subject
from dnevnikru.parsers import FormattedDate
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import datetime

bot = AsyncTeleBot('5475091262:AAHJ-kHMZtmrNKbgSFkEktOfX9uBx9dsD8M')
users = {}

admins = {}

master_pass = "uKUEq92Q"

registered = {}

key32 = InlineKeyboardButton('Первая группа', callback_data='IS-1')
key33 = InlineKeyboardButton('Вторая группа', callback_data='IS-2')
keyboard981 = InlineKeyboardMarkup()
keyboard981.add(key32)
keyboard981.add(key33)

key1 = InlineKeyboardButton('Расписание на сегодня', callback_data='today')
hw = InlineKeyboardButton('Узнать ДЗ', callback_data='hw')
keyboard = InlineKeyboardMarkup()
keyboard.add(key1)
keyboard.add(hw)

dn = Dnevnik(login="Pavel.smirnov2004100", password="Anonimys442")

dn_1 = Dnevnik(login="ignatevaao", password="Cashgg1977")

@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    userId = message.from_user.id
    if not(userId in registered):
        await bot.send_message(message.chat.id, """\
        Привет, это бесплатный бот позволяющий просматривать расписание групп ИС-12 и подгрупп. \
        Введите в чате дату, на которую хотите узнать расписание(01.09.2022), или воспользуйтесь кнопками.
        """)
        await bot.send_message(message.chat.id,"Для начала выберите свою группу ИС",reply_markup=keyboard981)
    else:
        await bot.send_message(message.chat.id, """\
        Привет, это бесплатный бот позволяющий просматривать расписание групп ИС-12 и подгрупп. \
        Введите в чате дату, на которую хотите узнать расписание(01.09.2022), или воспользуйтесь кнопками.
        """,keyboard)

@bot.message_handler(commands=['dinner'])
async def dinner(message):
    userId = message.from_user.id
    comment = message.text.replace("/dinner", "").split(" ")
    if len(comment) < 5:
        await bot.send_message(message.chat.id, "Пожалуйста, распишите подробно время начала обеда,"
                                          " по КАЖДОМУ ДНЮ недели, начиная с понедельника. Например: /dinner 11:30-12:20 14:10-15:10")
        return

    if not(userId in admins):
        await bot.send_message(message.chat.id, "Вы не в режиме администратора")
    comment[:] = [x for x in comment if x]
    if len(comment) < 6:
        for i in range(1,4+1):
            comment.append("10:30")
    Parser.basicTime = comment
    await bot.send_message(message.chat.id, "Вы успешно обновили, список обедов.")
@bot.message_handler(commands=['admin'])
async def comment(message):
    comment = message.text.split(" ")
    password = ""
    if len(comment) > 1:
        password = comment[1]
    userId = message.from_user.id

    if userId in users:

        if not calculateCooldown(userId):
            await bot.send_message(message.chat.id, "Подождите немного перед повторным использованием бота")
            return

    putUserInCooldown(userId)
    if password == master_pass:
        admins[userId] = password

        await bot.send_message(message.chat.id, "Вы вошли в режим админа. "
                                                "Используйте /dinner чтобы изменить расписание обедов.")
        pass
    else:
        await bot.reply_to(message, "Пароль: "+ password + " неверен.")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
defaultCooldown = 8
def calculateCooldown(userId):
    return True if users[userId] < datetime.datetime.now() else False

def formatCooldown():
    currentDateTimeNow = datetime.datetime.now()
    formattedDateTime = datetime.timedelta(seconds=defaultCooldown)
    resultDateTime = currentDateTimeNow + formattedDateTime
    return resultDateTime
def putUserInCooldown(userId):
    users[userId] = formatCooldown()
@bot.message_handler(func=lambda message: True)
async def solveTest(message):
     link = message.text.split(" ")
     print(link, len(link))
     userId = message.from_user.id

     if len(link) >= 1:
         datas = link[0]
         if not(isDate(datas)):
            return
         else:
             if not (userId in registered):
                 await bot.send_message(message.chat.id, "Для начала выберите свою группу ИС",
                                        reply_markup=keyboard981)
                 return
             if userId in users:

                 if not calculateCooldown(userId):
                     await bot.send_message(message.chat.id,
                                            "Подождите немного перед повторным использованием бота")
                     return
             putUserInCooldown(userId)
             await bot.send_message(message.chat.id, formatedDate(datetime.datetime.strptime(datas, "%d.%m.%Y"), datas))

             end_date = datetime.datetime.strptime(datas, "%d.%m.%Y") + datetime.timedelta(days=1)

             fmt = end_date.strftime("%d.%m.%Y")
             data = dn.week(dates=datas, section=registered[userId])
             await bot.send_message(message.chat.id, "" + data, parse_mode="HTML")

def isDate(sts):
    string = sts

    try:
        ms = string.split(".")
        parse(string, fuzzy=False)

        if(string.count(".")<2):
            return False

        return True

    except:
        return False
@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    now = datetime.datetime.now()
    userId = call.from_user.id
    formatted = now.strftime("%d.%m.%Y")
    cdata = call.data

    global dn
    global dn_1
    if userId in users:

        if not calculateCooldown(userId):
            await bot.send_message(call.message.chat.id, "Подождите немного перед повторным использованием бота")
            return
    if cdata == "IS-1":
        putUserInCooldown(userId)
        registered[userId] = 1
        await bot.send_message(call.message.chat.id,"Мы установили вам первую группу. Вы будете видеть расписание/дз только для своей группы.",
                         reply_markup=keyboard)
    if cdata == "IS-2":
        putUserInCooldown(userId)
        registered[userId] = 0
        await bot.send_message(call.message.chat.id,"Мы установили вам вторую группу. Вы будете видеть расписание/дз только для своей группы.",
                      reply_markup=keyboard)
    if not(userId in registered):
        await bot.send_message(call.message.chat.id,"Для начала выберите свою группу ИС",reply_markup=keyboard981)
        return
    if (not (dn.isDefined())):
        dn = Dnevnik(login="Pavel.smirnov2004100", password="Anonimys442")
        dn_1 = Dnevnik(login="ignatevaao", password="Cashgg1977")
        print("Reboot: Reassigned datas, because DN cant define.")
    if call.data == "hw":
        keyboard421 = InlineKeyboardMarkup()

        end_dates = datetime.date.today() + datetime.timedelta(days=1)

        fmt = end_dates.strftime("%d.%m.%Y")
        print("DATE ",fmt, "Now date ", formatted)

        btn91 = InlineKeyboardButton(text="ДЗ на сегодня",callback_data="hw"+formatted)
        btn912 = InlineKeyboardButton(text="ДЗ на " + fmt,callback_data="hw"+fmt)
        keyboard421.add(btn91)
        keyboard421.add(btn912)
        await bot.send_message(call.message.chat.id, "Выберите, даты на которые хотите увидеть дз.", reply_markup=keyboard421)
        return
    if "hw" in call.data and len(call.data) > 3 and registered[userId] == 0:
        keyboard421 = InlineKeyboardMarkup()

        putUserInCooldown(userId)
        print(cdata)
        dates = call.data.replace("hw", "")
        year = now.year

        end_date = datetime.datetime.strptime(dates, "%d.%m.%Y") + datetime.timedelta(days=1)

        fmt = end_date.strftime("%d.%m.%Y")

        print("DATE ", fmt, "Now date ", formatted)

        btn912 = InlineKeyboardButton(text="ДЗ на " + fmt, callback_data="hw" + fmt)

        keyboard421.add(btn912)

        hw = dn.homework(datefrom=dates, dateto=dates)['homework']

        if (len(hw) < 1):
            print("I see empty homework, try rerun connect...")

            dn = Dnevnik(login="Pavel.smirnov2004100", password="Anonimys442")

            hw = dn.homework(datefrom=dates, dateto=dates)['homework']
        output_str = ""
        for i in hw:
            output_str +="\n"+ i[2] + " ->\n\n<b>Предмет: </b>" + i[0] + "\n<b>Задание: </b>"+i[1]+"\n"
        if len(output_str) < 2:
            await bot.send_message(call.message.chat.id, dates+" На данную дату ДЗ не задано. ¯\_(ツ)_/¯", reply_markup=keyboard421)
            return
        else:
            await bot.send_message(call.message.chat.id, "<b>Домашние задания:</b> \n" + output_str,parse_mode="HTML", reply_markup=keyboard421)
    if "hw" in call.data and len(call.data) > 3 and registered[userId] == 1:
            keyboard421 = InlineKeyboardMarkup()

            putUserInCooldown(userId)
            dates = call.data.replace("hw", "")
            year = now.year

            end_date = datetime.datetime.strptime(dates, "%d.%m.%Y") + datetime.timedelta(days=1)

            fmt = end_date.strftime("%d.%m.%Y")

            print(fmt)

            btn912 = InlineKeyboardButton(text="ДЗ на " + fmt, callback_data="hw" + fmt)

            keyboard421.add(btn912)

            hw = dn_1.homework(datefrom=dates, dateto=dates)['homework']
            output_str = ""
            if(len(hw) < 1):
                print("I see empty homework, try rerun connect...")

                dn = Dnevnik(login="Pavel.smirnov2004100", password="Anonimys442")

                hw = dn.homework(datefrom=dates, dateto=dates)['homework']
            for i in hw:
                output_str += "\n" + i[2] + " ->\n\n<b>Предмет: </b>" + i[0] + "\n<b>Задание: </b>" + i[1] + "\n"
            if len(output_str) < 2:
                await bot.send_message(call.message.chat.id, dates + " На данную дату ДЗ не задано. ¯\_(ツ)_/¯",
                                       reply_markup=keyboard421)
                return
            else:
                await bot.send_message(call.message.chat.id, "<b>Домашние задания:</b> \n" + output_str,
                                       parse_mode="HTML", reply_markup=keyboard421)
        #TODO
    print("TODAY day is ", datetime.date.today())
    if "update" in call.data and isDate(call.data.replace("update","")):
        putUserInCooldown(userId)
        print("UUPDATED!")
        request = call.data.replace("update","")

        updateDate = datetime.datetime.strptime(request, "%d.%m.%Y")
        end_date = updateDate + datetime.timedelta(days=1)

        fmt = end_date.strftime("%d.%m.%Y")
        todayFmt = datetime.date.today().strftime("%d.%m.%Y")
        data = dn.week(dates=request, section=registered[userId])
        if(data == 'error'):
            print("I see error, try rerun connect...")
            dn = Dnevnik(login="Pavel.smirnov2004100", password="Anonimys442")

            data = dn.week(dates=request, section=registered[userId])

        key9 = InlineKeyboardButton('Расписание на сегодня', callback_data='today')
        key10 = InlineKeyboardButton('Расписание на '+fmt, callback_data=fmt)
        key11 = InlineKeyboardButton('Обновить расписание', callback_data="update" + todayFmt)

        keyboard87 = InlineKeyboardMarkup()
        if request != todayFmt:
            keyboard87.add(key9)
        keyboard87.add(key10)
        keyboard87.add(key11)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                    text="<b>Обновлено: </b>" + todayFmt + "\n\n" + data,parse_mode="HTML",reply_markup=keyboard87)


    if call.data == "today":
        putUserInCooldown(userId)
        end_date = datetime.date.today() + datetime.timedelta(days=1)

        fmt = end_date.strftime("%d.%m.%Y")

        await bot.send_message(call.message.chat.id, formatedDate(now, formatted))


        key21 = InlineKeyboardButton('Расписание на ' + fmt, callback_data=fmt)

        key11 = InlineKeyboardButton('Обновить расписание', callback_data="update"+formatted)

        data = dn.week(dates=formatted,section=registered[userId])
        #data = dn.week(dates="20.09.2022", section=0)
        print("User ID ", registered[userId])
        print(formatted)
        #if (len(data) <= 0):
            #dn = Dnevnik(login="Pavel.smirnov2004100", password="Anonimys442")

            #data = dn.week(dates=formatted,section=registered[userId])
        if(data == 'error'):
            print("I see error, try rerun connect...")
            dn = Dnevnik(login="Pavel.smirnov2004100", password="Anonimys442")

            data = dn.week(dates=formatted, section=registered[userId])
        keyboard12 = InlineKeyboardMarkup()

        keyboard12.add(key21)
        keyboard12.add(key11)
        await bot.send_message(call.message.chat.id,"" + data,parse_mode="HTML",reply_markup=keyboard12)

    sb = call.data
    print(sb)
    if isDate(sb):
        putUserInCooldown(userId)
        await bot.send_message(call.message.chat.id, formatedDate(datetime.datetime.strptime(sb,"%d.%m.%Y"), sb))

        end_date = datetime.datetime.strptime(sb,"%d.%m.%Y") + datetime.timedelta(days=1)

        fmt = end_date.strftime("%d.%m.%Y")

        key9 = InlineKeyboardButton('Расписание на сегодня', callback_data='today')
        key10 = InlineKeyboardButton('Расписание на '+fmt, callback_data=fmt)
        key11 = InlineKeyboardButton('Обновить расписание', callback_data="update" + sb)

        keyboard87 = InlineKeyboardMarkup()
        keyboard87.add(key1)
        keyboard87.add(key10)
        keyboard87.add(key11)
        print(sb)
        print("SECTION IS ", registered[userId])
        data = dn.week(dates=sb,section=registered[userId])
        if(data == 'error'):
            print("I see error, try rerun connect...")
            dn = Dnevnik(login="Pavel.smirnov2004100", password="Anonimys442")

            data = dn.week(dates=sb, section=registered[userId])
        #if (len(data) <= 0):
            #dn = Dnevnik(login="Pavel.smirnov2004100", password="Anonimys442")

            #data = dn.week(dates=formatted,section=registered[userId])

        print(data)
        await bot.send_message(call.message.chat.id, "" + data, parse_mode="HTML", reply_markup=keyboard87)


    elif call.data == "yesterday":
        await bot.answer_callback_query(call.id, "Answer is No")
def formatedDate(dd, _date):
    fs = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    ss = ['Будни'] * 5 + ['Выходной'] * 2
    return FormattedDate(number=dd.day, name=fs[dd.weekday()], status=ss[dd.weekday()], formatted=_date).outputformatted()
def isLink(link):
    return validators.url(link)

asyncio.run(bot.polling(non_stop=True, request_timeout=90))

