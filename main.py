#!/usr/bin/env python3
import asyncio
import os
import json
import discord
import wumpus
from discord.ext import commands

Client = discord.Client()

bot_prefix = "htw!"
token = "YOUR TOKEN HERE"

bot = commands.Bot(command_prefix=bot_prefix)

guild_dict = {}
games = {}


@bot.event
async def on_ready():
    print("Bot online.")
    print(f"ID: {bot.user.id}")
    print(f"Version: {discord.__version__}")


@bot.event
async def on_guild_join(guild):
    HTW_cat = await guild.create_category("Hunt the Wumpus")

    channel = await guild.create_text_channel("Hunting General", category=HTW_cat)

    msg = await channel.send(
        """To start a game of Hunt The Wumpus, type `htw!play` in `hunting-general`.
Type `htw!forfeit` in your game channel to end the game early.
Happy hunting!"""
    )
    await msg.pin()

    data = {"guild_id": guild.id, "category_id": HTW_cat.id, "command_id": channel.id}

    with open(str(guild.id) + ".json", "w") as write_file:
        json.dump(data, write_file)


@bot.event
async def on_message(message):
    with open(str(message.guild.id) + ".json", "r") as read_file:
        print("Opened file")
        data = json.load(read_file)

        print("Checking for command")
        if message.channel.id == int(data["command_id"]):
            print("Found command")
            await bot.process_commands(message)

        elif message.channel.id in games and not message.author.bot:
            if message.content == "htw!forfeit":
                await end_game(message.channel)
            else:
                print("Checking otherwise")
                await process_input(message.channel, message.content)

        else:
            print(message.channel.id)
            print(data["command_id"])


@bot.command(
    pass_context=True,
    help="Ends a hunt immediately. Only usable within a hunt channel.",
)
async def forfeit(ctx):
    pass


@bot.command(
    pass_context=True,
    help="Creates a hunt. Only usable withing the hunting general channel.",
)
async def play(ctx):
    with open(str(ctx.guild.id) + ".json", "r") as read_file:
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


bot.run(token)
