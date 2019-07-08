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
    print(
        f"Add bot to server: https://discordapp.com/oauth2/authorize/?permissions=16&scope=bot&client_id={bot.user.id}"
    )


@bot.event
async def on_guild_join(guild):
    category = await guild.create_category("Hunt The Wumpus")
    lobby = await category.create_text_channel(
        "lobby",
        overwrites={bot.user: discord.PermissionOverwrite(manage_messages=True)},
    )

    message = await lobby.send(
        """To start a game of Hunt The Wumpus, type `htw!play` in `hunting-general`.
Type `htw!forfeit` in your game channel to end the game early.
Happy hunting!"""
    )
    await message.pin()


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
    category = discord.utils.find(
        lambda c: c.name == "Hunt The Wumpus", ctx.guild.categories
    )
    lobby = discord.utils.find(lambda c: c.name == "lobby", category.text_channels)
    return ctx.message.channel.id == lobby.id


@bot.command(help="Creates a hunt. Only usable withing the hunting general channel.")
@commands.check(is_lobby_channel)
async def play(ctx):
    category = discord.utils.find(
        lambda c: c.name == "Hunt The Wumpus", ctx.guild.categories
    )
    channel = await category.create_text_channel(
        ctx.message.author.name,
        overwrites={
            ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False),
            ctx.message.author: discord.PermissionOverwrite(send_messages=True),
            ctx.bot.user: discord.PermissionOverwrite(send_messages=True),
        },
    )

    game = wumpus.Game()
    msg, state = game.start()
    games[channel.id] = state
    await channel.send(msg)


async def process_input(channel, input):
    msg, games[channel.id] = games[channel.id](input)
    if games[channel.id] is None:
        await end_game(channel)
    else:
        await channel.send(msg)


async def end_game(channel):
    del games[channel.id]
    await channel.delete()


bot.run(config.token)
