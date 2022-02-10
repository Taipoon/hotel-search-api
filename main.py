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


YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route('/')
def hello_world():
    return "<h1>It works!</h1><p>API practical and hands-on.</p>"


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
    # hotel.py extract_words()
    results = hotel.extract_words(push_text)
    if isinstance(results, tuple):
        msg = hotel.hotel_search(*results, hits=5)
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
