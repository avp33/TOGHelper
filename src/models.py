"""Module for data models used by the bot"""
from utils import (
    convert_json_to_object, 
    JSONSerializable,
)

def convert_json_list_to_objects(json_list, cls: JSONSerializable.__class__):
    if len(json_list) == 0:
        return list()
    return [cls.from_json_dict(**json_dict) for json_dict in json_list]

class GearCheckConfigurationInfo(JSONSerializable):
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
        self.destination_guild_id = destination_guild_id
        self.destination_channel_id = destination_channel_id
        self.realm = realm

    @staticmethod 
    def from_json_dict(**kwargs):
        return GearCheckConfigurationInfo(**kwargs)    


class BuffAlertConfigurationInfo(JSONSerializable):
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

    @staticmethod
    def from_json_dict(**kwargs):
        return BuffAlertConfigurationInfo(**kwargs)      


class DirectionalGuildConfiguration(object):
    """
    This class contains information about a guild (server) and its relationship
    to other guilds that it may be a source/destination for.
    """

    def __init__(self,
                 guild_id: int,
                 buff_alert_infos: list[BuffAlertConfigurationInfo] = None, 
                 gear_check_infos: list[GearCheckConfigurationInfo] = None):
        self.guild_id = guild_id
        self.buff_alert_infos = buff_alert_infos or list()
        self.gear_check_infos = gear_check_infos or list()

    @staticmethod
    def from_json_dict(cls,
                       buff_alert_infos,
                       gear_check_infos,
                       **kwargs):
        return cls(
            buff_alert_infos=convert_json_list_to_objects(buff_alert_infos, BuffAlertConfigurationInfo),
            gear_check_infos=convert_json_list_to_objects(gear_check_infos, GearCheckConfigurationInfo),
            **kwargs
        )

class DestinationGuildConfiguration(DirectionalGuildConfiguration):
    """
    This class contains information about a guild (server) and the other guilds
    that it is listening to.

    A destination guild receives forwarded messages for gear check and buff alerts
    """
    def add_buff_alert_source(self, 
                              source_channel_id: int,
                              destination_channel_id: int):
        if len(list(filter(lambda info: info.source_channel_id == source_channel_id, 
                           self.buff_alert_infos))) > 0:
            return False
        self.buff_alert_infos.append(BuffAlertConfigurationInfo(
            source_channel_id, self.guild_id, destination_channel_id))
        return True

    def add_gear_check_source(self, 
                              source_guild_id: int, 
                              destination_channel_id: int, 
                              realm: str):
        if len(list(filter(lambda info: info.source_guild_id == source_guild_id, 
                           self.gear_check_infos))) > 0:
            return False
        self.gear_check_infos.append(
            GearCheckConfigurationInfo(
                source_guild_id, self.guild_id, destination_channel_id, realm
            )
        )
        return True

    def remove_buff_alert_source(self, source_channel_id: int):
        orig_num_infos = len(self.buff_alert_infos)
        self.buff_alert_infos = list(filter(
            lambda info: info.source_channel_id != source_channel_id,
            self.buff_alert_infos
        ))
        return len(self.buff_alert_infos) != orig_num_infos

    def remove_gear_check_source(self, source_guild_id: int): 
        orig_num_infos = len(self.gear_check_infos)
        self.gear_check_infos = list(filter(
            lambda info: info.source_guild_id != source_guild_id,
            self.gear_check_infos
        ))
        return len(self.gear_check_infos) != orig_num_infos


class SourceGuildConfiguration(DirectionalGuildConfiguration):
    """
    This class contains information about a guild (server) and the other guilds
    that are listening to it.

    A source guild has mesages sent to it that are then forwarded to its destination guilds.
    """

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
        self.buff_alert_infos = list(filter(
            lambda info: info.destination_guild_id != destination_guild_id,
            self.buff_alert_infos
        ))

    def remove_gear_check_destination(self, destination_guild_id: int):
        self.gear_check_infos = list(filter(
            lambda info: info.destination_guild_id != destination_guild_id,
            self.gear_check_infos
        ))


class GuildConfiguration(object):
    """
    This class contains both source and destination configuration
    information for a guild.
    """

    def __init__(self, 
                 guild_id: int,
                 destination_config: DestinationGuildConfiguration = None, 
                 source_config: SourceGuildConfiguration = None):
        self.guild_id = guild_id
        self.destination_config = destination_config or DestinationGuildConfiguration(guild_id)
        self.source_config = source_config or SourceGuildConfiguration(guild_id)

    @staticmethod
    def from_json_dict(destination_config,
                       source_config,
                       **kwargs):
        return GuildConfiguration(
            destination_config=DestinationGuildConfiguration.from_json_dict(DestinationGuildConfiguration, **destination_config),
            source_config=SourceGuildConfiguration.from_json_dict(SourceGuildConfiguration, **source_config),
            **kwargs
        )

def get_or_create_guild_config(redis_server, guild_id):
    guild_config = redis_server.get(guild_id)
    if guild_config is None:
        guild_config = GuildConfiguration(guild_id)
    else:
        guild_config = convert_json_to_object(guild_config.decode('utf-8'), GuildConfiguration)
    return guild_config    

