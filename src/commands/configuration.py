"""Commands for configuring certain features to work on a server"""
import discord
import logging
from discord.ext import commands

from utils import (
    convert_json_to_object,
    convert_to_json_str,    
)
from models import (
    get_or_create_guild_config,
    GuildConfiguration,
)

class FeatureConfigurationCog(commands.Cog):
    """ A custom cog containing commands for configuring features """
    def __init__(self, bot, redis_server):
        self.bot = bot
        self.redis_server = redis_server

    @commands.command()
    async def setup_gear_check(self, ctx, source_guild_id: int, realm: str):
        """
        Configures the bot to send gear check information to the channel in which this
        command was sent.
        
        Two arguments should be given:
        - The first is the ID of the server that has gear check 
          messages sent to it, via channels like (bwl-gear-check, mc-gear-check) etc.
        - The second is the name of the realm that you are playing on

        Example usage is:
        tog.setup_gear_check 806389180162506802 Faerlina
        """        
        if not ctx.guild:
            return await ctx.send('This command can only be used in the channel of a discord server!')

        dest_guild_config = get_or_create_guild_config(self.redis_server, ctx.guild.id)
        add_success = dest_guild_config.destination_config.add_gear_check_source(
            source_guild_id,
            ctx.channel.id,
            realm
        )
        if not add_success:
            return await ctx.send(
                'This server is already receiving gear check messages from ' + \
                'the given server. Could not add.'
            )

        source_guild = discord.utils.get(self.bot.guilds, id=source_guild_id)
        if source_guild is None:
            return await ctx.send(
                'Could not add gear check messaging because the bot ' + \
                'does not have access to the source guild.'
            )

        source_guild_config = get_or_create_guild_config(self.redis_server, source_guild_id)
        source_guild_config.source_config.add_gear_check_destination(
            ctx.guild.id,
            ctx.channel.id,
            realm
        )

        self.redis_server.set(ctx.guild.id, convert_to_json_str(dest_guild_config))
        self.redis_server.set(source_guild_id, convert_to_json_str(source_guild_config))
        await ctx.send(
            f'This server will now receive gear check messages for messages in {source_guild.name}.'
        )


    @commands.command()
    async def remove_gear_check(self, ctx, source_guild_id: int):
        """
        Removes this server from receiving gear check messages.
        One argument should be given:
        - The id of the server that has gear check messages sent to it,
          via channels like (bwl-gear-check, mc-gear-check) etc. 

         Example usage is:
         tog.remove_gear_check 806389180162506802
        """
        if not ctx.guild:
            return await ctx.send('This command can only be used in the channel of a discord server!')

        dest_guild_config = get_or_create_guild_config(self.redis_server, ctx.guild.id)
        remove_success = dest_guild_config.destination_config.remove_gear_check_source(
            source_guild_id
        )

        if not remove_success:
            return await ctx.send(
                'This server was already not receiving ' + \
                'alerts from the given server. Could not remove.'
            )


        source_guild = discord.utils.get(self.bot.guilds, id=source_guild_id)
        if source_guild is None:
            return await ctx.send(
                'Could not remove gear check messaging because the bot ' + \
                'does not have access to the source guild.'
            )
        source_guild_config = get_or_create_guild_config(self.redis_server, source_guild_id)
        source_guild_config.source_config.remove_gear_check_destination(
            ctx.guild.id
        )

        self.redis_server.set(ctx.guild.id, convert_to_json_str(dest_guild_config))
        self.redis_server.set(source_guild_id, convert_to_json_str(source_guild_config))
        await ctx.send(
            f'This server will no longer receive gear check messages for messages in {source_guild.name}.'
        )


    def get_guild_with_channel(self, channel_id):
        def does_guild_have_channel(guild, channel_id):
            channel = discord.utils.get(guild.channels, id=channel_id)
            return channel is not None

        return discord.utils.find(
            lambda g: does_guild_have_channel(g, channel_id),
            self.bot.guilds
        )


    @commands.command()
    async def setup_buff_alerts(self, ctx, source_channel_id: int):
        """
        Configures the bot to send buff alerts from a channel on another server to the 
        channel in which this command is sent.
        
        One argument should be given:
        - The ID of the channel on another server that will have buff alerts sent to it.

        Example usage is:
        tog.setup_buff_alerts 795575592501379073
        """ 
        if not ctx.guild:
            return await ctx.send('This command can only be used in the channel of a discord server!')

        dest_guild_config = get_or_create_guild_config(self.redis_server, ctx.guild.id)
        add_success = dest_guild_config.destination_config.add_buff_alert_source(
            source_channel_id,
            ctx.channel.id
        )

        if not add_success:
            return await ctx.send(
                'This server is already receiving buff alerts from the given ' + \
                'server. Could not add.'
            )

        source_guild = self.get_guild_with_channel(source_channel_id)
        if source_guild is None:
            return await ctx.send(
                'Could not setup buff alerts because the bot ' + \
                'does not have access to the source channel.'
            )

        source_guild_config = get_or_create_guild_config(self.redis_server, source_guild.id)
        source_guild_config.source_config.add_buff_alert_destination(
            ctx.guild.id,
            ctx.channel.id
        )

        source_channel = discord.utils.get(source_guild.channels, id=source_channel_id)
        self.redis_server.set(ctx.guild.id, convert_to_json_str(dest_guild_config))
        self.redis_server.set(source_guild.id, convert_to_json_str(source_guild_config))
        await ctx.send(f'This server is now listening for buff alerts from {source_channel.name}.')


    @commands.command()
    async def remove_buff_alerts(self, ctx, source_channel_id: int):
        """
        Removes this server from receiving buff alerts from a given channel on another server.
        One argument should be given:
        - The ID of the channel on another server that will have buff alerts sent to it.

         Example usage is:
         tog.remove_buff_alerts 795575592501379073
        """
        if not ctx.guild:
            return await ctx.send('This command can only be used in the channel of a discord server!')

        dest_guild_config = get_or_create_guild_config(self.redis_server, ctx.guild.id)
        remove_success = dest_guild_config.destination_config.remove_buff_alert_source(
            source_channel_id
        )

        if not remove_success:
            return await ctx.send(
                'This server was already not receiving ' + \
                'messages from the given server. Could not remove.'
            )        

        source_guild = self.get_guild_with_channel(source_channel_id)
        if source_guild is None:
            return await ctx.send(
                'Could not remove buff alerts because the bot ' + \
                'does not have access to the source channel.'
            )

        source_guild_config = get_or_create_guild_config(self.redis_server, source_guild.id)
        source_guild_config.source_config.remove_buff_alert_destination(
            ctx.guild.id,
        )

        source_channel = discord.utils.get(source_guild.channels, id=source_channel_id)
        self.redis_server.set(ctx.guild.id, convert_to_json_str(dest_guild_config))
        self.redis_server.set(source_guild.id, convert_to_json_str(source_guild_config))
        await ctx.send(f'This server will no longer receive buff alerts from {source_channel.name}.')

