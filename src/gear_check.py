"""Module for bot functionality related to gear checking"""

import discord
import logging
import re

from requests_html import AsyncHTMLSession
from urllib import request

from constants import Constants
from models import get_or_create_guild_config

GEAR_CHECK_CHANNEL_SUFFIX = 'gear-check'

# use 3+ chars after the / so links to sixtyupgrades.com don't trigger the bot
SIXTY_UPGRADES_REGEX = "(?P<url>https?://([^\s]+.)?sixtyupgrades.com/[a-zA-Z0-9]{3,}[^\s]+)"
PRIVATE_SIXTY_UPGRADES_REGEX = "(?P<url>https?://([^\s]+.)?sixtyupgrades.com/character/[^\s]+)"
WOWHEAD_GEAR_CHECK_REGEX = "(?P<url>https?://([^\s]+.)?classic.wowhead.com/gear-planner/[^\s]+)"
SUPPORTED_GEAR_URL_REGEXES = [
    SIXTY_UPGRADES_REGEX,
    WOWHEAD_GEAR_CHECK_REGEX,
]

# There seems to be an odd bug (either with requests_html or with caching in sixtyupgrades)
# where sometimes on the first load of a gear check url,
# we don't actually render the page, so the dom query fails. 
# Subsequent tries seem to work, though, so we will retry up to this many times. 
MAX_FETCH_CHARACTER_NAME_RETRIES = 5


# maps a channel prefix like 'mc' to the corresponding zone id in warcraft logs
channel_prefix_to_zone_id_map = {
    'mc': 1000,
    'bwl': 1002,
    'aq40': 1005,
    'naxx': 1006
}

def is_gear_check_message(message):
    """Returns whether the given message was sent in a gear check channel"""
    try: 
        channel_name = message.channel.name
        components = channel_name.split(GEAR_CHECK_CHANNEL_SUFFIX)
        return components[-1] == GEAR_CHECK_CHANNEL_SUFFIX and components[0] in channel_prefix_to_zone_id_map
    except Exception as e:
        logging.error(e)
        return False

async def handle_gear_check_message(message, bot, wcl_token, redis_server):
    """
    Handler for incoming gear check messages.

    Parses the message and sends a message with a link to the original 
    as well as a link to the player's warcraft logs for the relevant raid.
    """
    destination_infos = get_destination_infos(message, bot, redis_server)
    if len(destination_infos) == 0:
        return

    channel_prefix = str(message.channel).split('-')[0]
    zone_id = channel_prefix_to_zone_id_map.get(channel_prefix, None)
    if not zone_id:
        return

    gear_url = None
    for regex in SUPPORTED_GEAR_URL_REGEXES:
        try:
            gear_url = re.search(regex, message.content).group("url")
        except:
            continue

    if gear_url is None:
        # a message was sent to the channel that wasn't for a gear check
        return

    character_name = await get_character_name(gear_url, message)

    if not character_name and re.match(PRIVATE_SIXTY_UPGRADES_REGEX, gear_url):
        await message.reply(
            f'{message.author.mention} your link was private. Please post the ' + \
            'public link to your gear set.'
        )
        return

    if not re.match(SIXTY_UPGRADES_REGEX, gear_url):
        await message.reply(
            f'{message.author.mention} Please use https://sixtyupgrades.com/ to post your gear. ' + \
            'Doing this lets us know you know how to follow directions and helps us with our decision making. Thanks!'
        )

    for destination_info in destination_infos:
        wcl_url = get_warcraft_logs_url(zone_id, character_name, wcl_token, destination_info.realm)

        wcl_message = f'Please also check their [raid logs]({wcl_url}).' if wcl_url is not None \
                  else f'Raid logs could not be retrieved for character: {character_name}'
        embed = discord.Embed()
        embed.add_field(
            name=f'{message.author.display_name} just submitted a gear check request in ' + \
                 f'{message.channel.name}:',
            value=f'You can view it [here]({message.jump_url}). \n {wcl_message}'
        )
        guild = discord.utils.get(bot.guilds, id=destination_info.destination_guild_id)
        channel = discord.utils.get(guild.channels, id=destination_info.destination_channel_id)
        await channel.send(embed=embed)


async def get_character_name(gear_url, message):
    """
    It is *sometimes* the case that discord users don't update their username 
    to be their character name (eg for alts).

    This method renders the gear_url in an HTML session and parses the page
    to attempt to find the character's name.

    This assumes a specific format of the page: player names are nested in
    an h3 element with css class named 'class-[player class]'

    Returns the character's name if successful, otherwise returns the message sender's
    display name in discord.
    """
    name = message.author.display_name
    if not re.match(SIXTY_UPGRADES_REGEX, gear_url):
        return name

    for i in range(MAX_FETCH_CHARACTER_NAME_RETRIES):
        try:
            asession = AsyncHTMLSession()
            webpage = await asession.get(gear_url)
            await webpage.html.arender()
            query_selector = "h3[class^='class-']"
            name = webpage.html.find(query_selector, first=True).text
            break
        except Exception as e:
            logging.error(e)
        finally:
            await asession.close()
    return name


def get_warcraft_logs_url(zone_id, character_name, wcl_token, realm):
    """ 
    Returns the warcraft logs url for the player with the given character name 
    and the given zone id.

    Returns None if warcraft logs could not be found for the given character.
    """
    parse_url = f'https://classic.warcraftlogs.com:443/v1/parses/character/' + \
            f'{character_name}/{realm}/US' + \
            f'?zone={zone_id}&api_key={wcl_token}'
    try:
        res = request.urlopen(parse_url)
        if res.status != 200:
            return None
    except Exception as e:
        print(e)
        return None
    return f'https://classic.warcraftlogs.com/character/us/{realm}/' + \
           f'{character_name}?zone={zone_id}'


def get_destination_infos(message, bot, redis_server):
    """
    Returns the destination GearCheckConfigurationInfos should receive the gear check message.
    """
    guild_config = get_or_create_guild_config(redis_server, message.guild.id)
    return guild_config.source_config.gear_check_infos or []

