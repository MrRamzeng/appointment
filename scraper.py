import requests
import urllib3
import threading

from datetime import date
from bs4 import BeautifulSoup


def set_interval(func):
    e = threading.Event()
    while not e.wait(3000):
        try:
            func()
        except Exception as error:
            with open('errors.log', 'a') as errorsLog:
                print(error, file=errorsLog)


host = 'https://er.medkirov.ru'
ticket_times = []


def search_tasks():
    urllib3.disable_warnings()
    current_year = date.today().year
    current_week = date.today().isocalendar()[1]
    last_week = current_week + 5
    global ticket_times, host
    while current_week <= last_week:
        url = host + '/er/ereg3/cities/297576/hospitals/7/specializations/70/calendars' \
                     '/?week=' + str(current_week) + '&year=' + str(current_year)
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        table_rows = soup.find_all(class_='doctor')
        for data in table_rows:
            ticket = data.find(class_='freeTickets')
            if ticket:
                ticket_url = host + ticket.find_parent('a')['href']
                response = requests.get(ticket_url, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                times = soup.find_all('a', class_='kticket-free')
                doctor = soup.find('address').find(class_='media-heading').text
                if ticket_url[106] == '.':
                    day = '0' + ticket_url[105:107]
                else:
                    day = ticket_url[105:108]
                if ticket_url[108] == '.':
                    month = '0' + ticket_url[107:109]
                elif ticket_url[109] == '.':
                    month = '0' + ticket_url[108:110]
                else:
                    month = ticket_url[108:111]
                ticket_date = day + month + ticket_url[-4:]
                for time in times:
                    ticket_times.append(time.text + ': ' + host + time['href'])
                print(ticket_date, doctor, ticket_times)
        current_week += 1

set_interval(search_tasks)
