"""Commands for configuring certain features to work on a server"""
import discord
import logging
from discord.ext import commands

class FeatureConfigurationCog(commands.Cog):
    """ A custom cog containing commands for configuring features """
    def __init__(self, bot):
    	self.bot = bot

    @commands.command()
    async def setup_gear_check(self, ctx, *, observing_guild_id: int, realm: str):
    	"""
    	Configures the bot to send gear check information to the current channel.
		Two arguments should be give:
		- The first is the ID of the server that will have gear check 
		  messages sent to it, via channels like (bwl-gear-check, mc-gear-check) etc.
		- The second is the name of the realm that you are playing on

		Example usage is tog.configure_gear_check 806389180162506802 Faerlina
		"""
		return

	@commands.command()
	async def remove_gear_check(self, ctx, *, observing_guild_id: int):
		"""
		"""
		return

	@commands.command()
	async def setup_buff_alerts(self, ctx, *, observing_channel_id: int):
    	"""
    	Configures the bot to send buff alerts to the current channel.
		One argument should be give:
		- The ID of the channel that will have buff alerts sent to it.

		Example usage is tog.configure_buff_alerts 795575592501379073
		"""	
		return

	@commands.command()
	async def remove_buff_alerts(self, ctx, *, observing_channel_id: int):
		"""
		"""
		return