"""Module for bot functionality related to world buffs"""
import discord
import logging

from requests_html import AsyncHTMLSession
from urllib import request

from constants import Constants

class GuildAndChannelInfoWrapper(object):
    """ Wrapper around a guild and channel id """
    def __init__(self, guild_id, channel_id):
        self.guild_id = guild_id
        self.channel_id = channel_id


TOG_BUFF_LISTENER_CHANNEL = 821529167286894612
tog_listener_info = GuildAndChannelInfoWrapper(
    Constants.TOG_GUILD_ID,
    TOG_BUFF_LISTENER_CHANNEL
)

test_listener_info = GuildAndChannelInfoWrapper(
    Constants.ALPHADECAY_LISTENER_TEST_SERVER,
    830130841555697754
)

buff_channels_to_listeners_map = {
    795575592501379073: [tog_listener_info],
    830131836420227102: [test_listener_info]
}

def is_buff_message(message):
    """ Returns whether the given message is a buff message that has listeners"""
    listeners = buff_channels_to_listeners_map.get(message.channel.id, [])
    can_mention_everyone = message.author.guild_permissions.mention_everyone
    return len(listeners) > 0 and can_mention_everyone and message.mention_everyone


async def handle_buff_message(message, client):
    """Handles the incoming message, forwarding it in an embed to any listening channels"""
    outgoing_channels = get_listener_channels(message, client)
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


def get_listener_channels(message, client):
    """ Returns a list of Channels that are listening for buff messages """
    listeners = buff_channels_to_listeners_map.get(message.channel.id, [])
    channels = []
    for listener_info in listeners: 
        guild = discord.utils.get(client.guilds, id=listener_info.guild_id)
        channel = discord.utils.get(guild.channels, id=listener_info.channel_id)
        channels.append(channel)
    return channels