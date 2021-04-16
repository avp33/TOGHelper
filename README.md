# TOGHelper

A discord bot originally built for The Other Guys using discord.py. Now it can be used by any guild that wants to use it.

Note that the convention of referring to "Guilds" in code is really referring to Discord servers. This is for consistency with discord.py / the discord api.

## Adding the bot to your server
[Go to this URL](https://discord.com/api/oauth2/authorize?client_id=822262145412628521&permissions=199808&scope=bot) to authorize the bot on your server. The permissions that are selected here are all used by the bot, so please leave them checked to make sure everything works as expected.

## Gear checking
The gear checking feature currently works such that when somebody sends a sixtyupgrades (or wowhead gear planner) link to a channel of the form:
mc-gear-check, bwl-gear-check, naxx-gear-check, or aq40-gear-check
A link to this message as well as the user's logs will be forwarded to a different server and channel (once configured):

![image](https://user-images.githubusercontent.com/5596048/114349371-a8e68000-9b1c-11eb-9c15-8a1276ab20cc.png)


Gear checking will tell users to use sixtyupgrades if they use wowhead instead, as sixtyupgrades was TOG's preferred gear checker. It will also tell the user if they posted a sixtyupgrades link that was private.

## Configuring gear checking
To enable gear checking on your server, you will want to be sure that TOG Helper has been added to both the server that will be receiving gear check requests and the server that will have the messages forwarded to it.

Once that is done, go to the channel in the server that you want messages forwarded to, and use the tog.setup_gear_check command.

An example of using this command is 'tog.setup_gear_check 806389180162506802 Faerlina', where the first argument is the id of the server that will be receiving gear check requests, and the second is the name of your server (NA is the only supported region currently).

To get the id of your server, follow [these steps](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID).

After that command is run, if you no longer want to receive forwarded messages, you can run 'tog.remove_gear_check 806389180162506802', where the only argument is the id of the server that you want to stop receiving messages from.

## Buff alerts
Buff alerting currently allows you to have messages that notify @everyone or @here in another server to be forwarded to your own server.

![image](https://user-images.githubusercontent.com/5596048/114350177-b6503a00-9b1d-11eb-838d-6d5a63ccea87.png)


## Configuring buff alerts
To enable buff alerts on your server, you will want to be sure that TOG Helper has been added to both the server that players are posting alerts to as well as the server that will have the messages forwarded to it.

Once that is done, go to the channel in the server that you want messages forward to, and use the tog.setup_buff_alerts comand.

An example of using this command is 'tog.setup_buff_alerts 795575592501379073 832414160410640454'. The first number is the id of the channel on another server that you want to receive buff alerts from. The second number is optional, but if you only want a specific role to be notified of buff alerts (rather than @here), you can use this so only they receive a notification.

To get the id of a channel, follow [these steps](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID).

If you set a role to receive buffs, users can opt into notifications by using tog.buff_me and opt out by using tog.debuff_me

After that command is run, if you no longer want to receive forwarded messages, you can run 'tog.remove_buff_alerts 795575592501379073 832414160410640454', where the first argument is the id of the channel that you want to stop receiving messages from.



## Need more help with commands?
Use tog.help in your discord server or in a DM to the TOG Helper bot to find out more about the different commands
