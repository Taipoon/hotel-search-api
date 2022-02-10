import os

from flask import Flask
from flask import request
from flask import abort

from linebot import LineBotApi
from linebot import WebhookHandler

from linebot.exceptions import InvalidSignatureError

from linebot.models import MessageEvent
from linebot.models import TextMessage
from linebot.models import TextSendMessage

import hotel


app = Flask(__name__)

os.environ['YOUR_CHANNEL_ACCESS_TOKEN'] = 'EHzVhdLA2BAf3L1 + 69lmGLewoACE / 4Ekym9riUQo6W6E69WyaPBebrfE8PHM4DF2bmbKpNZvG7Cj7U6Y3uke5cYh + P0Leb4J1sVgz3uIJFrdCRepiD5i0owdW + Fex'
os.environ['YOUR_CHANNEL_SECRET'] = '15201d48c9429e2e5d9e8a6032af16dc'

YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route('/')
def hello_world():
    return "Hello World!"


@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body:', body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print('Invalid signature. Please check your channel access token/channel secret.')
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    push_text = event.message.text
    print(push_text)
    # hotel.py extract_words()
    results = hotel.extract_words(push_text)
    if isinstance(results, tuple):
        msg = hotel.hotel_search(*results)
    else:
        msg = results
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg)
    )


if __name__ == '__main__':
    port = os.getenv('PORT')
    if port:
        port = int(port)
    app.run(host='0.0.0.0', port=port)
