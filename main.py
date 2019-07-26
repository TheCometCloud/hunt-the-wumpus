from os import getenv

import discord
from discord.ext import commands

from wumpus import Game

bot = commands.Bot(command_prefix="htw!")

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
        """To start a game of Hunt The Wumpus, type `htw!play` in this channel.
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


@bot.command(help="End the game immediately.")
@commands.check(is_game_channel)
async def forfeit(ctx):
    await end_game(ctx.message.channel)


async def is_lobby_channel(ctx):
    category = discord.utils.find(
        lambda c: c.name == "Hunt The Wumpus", ctx.guild.categories
    )
    lobby = discord.utils.find(lambda c: c.name == "lobby", category.text_channels)
    return ctx.message.channel.id == lobby.id


@bot.command(help="Start a game.")
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

    game = Game()
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


bot.run(getenv("DISCORD_TOKEN"))
