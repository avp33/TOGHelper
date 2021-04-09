"""Module containing the entrypoint to the bot"""
import discord
import logging
import redis

from buffs import (
    handle_buff_message,
    is_buff_message,
)
from gear_check import ( 
    handle_gear_check_message,
    is_gear_check_message,
)

BOT_AUTHOR_NAME = 'TOG Helper'

redis_server = redis.Redis()
client = discord.Client() # starts the discord client.
AUTH_TOKEN = str(redis_server.get('TOG_BOT_AUTH_TOKEN').decode('utf-8'))
WCL_TOKEN = str(redis_server.get('WCL_TOKEN').decode('utf-8'))

@client.event 
async def on_ready():
    logging.debug(f'Successful Launch! {client.user}')


@client.event
async def on_message(message):
    """
    Handler for incoming messages to all channels.

    Depending on the channel that the message was sent to and the message's author,
    we may send additional messages from our bot in response.
    """
    try:
        if message.author.name == BOT_AUTHOR_NAME:
            return
        elif is_gear_check_message(message):
            await handle_gear_check_message(message, client, WCL_TOKEN)
        elif is_buff_message(message):
            await handle_buff_message(message, client)
    except Exception as e:
        logging.error(e)


# this blocks and should be the last line in our file
client.run(AUTH_TOKEN) 