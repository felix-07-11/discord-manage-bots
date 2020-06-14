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

- SQL db (if you don't edit code):
  - tables 
  ```sql
  clan_members (id INTEGER PRIMARY KEY UNIQUE NOT NULL, name TEXT, name_discord TEXT, name_displayed TEXT, name_wot TEXT, identification   INTEGER DEFAULT 0)
  clan_member_statistics (id INTEGER PRIMARY KEY UNIQUE NOT NULL, active_days INTEGER, missed_extra_invitations INTEGER, last_active_date TEXT, number_of_warnings INTEGER)
  ```
  

## manageBot.py

### commands

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
  
__table__ rows: [str], table: [str], args: optional[str] = ""  
  _create a sqlstatemant and run sql()_  
  _"SELECT [rows] FROM [table] WHERE [args]"_  

## userInteraktionBot.py
