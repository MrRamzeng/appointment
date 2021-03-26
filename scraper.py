import requests, urllib3, threading, urllib.parse as urlparse, atexit, time

from urllib.parse import parse_qs
from datetime import date, datetime
from bs4 import BeautifulSoup
from viberbot.api.messages import URLMessage
from viberbot.api.messages.text_message import TextMessage
from apscheduler.schedulers.background import BackgroundScheduler

host = 'https://er.medkirov.ru'
set_links = set()
clients = ['LL3mgrqogJK9yxBlHFvvSQ=='] #, 'J+GEZQj348xxUEK77WH/gg==', 'tPJ5GNMNYhx6MP0XND9Dmw==']

import pybot


def search_tickets():
    urllib3.disable_warnings()
    current_year = date.today().year
    current_week = date.today().isocalendar()[1]
    last_week = current_week + 3
    global host, set_links
    while current_week <= last_week:
        url = host + '/cities/297576/hospitals/215/specializations/64/calendars/?week=' + str(current_week) + '&year=' + str(current_year)
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        table_rows = soup.find_all(class_='doctor')
        for data in table_rows:
            ticket = data.find(class_='freeTickets')
            if ticket:
                ticket_url = host + ticket.find_parent('a')['href']
                parsed = urlparse.urlparse(ticket_url)
                ticket_date = datetime.strptime(
                    parse_qs(parsed.query)['date'][0], '%d.%m.%Y'
                )
                response = requests.get(ticket_url, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                times = soup.find_all('a', class_='kticket-free')
                doctor = soup.find('address').find(class_='media-heading').text
                if doctor == 'Довыденко Виктория Евгеньевна':
                    for ttime in times:
                        link = host + ttime['href']
                        if link not in set_links:
                            text = ticket_date.strftime('%d.%m.%Y') + ' в ' + ttime.text + \
                                   '\n' + doctor + '\n' + link
                            for client in clients:
                                pybot.viber.send_messages(
                                    client, [TextMessage(text=text)]
                                )
                            set_links.add(link)
                        time.sleep(5)
        current_week += 1


scheduler = BackgroundScheduler()
scheduler.add_job(func=search_tickets, trigger='interval', seconds=5)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
