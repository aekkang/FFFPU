import config
from slackclient import SlackClient
import urllib.request
import urllib.parse
import requests
from time import sleep
import ssl
from io import BytesIO
import shutil

BOT_ACCESS_TOKEN = config.BOT_ACCESS_TOKEN
ACCESS_TOKEN = config.ACCESS_TOKEN

class SlackBot():
    def __init__(self, access_token):
        self.sc = SlackClient(access_token)

    def rtm_socket_connected(self):
        return self.sc.rtm_connect()

    def send_message(self, message, channel):
        res = self.sc.api_call('chat.postMessage', channel=channel, text=message)
        return res

    def read_rtm_messages(self):
        res = self.sc.rtm_read()
        return res

    # def get_public_url(self, file_id):
    #     data = {'token': ACCESS_TOKEN, 'file': file_id}
    #     bdata = bytes(urllib.parse.urlencode(data), encoding='utf-8')
    #     api_url = 'https://slack.com/api/files.sharedPublicURL'
    #     res = urllib.request.urlopen(api_url, data=bdata)
    #     print(res)

    def download_image(self, url, name):
        headers = {'Authorization': 'Bearer ' + BOT_ACCESS_TOKEN}
        # res = requests.get(url, headers=headers)
        # with open(name, 'wb') as f:
        #     for chunk in res.iter_content(chunk_size=1024):
        #         if chunk:
        #             f.write(chunk)
        # with open(name, 'wb') as out_file:
        #     shutil.copyfileobj(BytesIO(res.content), out_file)
        opener = urllib.request.build_opener()
        opener.addheaders = [('Authorization', headers['Authorization'])]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, name)

    def handle_event(self, rtm_event):
        if len(rtm_event) == 0:
            return

        event = rtm_event[0]
        channel = event['channel']
        if 'file' in event and 'mimetype' in event['file'] and 'image' in event['file']['mimetype']:
            file_id = event['file']['id']
            self.send_message('We have received your food.', channel)
            # self.get_public_url(file_id)
            name = str(event['file']['name'])
            self.download_image(event['file']['url_private_download'], name)

    def activate(self):
        if self.rtm_socket_connected():
            print('Deployed!')
            while True:
                try:
                    self.handle_event(self.read_rtm_messages())
                except Exception as e:
                    print(e)
                sleep(0.05)
        else:
            print('Error, check access token!')

if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context

    bot = SlackBot(BOT_ACCESS_TOKEN)
    bot.activate()