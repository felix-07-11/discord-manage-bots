#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Code created by Felix Wochnick (2020)
# felixwochnick@gmx.de

# This Discord Bot is a Bot to manage and automate tasks on your server.

# Python3 libaries:
#   argparse
#   discord
#   sqlite3
#   tabulate
#   time
#   asyncio
#   json
#   os
#   typing

# –———————————— Code ————————————–

# —– import all Python libaries —–

import argparse
import discord
from discord.ext import commands
import sqlite3
from tabulate import tabulate
import time
import asyncio
import json
import os
import typing

import botSupportFuncs as bsf
from botSupportFuncs import Table

# –– read args with argparse & create main vars —–

parser = argparse.ArgumentParser(description='managebot can connect only to one server')
parser.add_argument('-t', '--token', type=str, required=False, help='Token to connect to a Bot')
parser.add_argument('-p', '--path-config', type=str, required=False, help='JSON config path')
args = parser.parse_args()

if args.token is None:
    parser.print_help()
    exit()

TOKEN                   = args.token # read token to connect to a discord bot

PATH                    = os.getcwd()
PATH_CONFIG             = os.path.join(PATH, 'rsc/bot.cfg' if args.path_config is None else args.path_config)
PATH_SQL                = bsf.get_PATHS(PATH_CONFIG)
PATH_TMP                = os.path.join(PATH, 'tmp/')
PATH_UPLOAD             = os.path.join(PATH, 'tmp/uploads/')

ROLE_ADUSER, ROLE_BOTS  = bsf.get_ROLES(PATH_CONFIG)

NAME_DISCORD            : str
GUILD                   : discord.Guild

# –– create bot ––

bot = commands.Bot(command_prefix='.')

# –– bot events ––

# ready event
@bot.event
async def on_ready():
    global GUILD, NAME_DISCORD
    print("\033[32mBot is ready, connecting...\033[0m")
    if bot.guilds is not None:
        GUILD = bot.guilds[0]
        NAME_DISCORD = bot.user.display_name
        print(f'Bot has connected to {GUILD.name}; id: {GUILD.id}')
    else:
        exit()

# on member update event: if member change his nickname
@bot.event
async def on_member_update(before, after):
    if before.display_name != after.display_name:
        with sqlite3.connect(PATH_SQL) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE clan_members SET name_displayed=? WHERE id=?', (after.display_name, after.id))
            conn.commit()
        await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':information_source: {str(after.mention)} has updated his/her nickname to {str(after.display_name)}')

@bot.event
async def on_user_update(before, after):
    if before.name != after.name or before.discriminator != after.discriminator:
        with sqlite3.connect(PATH_SQL) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE clan_members SET name=? WHERE id=?', (str(after), after.id))
            conn.commit()
        await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':information_source: {str(before)} has updated his/her profile to {str(after.mention)}')

@bot.event
async def on_member_remove(member):
    with sqlite3.connect(PATH_SQL) as conn:
        cur = conn.cursor()
        cur.execute('''
            DELETE FROM clan_members WHERE id=?;
        ''', (member.id,))
        cur.execute('''
            DELETE FROM clan_member_statistics WHERE id=?;
        ''', (member.id,))
        conn.commit()
    await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':arrow_left: {str(member)} left the server...')

# on voice state update event: if member join a voice chat
@bot.event
async def on_voice_state_update(member, before, after):
    pass


# –– bot commands ––

# – standart funktions –

# delete [limit] messages in a channel
@bot.command(name='clear')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def clear(ctx, limit: typing.Optional[int] = 10):
    await ctx.message.delete()
    await ctx.channel.purge(limit=limit)

# – file functions –

# upload file
# @bot.command(name='upload')
# @commands.guild_only()
# @commands.has_role(ROLE_ADUSER)
# async def upload(ctx):
#     pass

# download file
@bot.command(name='download')
@commands.guild_only()
async def download(ctx, *files):
    for file in files:
        try:
            await ctx.send(f':white_check_mark: {file} ready to download... ', file=bsf.get_FILE(os.path.join(PATH, file)))
        except Exception as e:
            await ctx.send(f':error: {file} something goes wrong: {str(e)}')


# update file
# @bot.command(name='update')
# @commands.guild_only()
# @commands.has_guild_permissions(administrator=True)
# async def update(ctx, file, to):
#     pass

# clear cache (tmp/)
@bot.command(name='clear-cache')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def clear_cache(ctx):
    os.removedirs(PATH_TMP)
    os.mkdir(PATH_TMP)
    os.mkdir(PATH_UPLOAD)

# – sql functions –

# sql function with sql statements as args
@bot.command(name='sql')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def sql(ctx, *args):
    for arg in args:

        r = bsf.sql(arg, PATH_SQL)
        if r == None:
            await ctx.send(':white_check_mark: The command was executed successfully...', delete_after=300.0)
        elif type(r) == Table:
            with open(os.path.join(PATH_TMP, 'sql-request.dbr'), 'w') as file:
                file.write(r.table)
            await ctx.send(':white_check_mark: The command was executed successfully...', file=discord.File(os.path.join(PATH_TMP, 'sql-request.dbr')), delete_after=300.0)

        elif type(r) == Exception:
            await ctx.send(f':error: By executing the command something goes wrong\n>{r}', delete_after=300.0)

        await ctx.message.delete(delay=300.0)

    await ctx.message.delete(delay=300.0)

# sql function with normal args
@bot.command(name='table')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def table(ctx, rows, table, where: typing.Optional[str] = "", args: typing.Optional[str] = ""):
    sql_statement = "SELECT {} FROM {} WHERE clan_member_statistics.id = clan_members.id {} {}".format(rows, table, 'and ( ' + where + ' )' if not where == "" else '', args)
    await sql(ctx, sql_statement)

# – show function –

# send a message with a table or a diagram
# @bot.command(name='show')
# @commands.guild_only()
# @commands.has_role(ROLE_ADUSER)
# async def show(ctx, info, *args):
#     if info == 'activity':
#         pass

# – write funktion –

# function to write a dm message to all members in a role
@bot.command(name='write-role')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def write_role(ctx, message, role: commands.Greedy[discord.Role]):
    with open(PATH_CONFIG) as file:
        fast_messages: dict = json.loads(file.read())["FAST_MESSAGES"]

    if message in list(fast_messages.keys()):
        try:
            message_to_write: str = fast_messages[message]
        except Exception as e:
            await ctx.send(f':error: something goes wrong... \n{e}', delete_after=300.0)
            return
    else:
        message_to_write: str = message

    await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_BRIDGE_ID"]).send(f'-write-role "{message_to_write}" "{role}"')
    await ctx.message.delete(delay=300.0)

# – fix –

@bot.command(name='fix')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def fix(ctx, *args):
    for arg in args:


        if arg == 'db-rows':
            with sqlite3.connect(PATH_SQL) as conn:
                cur = conn.cursor()
                no_registered_members = ''
                for member in GUILD.members:
                    cur.execute('SELECT identification FROM clan_members WHERE id=?;', (member.id,))
                    r = cur.fetchall()

                    if r == []:
                        no_registered_members += str(member) + ' ' + str(member.id) + ', '
                await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':warning: These are not registered: {no_registered_members}\ncommand to register: -insert-members *member_ids')

                cur.execute('SELECT id, name, name_displayed FROM clan_members')
                r = cur.fetchall()
                for row in r:
                    if GUILD.get_member(row[0]) is None:
                        cur.execute('DELETE FROM clan_members WHERE id=?;', (row[0],))
                        cur.execute('DELETE FROM clan_member_statistics WHERE id=?;', (row[0],))
                    elif GUILD.get_member(row[0]).name != row[1] or GUILD.get_member(row[0]).display_name != row[2]:
                        cur.execute('UPDATE clan_members SET name_discord=?, name_displayed=? WHERE id=?;', (str(GUILD.get_member(row[0]).name), str(GUILD.get_member(row[0]).display_name), row[0]))
                conn.commit()


        elif arg == 'path-config':
            pass


# ––  start bot with token ––

bot.run(TOKEN)
