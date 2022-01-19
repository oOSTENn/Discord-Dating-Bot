import discord
import sqlite3

from discord.ext import commands
from discord import utils
from discord.utils import get
from discord_buttons_plugin import *
from discord_components import DiscordComponents, Button, ButtonStyle

PREFIX = '/'

client = commands.Bot (command_prefix = PREFIX)
buttons = ButtonsClient(client)

client.remove_command('help')

connection = sqlite3.connect('server.db')
cursor = connection.cursor()

connection_two = sqlite3.connect('forms.db')
cursor_two = connection_two.cursor()

connection_third = sqlite3.connect('agree.db')
cursor_third = connection_third.cursor()

@client.event
async def on_ready():
    DiscordComponents(client)
    print('BOT connected')

@client.event
async def on_button_click(interaction):
	member = interaction.author
	channel = discord.utils.get(interaction.guild.channels, name=f"{member.id}")

	for value in cursor_third.execute("SELECT first_id, second_id FROM user_agree WHERE second_id = {}".format(member.id)):
		first_id = value[0]
		second_id = value[1]
		user_one = await client.fetch_user(first_id)
		user_two = await client.fetch_user(second_id)

		if interaction.component.label == f"Одобрить({str(first_id)[:3]}{str(second_id)[:3]})":
			overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)}

			category = discord.utils.get(interaction.guild.categories, name='чаты')

			channel = await interaction.guild.create_text_channel(name=f"chat-{str(first_id)[:3]}{str(second_id)[:3]}", overwrites = overwrites, category=category)
			await interaction.respond(content=f'Отлично! Для того чтобы начать общаться с {user_one.mention} перейдите: {channel.mention}**(/menu - перейти в меню)**')

			await channel.set_permissions(user_one, read_messages=True, send_messages=True)
			await channel.set_permissions(user_two, read_messages=True, send_messages=True)
			channel_two = await interaction.guild.create_voice_channel(name=f"chat-{str(first_id)[:3]}{str(second_id)[:3]}", overwrites = overwrites, category=category)
			await channel_two.set_permissions(user_one, connect = True, read_messages=True, speak=True)
			await channel_two.set_permissions(user_two, connect = True, read_messages=True, speak=True)

			cursor_third.execute("DELETE FROM user_agree WHERE first_id = ? and second_id = ?", (first_id,second_id,))
			connection_third.commit()

			channel_three = discord.utils.get(interaction.guild.channels, name=f"{first_id}")
			await channel_three.send(f"Пользователь {user_two.mention} принял вашу заявку! Для начала общения перейдите: {channel.mention}**(/menu - перейти в меню)**")

		if interaction.component.label == f"Отклонить({str(first_id)[:3]}{str(second_id)[:3]})":
			cursor_third.execute("DELETE FROM user_agree WHERE first_id = ? and second_id = ?", (first_id,second_id,))
			connection_third.commit()
			await interaction.respond(content="Вы отклонили анкету!")


	if interaction.component.label == "⠀⠀⠀⠀⠀⠀⠀Составить анкету⠀⠀⠀⠀⠀⠀⠀":
		await interaction.respond(content=f'Для заполнения анкеты пропишите /start')
	if interaction.component.label == "⠀Заполнить свою анкету заново⠀":
		await interaction.respond(content=f'Для заполнения анкеты пропишите /start')

	if interaction.component.label == "⠀⠀⠀⠀⠀⠀Начать⠀⠀⠀⠀⠀⠀":
		channel = discord.utils.get(interaction.guild.channels, name=f"{member.id}")
		if channel == None:
			overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)}

			category = discord.utils.get(interaction.guild.categories, name='поиск')

			channel = await interaction.guild.create_text_channel(name=f"{member.id}", overwrites = overwrites, category=category)

			await channel.set_permissions(member, read_messages=True, send_messages=True)

			await channel.send(
					embed=discord.Embed(title="Это ваш личный чат с ботом!", description="Сформируйте анкету, и можете начинать поиски!", color = discord.Color.blue()),
					components=[
					Button(style=ButtonStyle.blue, label="⠀⠀⠀⠀⠀⠀⠀Составить анкету⠀⠀⠀⠀⠀⠀⠀"),
					]
				)
			await interaction.respond(content=f"Чат был успешно создан! Перейдите в: {channel.mention}")			
		else:
			await interaction.respond(content="У вас уже создан чат с ботом.")
	if interaction.component.label == "⠀Начать просмотр других анкет⠀":
		for value in cursor_two.execute(f"SELECT * FROM forms WHERE id != {member.id} ORDER BY RANDOM() LIMIT 1"):
			await interaction.respond(content="Переходим по вашему запросу...")
			
			name = value[0]
			age =value[1]
			city = value[2]
			about_me = value[3]
			img = value[4]
			member_id = value[5]

			cursor.execute("UPDATE users SET m_id = ? WHERE id = ?", (member_id, member.id,))
			connection.commit()

			emb=discord.Embed(
			title=f"{name} - {age}({city})", 
			description = f"{about_me}", 
			color = discord.Color.blue(), 
			)
			emb.set_image(url = img)
			await channel.send(embed=emb,
			components=[
				Button(style=ButtonStyle.green, label="Отправить заявку"),
				Button(style=ButtonStyle.red, label="Следующая анкета"),
				Button(style=ButtonStyle.blue, label="Вернуться в меню")
			]
		)
	if interaction.component.label == "Следующая анкета":
		for value in cursor_two.execute(f"SELECT * FROM forms WHERE id != {member.id} ORDER BY RANDOM() LIMIT 1"):
			await interaction.respond(content="Переходим по вашему запросу...")
			
			name = value[0]
			age =value[1]
			city = value[2]
			about_me = value[3]
			img = value[4]
			member_id = value[5]

			cursor.execute("UPDATE users SET m_id = ? WHERE id = ?", (member_id, member.id,))
			connection.commit()

			emb=discord.Embed(
			title=f"{name} - {age}({city})", 
			description = f"{about_me}", 
			color = discord.Color.blue(), 
			)
			emb.set_image(url = img)
			await channel.send(embed=emb,
			components=[
				Button(style=ButtonStyle.green, label="Отправить заявку"),
				Button(style=ButtonStyle.red, label="Следующая анкета"),
				Button(style=ButtonStyle.blue, label="Вернуться в меню")
			]
		)

	if interaction.component.label == "Вернуться в меню":
		await interaction.respond(content="Переходим по вашему запросу...")
		emb=discord.Embed(
		title=f"Меню взаимодействия", 
		description = f"выберите нужный пункт", 
		color = discord.Color.blue(), 
		)
		await channel.send(embed=emb,
		components=[
			Button(style=ButtonStyle.blue, label="⠀Начать просмотр других анкет⠀"),
			Button(style=ButtonStyle.blue, label="⠀Заполнить свою анкету заново⠀"),
			Button(style=ButtonStyle.blue, label="Как мне изменить фото в анкете?"),
			Button(style=ButtonStyle.blue, label="Как выглядит моя анкета сейчас?")
		]
	)

	if interaction.component.label == "Как мне изменить фото в анкете?":
		await interaction.respond(content="Для того чтобы изменить фото в своей анкете, просто отправьте желаемую фотографию в любой момент.")

	if interaction.component.label == "Как выглядит моя анкета сейчас?":
		await interaction.respond(content="Переходим по вашему запросу...")
		for value in cursor_two.execute("SELECT name, age, city, about_me, img FROM forms WHERE id = {}".format(member.id)):
			name = value[0]
			age = value[1]
			city = value[2]
			about_me = value[3]
			img = value[4]

			emb=discord.Embed(
			title=f"{name} - {age}({city})", 
			description = f"{about_me}", 
			color = discord.Color.blue(), 
			)
			emb.set_image(url = img)
			await channel.send(embed=emb,
			components=[
				Button(style=ButtonStyle.blue, label="⠀Начать просмотр других анкет⠀"),
				Button(style=ButtonStyle.blue, label="⠀Заполнить свою анкету заново⠀"),
				Button(style=ButtonStyle.blue, label="Как мне изменить фото в анкете?"),
				Button(style=ButtonStyle.blue, label="Как выглядит моя анкета сейчас?")
			]
		)
	if interaction.component.label == "Отправить заявку":
		for value in cursor_two.execute("SELECT name, age, city, about_me, img FROM forms WHERE id = {}".format(member.id)):
			name = value[0]
			age = value[1]
			city = value[2]
			about_me = value[3]
			img = value[4]
		for value in cursor.execute("SELECT m_id FROM users WHERE id = {}".format(member.id)):
			m_id = value[0]
			channel_one = discord.utils.get(interaction.guild.channels, name=f"chat-{str(m_id)[:3]}{str(member.id)[:3]}")
			channel_two = discord.utils.get(interaction.guild.channels, name=f"chat-{str(member.id)[:3]}{str(m_id)[:3]}")
			if channel_one == None and channel_two == None:
				if cursor_third.execute(f"SELECT first_id FROM user_agree WHERE first_id = {member.id} and second_id = {m_id}").fetchone() is None:
					cursor_third.execute(f"INSERT INTO user_agree VALUES ({member.id}, {m_id})")
					connection_third.commit()
					
					channel = discord.utils.get(interaction.guild.channels, name=f"{m_id}")

					first_id = str(member.id)[:3]
					second_id = str(m_id)[:3]

					await channel.send("Ваша анкета кому-то понравилась!")

					emb=discord.Embed(
					title=f"{name} - {age}({city})", 
					description = f"{about_me}", 
					color = discord.Color.blue(), 
					)
					emb.set_image(url = img)
					await channel.send(embed=emb,
					components=[[
						Button(style=ButtonStyle.blue, label=f"Одобрить({first_id}{second_id})"),
						Button(style=ButtonStyle.blue, label=f"Отклонить({first_id}{second_id})")]])
					await channel.send("**/menu - перейти в меню**")
					await interaction.respond(content="Заявка была отправлена! Ожидайте ответа**(/menu - перейти в меню)**.")
				else:
					await interaction.respond(content="Заявка данному человеку уже была отправлена. Ожидайте ответа**(/menu - перейти в меню)**.")
			else:
				await interaction.respond(content="У вас уже создан чат с этим человеком! **(/menu - перейти в меню)**.")


@client.event
async def on_message(message):
	author_id = message.author.id
	channel = discord.utils.get(message.guild.channels, name=f"{author_id}")
	if message.channel == channel:
		try:
			img = message.attachments[0].url
			cursor_two.execute("UPDATE forms SET img = ? WHERE id = ?", (img, author_id,))
			connection_two.commit()
			for value in cursor_two.execute("SELECT name, age, city, about_me FROM forms WHERE id = {}".format(author_id)):
				name = value[0]
				age = value[1]
				city = value[2]
				about_me = value[3]

				emb=discord.Embed(
				title=f"{name} - {age}({city})", 
				description = f"{about_me}", 
				color = discord.Color.blue(), 
				)
				emb.set_image(url = img)
				await channel.send(embed=emb,
				components=[
					Button(style=ButtonStyle.blue, label="⠀Начать просмотр других анкет⠀"),
					Button(style=ButtonStyle.blue, label="⠀Заполнить свою анкету заново⠀"),
					Button(style=ButtonStyle.blue, label="Как мне изменить фото в анкете?"),
					Button(style=ButtonStyle.blue, label="Как выглядит моя анкета сейчас?")
				]
			)
		except:
			if message.content.startswith('/start'):
				if cursor_two.execute(f"SELECT id FROM forms WHERE id = {author_id}").fetchone() is None:
					cursor_two.execute(f"INSERT INTO forms VALUES ('none', 'none', 'none', 'none', 'https://media.discordapp.net/attachments/926927915499786343/926948209664868472/fmt_89_24_foto-1.png?width=670&height=670', {author_id})")
					connection_two.commit()
				else:
					pass

				if message.channel == channel:
					await channel.send('Как вас зовут?')
					name = await client.wait_for('message', check=lambda m: m.author == message.author and m.channel == channel)
					name = name.content
					await channel.send('Сколько вам лет?')
					age = await client.wait_for('message', check=lambda m: m.author == message.author and m.channel == channel)
					age = age.content
					await channel.send('Из какого вы города?')
					city = await client.wait_for('message', check=lambda m: m.author == message.author and m.channel == channel)
					city = city.content
					await channel.send('Расскажите немного о себе.')
					about_me = await client.wait_for('message', check=lambda m: m.author == message.author and m.channel == channel)
					about_me = about_me.content
					await channel.send('Для того чтобы сменить аватарку, отправьте желаемое фото(работает в любой момент).')
					cursor_two.execute("UPDATE forms SET name = ?, age = ?,  city = ?, about_me = ? WHERE id = ?", (name, age, city, about_me, author_id,))
					connection_two.commit()
					await channel.send("Отлично! Вы закончили заполнять анкету. Вот что получилось:")
					for value in cursor_two.execute("SELECT img FROM forms WHERE id = {}".format(author_id)):
						img = value[0]
						emb=discord.Embed(
						title=f"{name} - {age}({city})", 
						description = f"{about_me}", 
						color = discord.Color.blue(), 
						)
						emb.set_image(url = img)
						await channel.send(embed=emb,
						components=[
							Button(style=ButtonStyle.blue, label="⠀Начать просмотр других анкет⠀"),
							Button(style=ButtonStyle.blue, label="⠀Заполнить свою анкету заново⠀"),
							Button(style=ButtonStyle.blue, label="Как мне изменить фото в анкете?"),
							Button(style=ButtonStyle.blue, label="Как выглядит моя анкета сейчас?")
						]
					)
		if message.content.startswith('/menu'):
			emb=discord.Embed(
			title=f"Меню взаимодействия", 
			description = f"выберите нужный пункт", 
			color = discord.Color.blue(), 
			)
			await channel.send(embed=emb,
			components=[
				Button(style=ButtonStyle.blue, label="⠀Начать просмотр других анкет⠀"),
				Button(style=ButtonStyle.blue, label="⠀Заполнить свою анкету заново⠀"),
				Button(style=ButtonStyle.blue, label="Как мне изменить фото в анкете?"),
				Button(style=ButtonStyle.blue, label="Как выглядит моя анкета сейчас?")
			]
		)

#RUN + CONECT
token = open('token.txt', 'r').readline()

client.run(token)

