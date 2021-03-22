import requests
import urllib3
import threading
import urllib.parse as urlparse

from urllib.parse import parse_qs
from datetime import date, datetime
from bs4 import BeautifulSoup


def set_interval(func):
    e = threading.Event()
    while not e.wait(10):
        try:
            func()
        except Exception as error:
            with open('errors.log', 'a') as errorsLog:
                print(error, file=errorsLog)


host = 'https://er.medkirov.ru'
ticket_times = []
set_links = set()


def search_tickets():
    urllib3.disable_warnings()
    current_year = date.today().year
    current_week = date.today().isocalendar()[1]
    last_week = current_week + 5
    global ticket_times, host, set_links
    while current_week <= last_week:
        url = host + '/er/ereg3/cities/297576/hospitals/7/specializations/70/' \
                     'calendars/?week=' + str(current_week) + '&year=' + str(current_year)
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
                for time in times:
                    link = host + time['href']
                    if link not in set_links:
                        print(ticket_date.strftime('%d.%m.%Y'), doctor, time.text, link)
                        set_links.add(link)
        current_week += 1


set_interval(search_tickets)
