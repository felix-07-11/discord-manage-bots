# discord-manage-bots
Discord bots to manage the members of the servers
there are bots to manage a World of Tanks Clan Server, if you don't edit the sourcecode.

## requierements
- Python libaries:
  - argparse
  - discord
  - sqlite3
  - tabulate
  - time
  - asyncio
  - json
  - os
  - typing

- Files:
  - SQL db with tables (default):
  ```sql
  clan_members (id INTEGER PRIMARY KEY UNIQUE NOT NULL, name TEXT, name_discord TEXT, name_displayed TEXT, name_wot TEXT, identification   INTEGER DEFAULT 0)
  clan_member_statistics (id INTEGER PRIMARY KEY UNIQUE NOT NULL, active_days INTEGER DEFAULT 0, missed_extra_invitations INTEGER DEFAULT 0, last_active_date TEXT DEFAULT '', number_of_warnings INTEGER DEFAULT 0)
  ```
  - Config File: format = json, default path = ./rsc/bot.cfg
 
- Discord channels
  - Command-Bridge: a textchannel on which only the bots have permissions to exchange informations or commands.

## manageBot.py

### start
```sh
$ python3 manageBot.py -t TOKEN
$ ./manageBot.py -t TOKEN
```
with config path:
```sh
$ python3 manageBot.py -t TOKEN -p PATH-CONFIG
$ ./manageBot.py -t TOKEN -p PATH-CONFIG
```
### events

  - [x] on_ready  
  - [ ] on_member_update  
  
### commands
  
  - [x] clear  
  - [ ] upload  
  - [x] download  
  - [ ] update  
  - [x] clear cache  
  - [x] sql  
  - [x] table  
  - [ ] show  
  - [x] write-role  

_Prefix_: '.'  

__clear__ x: optional[int] = 10  
  _delete x messages in a channel_  

__download__ \*files: List[str]  
  _@files: paths of files_  
  _upload files to downloads_  

__clear-cache__  
  _clear ./tmp/_  

__sql__ \*args: List[str]  
  _@args: sqlstatements_  
  _execute every sqlstatement in args_  
  
__table__ rows: [str], table: [str], where: optional[str] = "", args: optional[str] = ""  
  _create a sqlstatemant and run sql()_  
  _"SELECT [rows] FROM [table] WHERE clan_member_statistics.id = clan_members.id and ([where]) [args]"_  
  
__write-role__ message: [str], role: [discord.Role]  
  _command send on to a other bot via commad-bridge_  
  _write [message] to all members of the [role]_  
  _you can also define fast messages in the config-file_  

## userInteraktionBot.py

### start
```sh
$ python3 userInteractionBot.py -t TOKEN
$ ./userInteractionBot.py -t TOKEN
```
with config path:
```sh
$ python3 userInteractionBot.py -t TOKEN -p PATH-CONFIG
$ ./userInteractionBot.py -t TOKEN -p PATH-CONFIG
```
### commands

  - [x] identify  
  - [ ] update-my-data  

_Prefix_: '.'  

_dm only_  
__identify__ clan_member: [str -> bool], name: optional[str] = "", name_wot. optional[str] = ""  
  _complete db with [name] and [name_wot] if clan_member is True_
  
__update-my-data__ clan_member: [str -> bool], name: optional[str] = "", name_wot. optional[str] = ""  
  _complete db with [name] and [name_wot] if clan_member is True_  
  _delete [name] and [name_wot] in db if clan_member is False_
