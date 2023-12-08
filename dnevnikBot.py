import requests
from dnevnikru import Dnevnik
from dnevnikru.parsers import Parser
from dnevnikru.parsers import DataOfState
from dnevnikru.parsers import Subject
from dnevnikru.parsers import FormattedDate
from pprint import pprint

isdef = dn_1.isDefined()
print(isdef)
data = dn_1.week(dates="13.03.2023", section=0)
data_1 = dn_1.week(dates="13.03.2023", section=0)
#data_2 = dn.week(dates="26.10.2022", section=0)
#hw = dn.homework(studyyear=2022, datefrom='26.10.2022', dateto='28.10.2022')['homework']
result = requests.get("https://xn--b1addnkoc.xn--p1ai").text
#print(result)
print(data)

print("New data\n", data_1)

