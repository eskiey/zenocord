import discord
from discord.ext import commands, tasks
import random
from flask import Flask
import threading

# Set up Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "The bot is running!"

# Set up bot with command prefix (e.g., !)
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to read messages
intents.guilds = True  # Allows the bot to join guilds (servers)
intents.members = True  # Allows the bot to track members joining/leaving

bot = commands.Bot(command_prefix="!", intents=intents)

# Channel IDs
WELCOME_CHANNEL_ID = 1270591778764095548  # Replace with your welcome channel ID
MESSAGE_CHANNEL_ID = 123456789012345678  # Replace with your target message channel ID

# Dictionary to store user levels
user_levels = {}
# Bio storage
user_bios = {}  # Made With Love By Eskiey

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is ready!')  # Made With Love By Eskiey

    # Set up Rich Presence
    activity = discord.Game(name="Playing with Discord API")
    await bot.change_presence(activity=activity)

    send_periodic_message.start()  # Start the periodic message task

# Welcome message for new members
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f'Welcome to the server, {member.mention}! 🎉')  # Made With Love By Eskiey

# Leveling system: Track user messages and increase their level
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Leveling logic
    author_id = message.author.id
    if author_id not in user_levels:
        user_levels[author_id] = 1  # Start at level 1

    user_levels[author_id] += random.randint(1, 3)  # Give random XP
    level = user_levels[author_id] // 100  # Every 100 XP = 1 level

    if user_levels[author_id] % 100 == 0:  # If user levels up
        await message.channel.send(
            f'{message.author.mention} just reached level {level}! 🎉')

    await bot.process_commands(message)  # Make sure other commands work

# Command to set or view user bio
@bot.command()
async def bio(ctx, *, bio: str = None):
    if bio:
        user_bios[ctx.author.id] = bio
        await ctx.send(f'Your bio has been updated to: "{bio}"')  # Made With Love By Eskiey
    else:
        user_bio = user_bios.get(ctx.author.id, "You have not set a bio yet.")
        await ctx.send(f'Your bio: "{user_bio}"')

# Simple hello command (automated greeting)
@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}! How’s it going?')

# Periodic task to send a message every 10 minutes
@tasks.loop(minutes=10)
async def send_periodic_message():
    channel = bot.get_channel(MESSAGE_CHANNEL_ID)
    if channel:
        await channel.send("Here's your regular reminder to stay awesome! 🌟")  # Made With Love By Eskiey

# Command to check user level
@bot.command()
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author  # Default to the author if no member is mentioned
    level = user_levels.get(member.id, 0) // 100  # Retrieve the user's level
    await ctx.send(f'{member.display_name} is at level {level}.')

# Command to kick a user
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You can't kick yourself!")
        return

    if reason is None:
        reason = "No reason provided."

    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked for: {reason}.')

# Command to ban a user
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You can't ban yourself!")
        return

    if reason is None:
        reason = "No reason provided."

    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned for: {reason}.')

# Command to unban a user using their Discord user ID
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    try:
        # Fetch the user using their ID to get the name
        user = await bot.fetch_user(user_id)

        # Try to unban the user from the guild
        await ctx.guild.unban(user)
        await ctx.send(f'{user.mention} has been unbanned.')

    except discord.NotFound:
        # If the user is not found in the ban list, respond with their name
        await ctx.send(f'{user.name}#{user.discriminator} (ID: {user_id}) was not found in the ban list.')

    except discord.HTTPException:
        # Handle other potential HTTP errors
        await ctx.send('There was an error trying to unban the user. Please try again later.')

# Error handler for missing permissions
@kick.error
@ban.error
@unban.error
async def missing_permissions_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            f'Sorry, {ctx.author.mention}, you do not have permission to use this command.'  # Made With Love By Eskiey
        )

# Command to display all available commands
@bot.command(name='commands')
async def show_commands(ctx):
    commands_list = [
        "!hello - Greet the bot.",
        "!level - Check the level of a user.",
        "!kick - Kick a user from the server.",
        "!ban - Ban a user from the server.",
        "!unban - Unban a user by their ID.",
        "!bio - Set or view your bio.",
        "!commands - Show this list of commands."
    ]

    commands_message = "Here are all the available commands:\n" + "\n".join(commands_list)
    await ctx.send(commands_message)

# Start the Flask server in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=3000)  # Use port 3000 for Replit

threading.Thread(target=run_flask).start()

# Run the Discord bot
bot_token = 'MTE3Mzg4ODg3Mzk1MzI1MTM1OA.GixK_b.WZpuON-k-BUjUvWUu9EkvVOKedYEUplhVyolLQ'  # Replace with your Discord bot token
bot.run(bot_token)  # Made With Love By Eskiey
