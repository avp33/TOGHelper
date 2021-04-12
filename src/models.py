"""Module for data models used by the bot"""

class GearCheckConfigurationInfo(object):
    """ 
    Contains properties necessary to define which guild has
    gear check messages being posted to it, and which guild/channel should
    be having these messages forwarded (with additional character info)
    """ 
    def __init__(self, 
                 source_guild_id: int, 
                 destination_guild_id: int, 
                 destination_channel_id: int, 
                 realm: str):
        self.source_guild_id = source_guild_id
        self.destination_guild_id = guild_id
        self.destination_channel_id = gear_check_channel_id
        self.realm = realm


class BuffAlertConfigurationInfo(object):
    """
    Contains properties necessary define which channel has buff messages
    being posted to it, and which guild/channel should be having 
    these messages forwarded
    """

    def __init__(self, 
                 source_channel_id: int, 
                 destination_guild_id: int, 
                 destination_channel_id: int):
        self.source_channel_id = source_channel_id
        self.destination_guild_id = destination_guild_id
        self.destination_channel_id = destination_channel_id


class DestinationGuildConfiguration(object):
    """
    This class contains information about a guild (server) and the other guilds
    that it is listening to.

    A destination guild receives forwarded messages for gear check and buff alerts
    """

    def __init__(self,
                 guild_id: int,
                 buff_alert_infos: list[BuffAlertConfigurationInfo], 
                 gear_check_infos: list[GearCheckConfigurationInfo]
    ):
        self.guild_id = guild_id
        self.buff_alert_infos = buff_alert_infos
        self.gear_check_infos = gear_check_infos

    def add_buff_alert_source(self, 
                              source_channel_id: int,
                              destination_channel_id: int):
        self.buff_alert_infos.append(BuffAlertConfigurationInfo(
            source_channel_id, self.guild_id, destination_channel_id))

    def add_gear_check_source(self, 
                              source_guild_id: int, 
                              destination_channel_id: int, 
                              realm: str):
        self.gear_check_infos.append(
            GearCheckConfigurationInfo(
                source_guild_id, self.guild_id, destination_channel_id, realm
            )
        )

    def remove_buff_alert_source(self, source_channel_id: int):
        self.buff_alert_infos = filter(
            lambda info: info.source_channel_id != source_channel_ids,
            self.buff_alert_infos
        )

    def remove_gear_check_source(self, source_guild_id: int):
        self.gear_check_infos = filter(
            lambda info: info.source_guild_id != source_guild_id,
            self.gear_check_infos
        )


class SourceGuildConfiguration(object):
    """
    This class contains information about a guild (server) and the other guilds
    that are listening to it.

    A source guild has mesages sent to it that are then forwarded to its destination guilds.
    """

    def __init__(self,
                 guild_id: int,
                 buff_alert_infos: list[BuffAlertConfigurationInfo], 
                 gear_check_infos: list[GearCheckConfigurationInfo]
    ):
        self.guild_id = guild_id
        self.buff_alert_infos = buff_alert_infos
        self.gear_check_infos = gear_check_infos

    def add_buff_alert_destination(self, 
                                   destination_guild_id: int, 
                                   destination_channel_id: int):
        self.buff_alert_infos.append(BuffAlertConfigurationInfo(
            self.guild_id, destination_guild_id, destination_channel_id))

    def add_gear_check_destination(self, 
                                   destination_guild_id: int, 
                                   destination_channel_id: int, 
                                   realm: str):
        self.gear_check_infos.append(
            GearCheckConfigurationInfo(
                self.guild_id, destination_guild_id, destination_channel_id, realm
            )
        )        

    def remove_buff_alert_destination(self, destination_guild_id: int):
        self.buff_alert_infos = filter(
            lambda info: info.destination_guild_id != destination_guild_id,
            self.buff_alert_infos
        )

    def remove_gear_check_destination(self, destination_guild_id: int):
        self.gear_check_infos = filter(
            lambda info: info.destination_guild_id != destination_guild_id,
            self.gear_check_infos
        )
