"""Module containing the entrypoint to the bot"""
import discord
from discord.ext.commands import Bot
import logging
import redis

from buffs import (
    handle_buff_message,
    is_buff_message,
)
from commands.help import HelpCommandCog
from commands.configuration import FeatureConfigurationCog
from gear_check import ( 
    handle_gear_check_message,
    is_gear_check_message,
)

BOT_AUTHOR_ID = 822262145412628521
COMMAND_PREFIX = 'tog.'
redis_server = redis.Redis()

bot = Bot(command_prefix=COMMAND_PREFIX)
bot.add_cog(HelpCommandCog(bot))
bot.add_cog(FeatureConfigurationCog(bot, redis_server))

AUTH_TOKEN = str(redis_server.get('TOG_BOT_AUTH_TOKEN').decode('utf-8'))
WCL_TOKEN = str(redis_server.get('WCL_TOKEN').decode('utf-8'))

@bot.event 
async def on_ready():
    logging.debug(f'Successful Launch! {bot.user}')


@bot.event
async def on_message(message):
    """
    Handler for incoming messages to all channels.

    Depending on the channel that the message was sent to and the message's author,
    we may send additional messages from our bot in response.
    """
    try:
        if message.author.id == BOT_AUTHOR_ID:
            return
        elif is_gear_check_message(message):
            return await handle_gear_check_message(message, bot, WCL_TOKEN, redis_server)
        elif is_buff_message(message, bot, redis_server):
            return await handle_buff_message(message, bot, redis_server)
    except Exception as e:
        logging.error(e)
    await bot.process_commands(message)

# this blocks and should be the last line in our file
bot.run(AUTH_TOKEN) 