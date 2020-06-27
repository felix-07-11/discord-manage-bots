import json
import os
import sqlite3
from tabulate import tabulate
from discord import File

# classes
class Table():
    def __init__(self, table: str):
        self.table: str = table

# errror classes
class CheckNameError(Exception):
    pass

async def command_react(ctx, emoji='🆗'):
    for reaction in ctx.message.reactions:
        if reaction.emoji == emoji:
            return
    await ctx.message.add_reaction(emoji)

def get_PATHS(json_PATH):
    with open(json_PATH) as file:
        jsonDict = json.loads(file.read())
    return os.path.join(os.getcwd(), jsonDict["PATH_SQL"])

def get_JSON(json_PATH):
    with open(json_PATH) as file:
        return json.loads(file.read())

def get_FILE(path):
    if not os.path.exists(path):
        raise FileNotFoundError
    else:
        return File(path)

def get_ROLES(json_PATH):
    with open(json_PATH) as file:
        jsonDict = json.loads(file.read())
    return jsonDict["ROLE_ADUSER"]

def sql(statement: str, sql_path: str):
    with sqlite3.connect(sql_path) as conn:

        cur = conn.cursor()
        try:
            cur.execute(statement)
            sql = cur.fetchall()
            conn.commit()
            if sql != []:
                return Table(tabulate(sql, tablefmt='orgtbl'))
            else:
                return None

        except Exception as e:
            conn.commit()
            return e

def str_to_bool(string: str) -> bool:
    string = string.lower().replace(' ', '')

    if string == 'true':
        return True
    elif string == 'false':
        return False

def check_str(string: str, minlen=0, maxlen=None):
    if maxlen is not None:
        if not (len(string) >= minlen and len(string) <= maxlen):
            raise CheckNameError('Check failed')
    else:
        if not len(string) >= minlen:
            raise CheckNameError('Check failed')
    return string
