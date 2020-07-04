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
#   time

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
import time

import botSupportFuncs as bsf
from botSupportFuncs import Table, CheckNameError, command_react

# ––– read args with argparse & create global vars —––

parser = argparse.ArgumentParser(description='managebot can connect only to one server')
parser.add_argument('-t', '--token', type=str, required=False, help='Token to connect to a Bot')
parser.add_argument('-p', '--path-config', type=str, required=False, help='JSON config path')
parser.add_argument('-T', '--test-mode', action='store_true', required=False, help='Test mode')
args = parser.parse_args()

if args.token is None:
    parser.print_help()
    exit()

TOKEN                   = args.token # read token to connect to a discord bot

PATH                    = os.getcwd()
PATH_CONFIG             = os.path.join(PATH, 'rsc/bot.cfg.json' if args.path_config is None else args.path_config)
PATH_SQL                = bsf.get_PATHS(PATH_CONFIG)
PATH_TMP                = os.path.join(PATH, 'tmp/')
PATH_UPLOAD             = os.path.join(PATH, 'tmp/uploads/')

ROLE_ADUSER             = bsf.get_ROLES(PATH_CONFIG)

NAME_DISCORD            : str
GUILD                   : discord.Guild

# ––– create bot –––

bot = commands.Bot(command_prefix='-') # changed from '.' to '-'

# ––– bot events –––

# ready event
@bot.event
async def on_ready():
    global GUILD, NAME_DISCORD
    print("\033[32mBot is ready, connecting...\033[0m")
    if bot.guilds is not None:
        GUILD = bot.guilds[0]
        NAME_DISCORD = bot.user.display_name
        print(f'Bot has connected to {GUILD.name}; id: {GUILD.id}')
        await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':globe_with_meridians: Hi, I\'m online...')
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
            await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':octagonal_sign: An error occurred while sending a message to {str(member.mention)}: {str(e)}')

    else:
        # the client is a bot
        # insert into db
        with sqlite3.connect(PATH_SQL) as conn:
            cur = conn.cursor()

            cur.execute('INSERT INTO clan_members (id, name, name_discord, name_displayed, permanent_member, identification) VALUES (?, ?, ?, ?, ?, ?)', (member.id, '~bot', str(member), member.display_name, 1, 1))
            cur.execute('INSERT INTO clan_member_statistics (id) VALUES (?)', (member.id,))

            conn.commit()
        await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':arrow_right: Bot {str(member.mention)} joined the server...')

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
# TODO: create statistics funktions
@bot.event
async def on_voice_state_update(member, before, after):
    pass


# ––– bot commands –––

# –– dm commands ––

# – identification –

@bot.command('identify')
@commands.dm_only()
async def identify(ctx, clan_member, name: typing.Optional[str] = "", name_wot: typing.Optional[str] = ""):
    await command_react(ctx)
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

            await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':white_check_mark: {str(ctx.author.mention)} identified himself/herself successfully, but he/she doesn\'t want be clan member...')
            await ctx.send(bsf.get_JSON(PATH_CONFIG)["D_MESSAGES"]["no clan member identification"])
    else:
        # user want be a clan member
        with sqlite3.connect(PATH_SQL) as conn:
            cur = conn.cursor()
            try:
                cur.execute('UPDATE clan_members SET identification=1, name=?, name_wot=? WHERE id=?', (name if not name.lower() == 'none' else None, bsf.check_str(name_wot, minlen=2), ctx.author.id))

                await GUILD.get_member(ctx.author.id).add_roles(discord.utils.get(GUILD.roles, name='clan members'))
                await ctx.send(bsf.get_JSON(PATH_CONFIG)["D_MESSAGES"]["successful identification"])
                await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':white_check_mark: {str(ctx.author.mention)} identified himself/herself successfully...')
            except Exception as e:
                await ctx.send(bsf.get_JSON(PATH_CONFIG)["D_MESSAGES"]["error message"])
                await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':octagonal_sign: An error occurred while {str(ctx.author.mention)} was identifying himself/herself: {str(e)}')

            conn.commit()

# – update meber data –

# TODO: Complete function
@bot.command('update-my-data')
@commands.dm_only()
async def update_member_data(ctx, clan_member, name: typing.Optional[str] = "", name_wot: typing.Optional[str] = ""):
    await command_react(ctx)
    with sqlite3.connect(PATH_SQL) as conn:
        cur = conn.cursor()

        cur.execute('SELECT identification FROM clan_member WHERE id=?', (ctx.author.id,))
        r = cur.fetchall()[0][0]
        conn.commit()
    if r == 0:
        return

# –– guild commands ––

# – standart funktions –

# log out bot
@bot.command(name='shutdown')
@commands.guild_only()
@commands.has_guild_permissions(administrator=True)
async def clear(ctx, arg: typing.Optional[str] = ""):
    await command_react(ctx)
    await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f":zzz: Bye, I will go offline in 5 sec...")
    time.sleep(5)
    await bot.logout()


# delete [limit] messages in a channel
@bot.command(name='clear')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def clear(ctx, limit: typing.Optional[int] = 10):
    await command_react(ctx)
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
    await command_react(ctx)
    for file in files:
        try:
            await ctx.send(f':white_check_mark: {file} ready to download... ', file=bsf.get_FILE(os.path.join(PATH, file)))
        except Exception as e:
            await ctx.send(f':octagonal_sign: {file} something goes wrong: {str(e)}')


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
    await command_react(ctx)
    os.removedirs(PATH_TMP)
    os.mkdir(PATH_TMP)
    os.mkdir(PATH_UPLOAD)

# – sql functions –

# sql function with sql statements as args
@bot.command(name='sql')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def sql(ctx, *args):
    await command_react(ctx)
    for arg in args:

        r = bsf.sql(arg, PATH_SQL)
        if r == None:
            await ctx.send(':white_check_mark: The command was executed successfully...', delete_after=300.0)
        elif type(r) == Table:
            with open(os.path.join(PATH_TMP, 'sql-request.dbr'), 'w') as file:
                file.write(r.table)
            await ctx.send(':white_check_mark: The command was executed successfully...', file=discord.File(os.path.join(PATH_TMP, 'sql-request.dbr')), delete_after=300.0)

        elif type(r) == Exception:
            await ctx.send(f':octagonal_sign: By executing the command something goes wrong\n>{r}', delete_after=300.0)

        await ctx.message.delete(delay=300.0)

    await ctx.message.delete(delay=300.0)

# sql function with normal args
@bot.command(name='table')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def table(ctx, rows, table, where: typing.Optional[str] = "", args: typing.Optional[str] = ""):
    await command_react(ctx)
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

# – write funktions –

# function to write a message to a channel
@bot.command(name='write-channel')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def write_channel(ctx, channels: commands.Greedy[discord.TextChannel], message):
    await command_react(ctx)
    fast_messages: dict = bsf.get_JSON(PATH_CONFIG)["FAST_MESSAGES"]
    channels_send = ''

    if message in list(fast_messages.keys()):
        try:
            message_to_write: str = fast_messages[message]
        except Exception as e:
            await ctx.send(f':octagonal_sign: something goes wrong... \n{e}', delete_after=300.0)
            return
    else:
        message_to_write: str = message

    for textChannel in channels:
        try:
            await textChannel.send(message_to_write)
            channels_send += str(textChannel.name) + ', '
        except Exception as e:
            pass

    await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':white_check_mark: Your message was send to {channels_send}')

# function to write a dm message to all members in a role
@bot.command(name='write-role')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def write_role(ctx, role: commands.Greedy[discord.Role], message):
    await command_react(ctx)
    fast_messages: dict = bsf.get_JSON(PATH_CONFIG)["FAST_MESSAGES"]
    members_send = ''

    if message in list(fast_messages.keys()):
        try:
            message_to_write: str = fast_messages[message]
        except Exception as e:
            await ctx.send(f':octagonal_sign: something goes wrong... \n{e}', delete_after=300.0)
            return
    else:
        message_to_write: str = message

    for member in role[0].members:
        try:
            await member.send(message_to_write)
            members_send += str(member.mention) + ', '
        except Exception as e:
            pass

    await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':white_check_mark: Your message was send to {members_send}')

# function to write a dm message to all members in a role and a message to channel
@bot.command(name='write-server')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def write_server(ctx, role: commands.Greedy[discord.Role], channel: commands.Greedy[discord.TextChannel], message, message_to_channel: typing.Optional[str] = ''):
    await command_react(ctx)
    if message_to_channel == '':
        await write_role(ctx, role, message)
        await write_channel(ctx, channel, message)
    else:
        await write_role(ctx, role, message)
        await write_channel(ctx, channel, message_to_channel)

# – fix –

@bot.command(name='fix')
@commands.guild_only()
@commands.has_role(ROLE_ADUSER)
async def fix(ctx, *args):
    await command_react(ctx)
    for arg in args:


        if arg == 'db-rows':
            with sqlite3.connect(PATH_SQL) as conn:
                cur = conn.cursor()
                no_registered_members = ''
                for member in GUILD.members:
                    cur.execute('SELECT identification FROM clan_members WHERE id=?;', (member.id,))
                    r = cur.fetchall()

                    if r == []:
                        no_registered_members += str(member.mention) + ', '
                        await on_member_join(member)

                if no_registered_members == '':
                    await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':white_check_mark: All members of the server are registered')
                else:
                    await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':warning: These were not registered: {no_registered_members}')

                cur.execute('SELECT id, name, name_displayed FROM clan_members')
                r = cur.fetchall()
                for row in r:
                    if GUILD.get_member(row[0]) is None:
                        cur.execute('DELETE FROM clan_members WHERE id=?;', (row[0],))
                        cur.execute('DELETE FROM clan_member_statistics WHERE id=?;', (row[0],))
                    elif str(GUILD.get_member(row[0])) != row[1] or GUILD.get_member(row[0]).display_name != row[2]:
                        cur.execute('UPDATE clan_members SET name_discord=?, name_displayed=? WHERE id=?;', (str(GUILD.get_member(row[0])), str(GUILD.get_member(row[0]).display_name), row[0]))
                conn.commit()


        elif arg == 'db-old':
            with sqlite3.connect(os.path.join(PATH, bsf.get_JSON(PATH_CONFIG)["OLD_DB"]["PATH"])) as conn:
                cur = conn.cursor()

                cur.execute('SELECT id, name, name_discord, name_displayed, name_wot, identification FROM clan_members')

                r = cur.fetchall()

                conn.commit()

            with sqlite3.connect(PATH_SQL) as conn:
                cur = conn.cursor()
                for row in r:
                    if row[5] and row[4] == None:
                        identification = 2

                    elif row[5]:
                        identification = 1

                    elif not row[5]:
                        identification = 0

                    try:
                        cur.execute('INSERT OR IGNORE INTO clan_members (id, name, name_discord, name_displayed, name_wot, identification) VALUES (?, ?, ?, ?, ?, ?)', (row[0], row[1], str(GUILD.get_member(int(row[0]))), row[3], row[4], identification))
                        cur.execute('INSERT OR IGNORE INTO clan_member_statistics (id) VALUES (?)', (row[0],))
                        await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':information_source: {GUILD.get_member(int(row[0])).mention} was inserted into {PATH_SQL} from {bsf.get_JSON(PATH_CONFIG)["OLD_DB"]["PATH"]}')
                    except Exception as e:
                        await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':octagonal_sign: An error occurred while inserting {GUILD.get_member(int(row[0])).mention} into {PATH_SQL} from {bsf.get_JSON(PATH_CONFIG)["OLD_DB"]["PATH"]}: {str(e)}')

                conn.commit()

        elif arg == 'db-identify':

            with sqlite3.connect(PATH_SQL) as conn:
                cur = conn.cursor()
                no_registered_members = ''
                for member in GUILD.members:
                    cur.execute('SELECT identification FROM clan_members WHERE id=?;', (member.id,))
                    r = cur.fetchall()

                    if r[0][0] == 0:
                        no_registered_members += str(member) + ', '
                        await on_member_join(member)

                if no_registered_members == '':
                    await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':white_check_mark: All members of the server are registered')
                else:
                    await bot.get_channel(bsf.get_JSON(PATH_CONFIG)["COMMAND_PROMPT_ID"]).send(f':warning: These are not identified: {no_registered_members}')

        elif arg == 'path-config':
            pass


# ––  start bot with token ––

bot.run(TOKEN)
