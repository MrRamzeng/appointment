import requests
import urllib3
import re
import threading

from datetime import date
from bs4 import BeautifulSoup


def set_interval(func):
    e = threading.Event()
    while not e.wait(5000):
        try:
            func()
        except Exception as error:
            with open('errors.log', 'a') as errorsLog:
                print(error, file=errorsLog)


def search_tasks():
    urllib3.disable_warnings()
    current_year = date.today().year
    current_week = date.today().isocalendar()[1]
    last_week = current_week + 5
    host = 'https://er.medkirov.ru/'

    while current_week <= last_week:
        url = host + 'er/ereg3/cities/297576/hospitals/7/specializations/70/calendars' \
                     '/?week=' + str(current_week) + '&year=' + str(current_year)
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        table_rows = soup.find_all(class_='doctor')
        for data in table_rows:
            doctor = data.find('strong').text
            specialty = re.sub(r'\s+', ' ', data.find('div').text).strip()
            ticket = data.find(class_='freeTickets')
            if doctor and ticket:
                ticket_url = host + ticket.find_parent('a')['href']
                response = requests.get(ticket_url, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                ticket_times = soup.find_all('a', class_='kticket-free')
                for time in ticket_times:
                    time_link = host + time['href']
                    print(doctor, specialty, ticket_url[106:], time.text, time_link,
                          sep=' | ')
                    print('-' * 150)
                print('=' * 50)
        print('*' * 50)
        current_week += 1


set_interval(search_tasks)
