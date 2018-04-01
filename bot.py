import config
from slackclient import SlackClient
import urllib.request
import shutil
import requests
import os
import json
from time import sleep
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

BOT_ACCESS_TOKEN = config.BOT_ACCESS_TOKEN

class SlackBot(object):
    '''
    This is a wrapper for the slackclient library that you can use if you find
    helpful. Add methods as you see fit. Only a bot access token that starts
    with xoxb needs to be provided as an input argument.
    '''
    def __init__(self, access_token):
        self.sc = SlackClient(access_token)

    def rtm_socket_connected(self):
        '''
        Checks if the bot is connected to the real time messaging socket, which
        allows it to monitor messages in the slack in real-time.
        '''
        return self.sc.rtm_connect()

    def send_message(self, message, channel):
        '''
        Sends a message to a channel. The message can be a formatted markdown
        message. The channel can be a DM, MPDM (multiple person DM), or a public
        or private channel.
        '''
        res = self.sc.api_call('chat.postMessage', channel=channel, text=message)
        return res

    def read_rtm_messages(self):
        '''
        Reads the incoming stream of real time messages from all channels the
        bot is a member of.
        '''
        res = self.sc.rtm_read()
        return res

    def download_file(self, url):
        header = {'Authorization': ' '.join(['Bearer', 'xoxp-328288475393-334002442113-340311699335-0b267b7ab3529184fdd0b248547fd051'])}
        # res = requests.get(url, headers=header)

        # if res.status_code == 200:
        req = urllib.request.Request(url)
        req.add_header('Authorization', ' '.join(['Bearer', 'xoxp-328288475393-334002442113-340311699335-0b267b7ab3529184fdd0b248547fd051']))
        with urllib.request.urlopen(req) as response:
            with open('/Users/joshuachen/git_repos/FFFPU/food.jpg', 'wb') as f:
                f.write(response.content)
        # with urllib.request.urlopen(req) as response, open('/Users/joshuachen/git_repos/FFFPU/food.jpg', 'wb') as outfile:
        #     shutil.copyfileobj(response, outfile)
        # else:
        #     print('Download failed.')

    def handle_event(self, rtm_event):
        '''
        Handles all real time messaging events.
        '''
        if len(rtm_event) != 0:
            event = rtm_event[0]
            channel = event['channel']
            if 'file' in event:
                file = event['file']
                file_id = file['id']
                url = file['url_private']
                if 'mimetype' in file and 'image' in file['mimetype']:
                    self.send_message('we have received your image', channel)
                    print('received %s' % file_id)
                    self.download_file(url)


        # if 'file' in event and 'mimetype' in event['file']:
        #     channel = event['channel']
        #     file = event['file']
        #     file_id = file['id']

        #     if 'image' in file['mimetype']:
        #         print('received image: %s' % file_id)
        #         res = self.sc.api_call('files.sharedPublicURL', file_id)
        #         print(res)
        #         url = file['url_private']
        #         data = {'Authorization': ' '.join(['Bearer', BOT_ACCESS_TOKEN])}
        #         json_data = json.dumps(data)
        #         print(json_data)
                
        #         res = requests.get(url, headers=data)
        #         if res.status_code == '200':
        #             res.?
        #         else:
        #             print('Download failed.')

        #         d = json.loads(res.content)
        #         d[]

        #         self.send_message('we\'ve received your picture!', event['channel'])
        #         with urllib.request.urlopen(url) as response, open('food.jpg', 'wb') as out:
        #             print(response.read())
        #             shutil.copyfileobj(response, out)

    def activate(self):
        '''
        Starts the bot, which monitors all messages events from channels it is a
        part of and then sends them to the message handler.
        '''
        if self.rtm_socket_connected():
            print('Bot is up and running\n')
            while True:
                sleep(0.05)
                try:
                    self.handle_event(self.read_rtm_messages())
                except:
                    continue
        else:
            print('Error, check access token!')

if __name__ == '__main__':
    bot = SlackBot(BOT_ACCESS_TOKEN)
    bot.activate()
