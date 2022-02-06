"""Module containing the help command for the bot"""
import discord

from discord.ext import commands

class TOGHelpCommand(commands.MinimalHelpCommand):
    """
    Class that implements the help command for the bot

    See https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.HelpCommand.send_bot_help for more info
    https://gist.github.com/InterStella0/b78488fb28cadf279dfd3164b9f0cf96
    """
    async def send_pages(self):
        """The default help command for this bot"""
        channel = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page)
            await channel.send(embed=embed)


class HelpCommandCog(commands.Cog):
    """ A custom cog for the bot's help command """
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        self.bot = bot
        bot.help_command = TOGHelpCommand()
        bot.help_command.cog = self
        
    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        inviter = await self.get_inviter_for_guild(guild)
        await inviter.send(
            'Hello! Thanks for inviting me! ' + \
            f'For more info on how to configure me, type {self.bot.command_prefix}help'
        )

    async def get_inviter_for_guild(self, guild):
        """Gets the user that invited the bot to join this guild"""
        def was_tog_helper_invite(event):
            return event.target.id == self.bot.user.id
        bot_entry = await guild.audit_logs(
            action=discord.AuditLogAction.bot_add
        ).find(was_tog_helper_invite)
        return bot_entry.user