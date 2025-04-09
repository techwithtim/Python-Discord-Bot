import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random

# Load environment variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Set up logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration
secret_role = "Gamer"

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # FIXED: The word filter logic was flawed - it would block ANY message containing "shit"
    # even as part of another word (like "shirt"). Now it checks for whole words only
    # Also ensured command processing continues for non-filtered messages
    if any(f" {word} " in f" {message.content.lower()} " for word in ["shit"]):
        await message.delete()
        await message.channel.send(f"{message.author.mention} - dont use that word!")
        return  # FIXED: Added return here to prevent processing commands in filtered messages
    
    # FIXED: This line was not being reached for non-filtered messages due to indentation
    # which means bot commands were broken completely
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def assign(ctx):
    # FIXED: Added error handling for when the bot doesn't have permissions
    try:
        role = discord.utils.get(ctx.guild.roles, name=secret_role)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}")
        else:
            await ctx.send("Role doesn't exist")
    except discord.Forbidden:
        await ctx.send("I don't have permission to assign roles!")

@bot.command()
async def remove(ctx):
    # FIXED: Added error handling for when the bot doesn't have permissions
    try:
        role = discord.utils.get(ctx.guild.roles, name=secret_role)
        if role:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author.mention} has had the {secret_role} removed")
        else:
            await ctx.send("Role doesn't exist")
    except discord.Forbidden:
        await ctx.send("I don't have permission to remove roles!")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")

@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message!")

@bot.command()
async def poll(ctx, *, question):
    # FIXED: Added error handling for when there's no question
    if not question.strip():
        await ctx.send("Please provide a question for the poll!")
        return
        
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send("Welcome to the club!")

@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")

# Added a simple help command that shows available commands
@bot.command()
async def helpme(ctx):
    commands_list = [
        "**!hello** - Say hello to the bot",
        "**!assign** - Get the Gamer role",
        "**!remove** - Remove the Gamer role",
        "**!dm [message]** - Send yourself a DM",
        "**!reply** - Get a reply to your message",
        "**!poll [question]** - Create a yes/no poll",
        "**!helpme** - Show this help message"
    ]
    
    embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
    embed.description = "\n".join(commands_list)
    await ctx.send(embed=embed)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
