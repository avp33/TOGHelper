import discord
import os
import re
import redis
import urllib

from requests_html import AsyncHTMLSession

BOT_AUTHOR_NAME = 'TOG Helper'
GEAR_CHECK_CHANNEL_SUFFIX = 'gear-check'
LOGS_CHECK_CHANNEL = 'logs-check'

# maps a channel prefix like 'mc' to the corresponding zone id in warcraft logs
channel_prefix_to_zone_id_map = {
	'mc': 1000,
	'bwl': 1002,
	'aq40': 1005,
	'naxx': 1006
}

redis_server = redis.Redis()
client = discord.Client() # starts the discord client.
AUTH_TOKEN = str(redis_server.get('TOG_BOT_AUTH_TOKEN').decode('utf-8'))

@client.event 
async def on_ready():
    print(f'Successful Launch!!! {client.user}')

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
		gear_url = re.search("(?P<url>https?://[^\s]+)", message.content).group("url")
	except: 
		return

	try:
		character_name = await get_character_name(gear_url)
	except Exception as e:
		print(e)
		character_name = None
	wcl_url = get_warcraft_logs_url(message, zone_id, character_name)
	embed = discord.Embed()
	embed.add_field(
		name=f'{message.author.name} just submitted a gear check request in {message.channel.name}:',
	 	value=f'You can view it [here]({message.jump_url}). \n Please also check their [raid logs]({wcl_url}).'
	)

	logs_channel = discord.utils.get(message.guild.channels, name=LOGS_CHECK_CHANNEL)
	await logs_channel.send(embed=embed)


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

	r = await asession.get(gear_url)
	await r.html.arender()
	query_selector = "h3[class^='class-']"
	return r.html.find(query_selector, first=True).text

def get_warcraft_logs_url(message, zone_id, character_name):
	""" 
	Returns the warcraft logs url for the player with the given character name 
	(or discord name if the character name was None) and the given zone id.
	"""
	return 'https://classic.warcraftlogs.com/character/us/faerlina/' + \
		   f'{character_name or message.author.name}?zone={zone_id}';

client.run(AUTH_TOKEN) # Pull Auth Token from above