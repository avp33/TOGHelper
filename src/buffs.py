"""Module for bot functionality related to world buffs"""
import discord
import logging

from requests_html import AsyncHTMLSession
from urllib import request

from constants import Constants
from models import get_or_create_guild_config

# TODO: remove once migrated
# TOG_BUFF_LISTENER_CHANNEL = 821529167286894612
# tog_listener_info = GuildAndChannelInfoWrapper(
#     Constants.TOG_GUILD_ID,
#     TOG_BUFF_LISTENER_CHANNEL
# )

# test_listener_info = GuildAndChannelInfoWrapper(
#     Constants.ALPHADECAY_LISTENER_TEST_SERVER,
#     830130841555697754
# )

# buff_channels_to_listeners_map = {
#     795575592501379073: [tog_listener_info],
#     830131836420227102: [test_listener_info]
# }

def is_buff_message(message, bot, redis_server):
    """ Returns whether the given message is a buff message that has listeners"""
    try:
        can_mention_everyone = message.author.guild_permissions.mention_everyone
        return (
            can_mention_everyone and message.mention_everyone and \
            len(get_destination_channels(message, bot, redis_server)) > 0
        )
    except Exception as e:
        logging.error(e)
        return False


async def handle_buff_message(message, bot, redis_server):
    """Handles the incoming message, forwarding it in an embed to any listening channels"""
    outgoing_channels = get_destination_channels(message, bot, redis_server)
    for channel in outgoing_channels:
        embed = discord.Embed()
        embed.add_field(
            name='A buff is dropping!',
            value=f'{message.content} \n [Go here for more info.]({message.jump_url})'
        )
        try:
            await channel.send(embed=embed)
            await channel.send('@here')
        except Exception as e:
            logging.error(e)


def get_destination_channels(message, bot, redis_server):
    """ Returns a list of Channels that are listening for buff messages """
    guild_config = get_or_create_guild_config(redis_server, message.guild.id)
    destination_infos = guild_config.source_config.buff_alert_infos
    channels = []
    for destination_info in destination_infos:
        guild = discord.utils.get(bot.guilds, id=destination_info.destination_guild_id)
        channel = discord.utils.get(guild.channels, id=destination_info.destination_channel_id)
        channels.append(channel)
    return channels