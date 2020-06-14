#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Code created by Felix Wochnick (2020)
# felixwochnick@gmx.de

# This Discord Bot is a Bot to interact with the members of a server.

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
from botSupportFuncs import Table, CheckNameError

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

bot = commands.Bot(command_prefix='-')

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

# join event
@bot.event
async def on_member_join(member: discord.Member):
    if not member.bot:
        # insert into db
        with sqlite3.connect(PATH_SQL) as conn:
            cur = conn.cursor()

            cur.execute('INSERT INTO clan_members (id, name_discord, name_displayed) VALUES (?, ?, ?)', (member.id, str(member), member.display_name))
            cur.execute('INSERT INTO clan_member_statistics (id) VALUES (?)', (member.id,))

            conn.commit()

        await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':arrow_right: {str(member.mention)} joined the server...')
        try:
            await member.send(bsf.get_JSON(PATH_CONFIG)["D_MESSAGES"]["welcome message"].format(member.name))
        except Exception as e:
            await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':error: An error occurred while sending a message to {str(member.mention)}: {str(e)}')

    else:
        # the client is a bot
        # insert into db
        with sqlite3.connect(PATH_SQL) as conn:
            cur = conn.cursor()

            cur.execute('INSERT INTO clan_members (id, name, name_discord, name_displayed, permanent_member, identification) VALUES (?, ?, ?, ?, ?)', (member.id, '~bot', str(member), member.display_name, 1, 1))
            cur.execute('INSERT INTO clan_member_statistics (id) VALUES (?)', (member.id,))

            conn.commit()
        await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':arrow_right: Bot {str(member.mention)} joined the server...')

# –– bot commands ––

# – identification –

@bot.command('identify')
@commands.dm_only()
async def identify(ctx, clan_member, name: typing.Optional[str] = "", name_wot: typing.Optional[str] = ""):
    with sqlite3.connect(PATH_SQL) as conn:
        cur = conn.cursor()

        cur.execute('SELECT identification FROM clan_members WHERE id=?', (ctx.author.id,))
        r = cur.fetchall()[0][0]
        conn.commit()
    if not r == 0:
        return
    if not bsf.str_to_bool(clan_member):
        # user don't want be clan member
        with sqlite3.connect(PATH_SQL) as conn:
            cur = conn.cursor()

            cur.execute('UPDATE clan_members SET identification=2 WHERE id=?', (ctx.author.id,))

            conn.commit()
    else:
        # user want be a clan member
        with sqlite3.connect(PATH_SQL) as conn:
            cur = conn.cursor()
            try:
                cur.execute('UPDATE clan_members SET identification=1, name=?, name_wot=? WHERE id=?', (name if not name.lower() == 'none' else None, bsf.check_str(name_wot, minlen=2), ctx.author.id))
                await ctx.send(bsf.get_JSON(PATH_CONFIG)["D_MESSAGES"]["successful identification"])
                await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':white_check_mark: {str(ctx.author.mention)} identified himself/herself successfully...')
            except Exception as e:
                await ctx.send(bsf.get_JSON(PATH_CONFIG)["D_MESSAGES"]["error message"])
                await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':error: An error occurred while {str(ctx.author.mention)} was identifying himself/herself: {str(e)}')

            conn.commit()

# – update –

@bot.command('update-my-data')
@commands.dm_only()
async def update_member_data(ctx, clan_member, name: typing.Optional[str] = "", name_wot: typing.Optional[str] = ""):
    with sqlite3.connect(PATH_SQL) as conn:
        cur = conn.cursor()

        cur.execute('SELECT identification FROM clan_member WHERE id=?', (ctx.author.id,))
        r = cur.fetchall()[0][0]
        conn.commit()
    if r == 0:
        return

# –– COMMAND BRIDGE commands ––

# – write-role –

@bot.command(name='write-role')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def write_role(ctx, message, role: commands.Greedy[discord.Role]):
    members_send = ''

    for member in role[0].members:
        try:
            await member.send(message_to_write)
            members_send += str(member.mention) + ', '
        except Exception as e:
            pass

    await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':white_check_mark: Your message was send to {members_send}'.replace(', ', '.'), delete_after=300.0)

@bot.command(name='insert-members')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def insert_member(ctx, *member_ids):
    for member_id in member_ids:
        await on_member_join(GUILD.get_member(int(member_id)))


# ––  start bot with token ––

bot.run(TOKEN)
