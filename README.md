# discord-manage-bots
Discord bots to manage the members of the servers.  
There are bots to manage a World of Tanks Clan Server, if you don't edit the sourcecode.

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
- [x] on_member_update  
- [x] on_user_update  
- [x] on_member_remove  
- [ ] on_voice_state_update  

### commands
  
- [x] clear  
- [ ] upload  
- [x] download  
- [ ] update  
- [x] clear cache  
- [x] sql  
- [x] table  
- [ ] show  
- [x] fix

_Prefix_: '.'  

> __clear__ x: optional[int] = 10  
> delete x messages in a channel  

> __download__ \*files: List[str]  
> @files: paths of files
> upload files to downloads  

> __clear-cache__  
> clear ./tmp/

> __sql__ \*args: List[str]  
> @args: sqlstatements
> execute every sqlstatement in args
  
> __table__ rows: [str], table: [str], where: optional[str] = "", args: optional[str] = ""  
> create a sqlstatemant and run sql()
> `SELECT [rows] FROM [table] WHERE clan_member_statistics.id = clan_members.id and ([where]) [args]`
  
> __fix__ \*args: List[str]  
> try to fix errors

> __write-role__ message: [str], role: [discord.Role]  
> command send on to a other bot via commad-bridge
> write [message] to all members of the [role]
> you can also define fast messages in the config-file

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

### events

- [x] on_ready  
- [x] on_member_join   
  
### commands

- [x] identify  
- [ ] update-my-data  
- [x] write-role
- [x] instert members  

_Prefix_: '-'  

> _dm only_  
> __identify__ clan_member: [str -> bool], name: optional[str] = "", name_wot. optional[str] = ""  
> complete db with [name] and [name_wot] if clan_member is True

> _dm only_  
> __update-my-data__ clan_member: [str -> bool], name: optional[str] = "", name_wot. optional[str] = ""  
> complete db with [name] and [name_wot] if clan_member is True
> delete [name] and [name_wot] in db if clan_member is False
