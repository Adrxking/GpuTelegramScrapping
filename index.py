import configparser
import json
import os
import re
import telegram_send

from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import PeerChannel

if os.path.exists("channel_messages.json"):
      os.remove("channel_messages.json")
else:
  print("The file does not exist")
  
if os.path.exists("messages.json"):
  os.remove("messages.json")
else:
  print("The file does not exist")


# some functions to parse json date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)


# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']
token = config['Telegram']['token']
channel = 'https://t.me/StockerGPUs'

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    user_input_channel = channel

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 300

    while True:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    with open('channel_messages.json', 'w') as outfile:
        json.dump(all_messages, outfile, cls=DateTimeEncoder)

with client:
    client.loop.run_until_complete(main(phone))

# Function for getting a word inside a String    
def contains_word(s, w):
    return f' {w} ' in f' {s} '

# Get the message column from the file
with open('channel_messages.json') as f:
    data = json.load(f)

    all_messages = []
    for message in data:
        mensaje = message['message']
        precio = ''
        # Get the 7 characters after Price: substring
        match = re.search(r'(?<=Precio: ).{7}', mensaje)
        if match:
            precio = match.group(0).replace('€', '')
            precio = precio.replace(' ', '')
            precio = float(precio.replace(',','.'))
        
        # Check if there is a message without price
        if (type(precio) is str):
            continue
        
        # Function that gets the model we wanna check and the maximum price we want
        def check_price(model,price):
            if (contains_word(mensaje, model)):
                if (precio <= price):
                    all_messages.append(mensaje)
                    
                return True
        
        if (check_price('#RTX3060', 550)):
            continue
        if (check_price('#RTX3060TI', 600)):
            continue
        if (check_price('#RTX3070', 650)):
            continue
        if (check_price('#RTX3070TI', 600)):
            continue
        if (check_price('#RTX3080', 1000)):
            continue
        if (check_price('#RTX3080TI', 1000)):
            continue
        if (check_price('#RTX3090', 1400)):
            continue
        if (check_price('#RX6600', 470)):
            continue
        if (check_price('#RX6700', 600)):
            continue
        if (check_price('#RX6800', 850)):
            continue
        if (check_price('#RX6900', 850)):
            continue
        
    with open('messages.json', 'w') as outfile:
        json.dump(all_messages, outfile, cls=DateTimeEncoder)
        
with open('messages.json') as f:
    data = json.load(f)
    telegram_send.send(messages=data)