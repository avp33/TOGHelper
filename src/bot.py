import discord
import logging
import os
import re
import redis
import urllib

from requests_html import AsyncHTMLSession

BOT_AUTHOR_NAME = 'TOG Helper'
GEAR_CHECK_CHANNEL_SUFFIX = 'gear-check'

# TODO: ideally this should be configurable when you add the bot to your server
OUTGOING_GEAR_CHECK_CHANNEL = 'pugs-gear-check'

# maps a channel prefix like 'mc' to the corresponding zone id in warcraft logs
channel_prefix_to_zone_id_map = {
    'mc': 1000,
    'bwl': 1002,
    'aq40': 1005,
    'naxx': 1006
}

# maps the id of the server that we are receiving messages on to 
# the id of the server that we will send the message to in a logs-check channel.
# TODO: ideally this should be configurable when you add the bot to your server
guild_id_to_outgoing_message_guild_id_map = {
    822265121606336512: 822895340058574868, # maps between my two test servers
    806389180162506802: 804969289349464074, # maps between TOG Pugs and TOG main server
}

redis_server = redis.Redis()
client = discord.Client() # starts the discord client.
AUTH_TOKEN = str(redis_server.get('TOG_BOT_AUTH_TOKEN').decode('utf-8'))

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
    if message.channel.name.endswith(GEAR_CHECK_CHANNEL_SUFFIX) \
        and message.author.name != BOT_AUTHOR_NAME:
        await handle_gear_check_message(message)

async def handle_gear_check_message(message):
    """
    Handler for incoming gear check messages.

    Parses the message and sends a message with a link to the original 
    as well as a link to the player's warcraft logs for the relevant raid.
    """     
    channel_prefix = str(message.channel).split('-')[0]
    zone_id = channel_prefix_to_zone_id_map.get(channel_prefix, None)
    if not zone_id:
        return

    try:
        gear_url = re.search(
            "(?P<url>https?://sixtyupgrades.com[^\s]+)", message.content
        ).group("url")
    except: 
        # a message was sent to the channel that wasn't for a gear check
        return

    character_name = await get_character_name(gear_url)
    wcl_url = get_warcraft_logs_url(message, zone_id, character_name)
    embed = discord.Embed()
    embed.add_field(
        name=f'{message.author.display_name} just submitted a gear check request in ' + \
             f'{message.channel.name}:',
        value=f'You can view it [here]({message.jump_url}). \n Please also check ' + \
              f'their [raid logs]({wcl_url}).'
    )

    outgoing_channel = get_outgoing_channel(message)
    await outgoing_channel.send(embed=embed)


async def get_character_name(gear_url):
    """
    It is *sometimes* the case that discord users don't update their username 
    to be their character name (eg for alts).

    This method renders the gear_url in an HTML session and parses the page
    to attempt to find the character's name.

    This assumes a specific format of the page: player names are nested in
    an h3 element with css class named 'class-[player class]'

    Returns the character's name if successful.
    """
    asession = AsyncHTMLSession()

    name = None
    try:
        webpage = await asession.get(gear_url)
        await webpage.html.arender()
        query_selector = "h3[class^='class-']"
        name = webpage.html.find(query_selector, first=True).text
    except Exception as e:
        logging.error(e)
    finally:
        await asession.close()
    return name

def get_warcraft_logs_url(message, zone_id, character_name):
    """ 
    Returns the warcraft logs url for the player with the given character name 
    (or discord name if the character name was None) and the given zone id.
    """
    return 'https://classic.warcraftlogs.com/character/us/faerlina/' + \
           f'{character_name or message.author.display_name}?zone={zone_id}';


def get_outgoing_channel(message):
    """
    Returns the channel to send the gear check message to for the given incoming message.
    """
    # fall back to the same guild (server) if it wasn't in the map 
    outgoing_guild_id = guild_id_to_outgoing_message_guild_id_map.get(
        message.guild.id, message.guild.id
    )

    outgoing_guild = discord.utils.get(client.guilds, id=outgoing_guild_id)
    if not outgoing_guild: 
        return

    outgoing_channel = discord.utils.get(
        outgoing_guild.channels, name=OUTGOING_GEAR_CHECK_CHANNEL
    )
    return outgoing_channel


# this blocks and should be the last line in our file
client.run(AUTH_TOKEN) 