from dnevnikru.exceptions import DnevnikError
from dnevnikru.parsers import Parser
from dnevnikru import settings
import urllib3

from datetime import timedelta, datetime
from typing import Union
import requests
import time
from requests.adapters import HTTPAdapter, Retry

"""В качестве основы взял Dnevnik ru чтобы сэкономить время.
 Полностью было переписано множество функций для нормальной работы. Была выполнена оптимизация."""
class UTF8RedirectingSession(requests.Session):
    def get_redirect_target(self, resp):
        if resp.is_redirect and 'token' in resp.headers['location']:

            print("Direct destinations1 ", resp.headers['location'])
            ms = resp.headers['location'].encode('latin1').decode('utf8').split("returnUrl=")[1]
            splited_url = urls.split("/login/")
            second_splited_part = urls.split("returnUrl=")[1]
            end_url = splited_url[0].encode('idna').decode('utf8') + "/login/"+splited_url[1].replace("https://дневник.рф/","")+ms
            return end_url
        elif resp.is_redirect:
            print("Re direct ", resp.headers['location'])
            print("Debug ", resp.headers)
            return None
        return None
class Dnevnik:
    """Базовый класс Дневника"""

    def __init__(self, login: str, password: str) -> None:
        urllib3.disable_warnings()
        url = "https://login.dnevnik.ru/login/"
        self.__login, self.__password = login, password

        self._main_session = UTF8RedirectingSession()

       # self._main_session.mount('http://', adapter)
       # self._main_session.mount('https://', adapter)

        self._main_session.verify = False
        self._main_session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"})
        retry_counter = 0
        #while retry_counter < 5:
            #try:
        self._main_session.post(url, data={"login": self.__login, "password": self.__password})

        print("Logged with ", self._main_session.cookies)
        #self._main_session.post('https://login.dnevnik.ru',
                                        #json={"login": self.__login, "password": self.__password})
            #except socket.error as error:
                #print("Connection Failed due to socket - {}").format(error)
                #print("Attempting {} of 5").format(retry_counter)
                #time.sleep(3)
                #counter += 1
        self._school = 1000018821170
        if self._main_session.cookies.get("t0"):
            self._school = self._main_session.cookies.get("t0")
            return

    """Метод получения ДЗ"""
    def homework(self, datefrom=settings.DATEFROM, dateto=settings.DATETO, studyyear=settings.STUDYYEAR,
                 days: int = 10) -> dict:
        dateto = datefrom
        # Get homework
        print(datefrom, dateto)
        link = settings.HW_LINK.format(self._school, studyyear, datefrom, dateto)
        homework_response = self._main_session.get(link, headers={"Referer": link}).text
        if "Домашних заданий не найдено." in homework_response:
            return {"homeworkCount": 0, "homework": ()}
        last_page = Parser.last_page(homework_response)
        return Parser.get_homework(self, link=link, last_page=last_page, homework_response=homework_response)

    def isDefined(self):
        return Parser.isDefined(self._main_session)

    def week(self, info: str = "schedule", weeks: int = 0, dates="01.09.2022", section = 0) -> str:
        """Метод получения расписания на неделю"""
        # Checking the correctness of arguments
        assert info in settings.WEEK_INFORMATION, 'Invalid info'
        self._school = 0
        # get week
        return Parser.get_week_response(self._main_session,self._school,dates, section)
