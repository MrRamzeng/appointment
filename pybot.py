import time
import sched
import threading

from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import (
    ViberConversationStartedRequest, ViberFailedRequest, ViberMessageRequest,
    ViberSubscribedRequest, ViberUnsubscribedRequest
)

app = Flask(__name__)

token_file = open('../token.key', 'r')
token = token_file.read()
viber = Api(BotConfiguration(
    name='Eladmin',
    avatar='https://dl-media.viber.com/1/share/2/long/vibes/icon/image/0x0/ea8c/' \
           'f127440c377210eafa4f15cdffed3d86c1f4bc74072f33ea1ea73785cc4eea8c.jpg',
    auth_token=str(token[:-1])
))


@app.route('/', methods=['POST'])
def incoming():
    viber_request = viber.parse_request(request.get_data().decode('utf8'))
    if isinstance(viber_request, ViberMessageRequest):
        import scraper
    elif isinstance(viber_request, ViberConversationStartedRequest) \
            or isinstance(viber_request, ViberSubscribedRequest) \
            or isinstance(viber_request, ViberUnsubscribedRequest):
        viber.send_messages(viber_request.sender.id, [
            TextMessage(None, None, viber_request.get_event_type())
        ])
    return Response(status=200)


def set_webhook(viber):
    viber.set_webhook('https://myf.westeurope.cloudapp.azure.com:443/')


if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(10, 1, set_webhook, (viber,))
    t = threading.Thread(target=scheduler.run)
    t.start()
    context = ('../server.crt', '../server.key')
    app.run(host='0.0.0.0', port=443, debug=True, ssl_context=context)
