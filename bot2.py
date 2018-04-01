import config
from slackclient import SlackClient
import urllib.request
import requests
from time import sleep
import ssl
import shutil

BOT_ACCESS_TOKEN = config.BOT_ACCESS_TOKEN
ACCESS_TOKEN = config.ACCESS_TOKEN

class SlackBot():
    def __init__(self, access_token):
        """
        @brief      Class for slack bot.
        """
        self.sc = SlackClient(access_token)

    def rtm_socket_connected(self):
        """
        @brief      Connec to real time messaging.
                
        @return     Returns connection status.
        """
        return self.sc.rtm_connect()

    def send_message(self, message, channel):
        """
        @brief      Sends a message.
        
        @param      message  The message
        @param      channel  The channel
        
        @return     Returns status.
        """
        res = self.sc.api_call('chat.postMessage', channel=channel, text=message)
        return res

    def read_rtm_messages(self):
        """
        @brief      Reads messages.
                
        @return     Returns read message.
        """
        res = self.sc.rtm_read()
        return res

    def download_image(self, url, name):
        """
        @brief      Downloads an image.
        
        @param      url   The url
        @param      name  The name of the image        
        """
        headers = {'Authorization': 'Bearer ' + BOT_ACCESS_TOKEN}
        opener = urllib.request.build_opener()
        opener.addheaders = [('Authorization', headers['Authorization'])]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, name)

    def imgur_upload(self, file_name):
        """
        @brief      Upload image to imgur.
        
        @param      file_name  The file name
        
        @return     Returns public URL of image.
        """
        pass

    def handle_event(self, rtm_event):
        """
        @brief      Event handler.
        
        @param      rtm_event  The rtm event        
        """
        if len(rtm_event) == 0:
            return

        event = rtm_event[0]
        channel = event['channel']
        if 'file' in event and 'mimetype' in event['file'] and 'image' in event['file']['mimetype']:
            file_id = event['file']['id']
            self.send_message('Computing calories...', channel)
            name = str(event['file']['name'])
            ext = name.split('.')[-1]
            name = 'images/' + event['username'] + '.' + ext
            self.download_image(event['file']['url_private_download'], name)
            print('Downloaded %s' % file_id)

    def activate(self):
        """
        @brief      Activates slack bot.                
        """
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