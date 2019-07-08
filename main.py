#!/usr/bin/env python3

import asyncio
import os
import json
import discord
import wumpus
from discord.ext import commands
from collections import namedtuple
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", default="config.json")
args = parser.parse_args()

Config = namedtuple("Config", ["token", "prefix"], defaults=["htw!"])
with open(args.config) as f:
    config = json.load(f, object_hook=lambda obj: Config(**obj))

Client = discord.Client()

bot = commands.Bot(command_prefix=config.prefix)

guild_dict = {}
games = {}


@bot.event
async def on_ready():
    print("Bot online.")
    print(f"ID: {bot.user.id}")
    print(f"Version: {discord.__version__}")


@bot.event
async def on_guild_join(guild):
    category = await guild.create_category("Hunt The Wumpus")
    lobby = await category.create_text_channel("lobby")

    message = await lobby.send(
        """To start a game of Hunt The Wumpus, type `htw!play` in `hunting-general`.
Type `htw!forfeit` in your game channel to end the game early.
Happy hunting!"""
    )
    await message.pin()

    data = {"guild_id": guild.id, "category_id": category.id, "lobby_id": lobby.id}

    with open(str(guild.id) + ".json", "w") as write_file:
        json.dump(data, write_file)


@bot.event
async def on_message(msg):
    await bot.process_commands(msg)
    if msg.channel.id in games and not msg.author.bot:
        await process_input(msg.channel, msg.content)


async def is_game_channel(ctx):
    return ctx.message.channel.id in games


@bot.command(help="Ends a hunt immediately. Only usable within a hunt channel.")
@commands.check(is_game_channel)
async def forfeit(ctx):
    await end_game(ctx.message.channel)


async def is_lobby_channel(ctx):
    with open(str(ctx.guild.id) + ".json") as read_file:
        print("Opened file")
        data = json.load(read_file)
    return ctx.message.channel.id == int(data["lobby_id"])


@bot.command(help="Creates a hunt. Only usable withing the hunting general channel.")
@commands.check(is_lobby_channel)
async def play(ctx):
    with open(str(ctx.guild.id) + ".json") as read_file:
        data = json.load(read_file)

    channel = await ctx.guild.create_text_channel(
        ctx.message.author.name + "'s Hunt",
        category=bot.get_channel(data["category_id"]),
    )
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)

    game = wumpus.Game()
    state = game.start()
    games[channel.id] = [game, state[1]]

    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = True
    await channel.set_permissions(ctx.message.author, overwrite=overwrite)
    await channel.set_permissions(bot.user, overwrite=overwrite)

    await channel.send(state[0])
    return data


async def process_input(channel, input):
    state = games[channel.id][1](input)
    if state[1] is None:
        await end_game(channel)
    else:
        games[channel.id][1] = state[1]
        await channel.send(state[0])


async def end_game(channel):
    del games[channel.id]
    await channel.delete()


bot.run(config.token)
