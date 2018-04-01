import config
from slackclient import SlackClient
import urllib.request
import requests
from time import sleep
import ssl
import shutil
# import caloriecounter
import gcp_interface

BOT_ACCESS_TOKEN = config.BOT_ACCESS_TOKEN
ACCESS_TOKEN = config.ACCESS_TOKEN
GCP_API_KEY = 'gcp_interface/gcp_api_key.txt'

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

    def update(self, name, add_calories, add_sodium, calorielimit=None, sodiumlimit=None):
        """
        @brief      Update user's caloric info.
        
        @param      name          The user name
        @param      add_calories  The addl. calories
        @param      add_sodium    The addl. sodium

        Note: if add* < 0, this function is essentially clear()
        """
        # load file
        users = {}
        with open('fffdb.txt', 'r') as f:
            for line in f:
                temp = eval(line)
                users[temp['name']] = temp

        if name in users and add_calories >= 0 and add_sodium >= 0:
            # update user
            users[name]['currcalories'] += add_calories
            users[name]['currsodium'] += add_sodium
            if not calorielimit and not sodiumlimit:
                users[name]['num_meals'] += 1
            if calorielimit:
                users[name]['calorielimit'] = calorielimit
            if sodiumlimit:
                users[name]['sodiumlimit'] = sodiumlimit
        elif name not in users:
            users[name] = {'name': name, 
                           'currcalories': add_calories,
                           'calorielimit': 2200, # default
                           'currsodium': add_sodium,
                           'sodiumlimit': 2300, # milligrams
                           'num_meals': 1
                           }
        elif add_calories < 0 or add_sodium < 0:
            users[name]['currcalories'] = 0
            users[name]['currsodium'] = 0
            users[name]['num_meals'] = 0

        # save file
        with open('fffdb.txt', 'w') as f:
            for key, value in users.items():
                f.write(str(value) + '\n')

    def display(self, name, channel):
        with open('fffdb.txt', 'r') as f:
            for line in f:
                temp = eval(line)
                if temp['name'] == name:
                    break

        self.send_message('*SUMMARY:*\n\nCalorie count/limit: %d/%d\nRemaining calories: %d calories\n\nSodium count/limit: %d/%d mg\nRemaining sodium: %d mg\n\nNumber of meals: %d\nAverage calories/meal: %d\nAverage sodium (mg)/meal: %d' % (temp['currcalories'], temp['calorielimit'], temp['calorielimit']-temp['currcalories'], temp['currsodium'], temp['sodiumlimit'], temp['sodiumlimit'] - temp['currsodium'], temp['num_meals'], temp['currcalories'] / temp['num_meals'] if temp['num_meals'] != 0 else 0, temp['currsodium'] / temp['num_meals'] if temp['num_meals'] != 0 else 0), channel)

    def handle_event(self, rtm_event):
        """
        @brief      Event handler.
        
        @param      rtm_event  The rtm event        
        """
        if len(rtm_event) == 0:
            return

        event = rtm_event[0]
        if 'channel' not in event or 'user' not in event:
            return

        channel = event['channel']
        prename = event['user']
        if 'file' in event and 'mimetype' in event['file'] and 'image' in event['file']['mimetype']:
            file_id = event['file']['id']
            self.send_message('Computing nutritional information...', channel)
            name = str(event['file']['name'])
            ext = name.split('.')[-1]
            name = 'images/' + prename + '.' + ext
            self.download_image(event['file']['url_private_download'], name)
            print('Downloaded %s' % file_id)

            labels = gcp_interface.gcp_labeller(GCP_API_KEY, name)
            if len(labels) > 0:
                self.send_message('You\'re consuming: %s!' % labels[0], channel)
            else:
                self.send_message('Nothing detected :(', channel)

            # nutrition = caloriecounter.count(name)
            # caloriecounter.print_nutrition_info(nutrition)
            
            # COMMENT THIS OUT AFTER ADDING IN CALORIE CODE
            self.update(prename, 0, 0)
            self.update(prename, -1, -1)
            ### INSERT CALORIE CODE HERE
            ############self.update(prename, 100, 0.1)
        elif 'type' in event and event['type'] == 'message':
            message = event['text']
            if 'set calorie ' in message:
                climit = int(message.replace('set calorie ', '').strip())
                print('Setting calorie limit to: %d' % climit)
                self.update(prename, 0, 0, climit, 0)
                self.send_message('Set calorie limit to: %d' % climit, channel)
            elif 'set sodium ' in message:
                slimit = int(message.replace('set sodium ', '').strip())
                print('Setting sodium limit to: %d' % slimit)
                self.update(prename, 0, 0, 0, slimit)
                self.send_message('Set sodium limit to: %d' % slimit, channel)
            elif 'clear' in message:
                print('Clearing daily counts.')
                self.update(prename, -1, -1)
                self.send_message('Cleared!', channel)
            elif 'end' in message or 'display' in message:
                if 'end' in message:
                    self.update(prename, -1, -1)
                self.display(prename, channel)
            elif 'help' in message:
                self.send_message('Available commands:\n\ndisplay:\tDisplays current counts and limits.\nset calorie [number]:\tSet the calories limit.\nset sodium [number]:\tSet the sodium limit.\nclear:\tClear the daily counts.\nend:\tEnd the day! Display and clear counts.', channel)

        # elif check for 'end'
        # elif check for 'clear'
        # elif check for 'display'
        # elif check for 'set calorie' or 'set sodium'

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