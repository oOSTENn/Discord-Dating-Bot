import discord
import sqlite3

from discord.ext import commands
from discord_components import DiscordComponents

intents=intents=discord.Intents.all()

PREFIX = '/'

client = commands.Bot (command_prefix = PREFIX, intents=intents)

client.remove_command('help')

connection = sqlite3.connect('server.db')
cursor = connection.cursor()

@client.event
async def on_ready():
    DiscordComponents(client)
    print('BOT connected')

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        name BLOB,
        id INT,
        m_id INT
    )""")
    connection.commit()

    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0)")
            else:
                pass
    connection.commit()

@client.event
async def on_member_join(member):
    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0)")
            else:
                pass
    connection.commit()

#RUN + CONECT
token = open('token.txt', 'r').readline()

client.run(token)