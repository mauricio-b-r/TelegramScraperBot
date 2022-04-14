import asyncio
import re
import requests
import telepot
import telepot.aio

from bs4 import BeautifulSoup
from dotenv import dotenv_values
from pprint import pprint
from telepot.aio.loop import MessageLoop
from requests_html import HTMLSession
from fake_useragent import UserAgent

config = dotenv_values('.env')

ethermine_url = f'https://ethermine.org/miners/{config["ADDRESS"]}/dashboard'
dictionary_url = 'https://www.oxfordlearnersdictionaries.com/definition/english/'

session = HTMLSession()

async def handle(msg):
	async def commands(command, text):
		help = """
			/help
			/dictionary {text}
			/unpaid
			/payday
			/hashrate
		"""
		text = text.replace(command, '').strip().lower()
		switcher = {
			'/start':await bot.sendMessage(chat_id, 'Hi buddy'),
			'/help':await bot.sendMessage(chat_id, help),
			'/dictionary':await getMeaning(text),
			'/unpaid':await bot.sendMessage(chat_id, 'unpaid'),
			'/payday':await bot.sendMessage(chat_id, 'payday'),
			'/hashrate':await bot.sendMessage(chat_id, 'hashrate'),
		}
		pprint(text, 'text')
		return switcher.get(command.strip().lower(), await bot.sendMessage(chat_id, help))

	global chat_id
	# These are some useful variables
	content_type, chat_type, chat_id = telepot.glance(msg)
	# Log variables
	print(content_type, chat_type, chat_id)
	pprint(msg)
	username = msg['chat']['first_name']
	# Check that the content type is text and not the starting
	if content_type == 'text':
		text = str(msg['text'])
		await commands(text)


async def getHashrate():
	# create url
	r = session.get(ethermine_url)
	r.html.render()
	# pprint(r.html)
	# r.html.search('Python 2 will retire in only {months} months!')['months']

	# # let's soup the page
	# soup = BeautifulSoup(page.text, 'html.parser')
	# pprint(soup)
	# try:
	# 	# get Hashrate
	# 	definition = soup.find('span', {'class': 'def'}).text
	# 	await bot.sendMessage(chat_id, definition)
	# except:
	# 	await bot.sendMessage(chat_id, 'Something went wrong...')


async def getMeaning(text):
	# create url
	url = 'https://www.oxfordlearnersdictionaries.com/definition/english/' + text
	# define headers
	headers = { 'User-Agent': 'Generic user agent' }
	# get page
	page = requests.get(url, headers=headers)
	# let's soup the page
	soup = BeautifulSoup(page.text, 'html.parser')
	# pprint(soup)
	try:
		# get MP3 and definition
		try:
			# get MP3
			mp3link = soup.find('div', {'class': 'sound audio_play_button pron-uk icon-audio'}).get('data-src-mp3')
			await bot.sendAudio(chat_id=chat_id, audio=mp3link)
		except:
			await bot.sendMessage(chat_id, 'Pronunciation not found!')
		try:
			# get definition
			definition = soup.find('span', {'class': 'def'}).text
			await bot.sendMessage(chat_id, definition)
		except:
			await bot.sendMessage(chat_id, 'Meaning not found!')
	except:
		await bot.sendMessage(chat_id, 'Something went wrong...')

# Program startup
TOKEN = config["TELEGRAM_TOKEN"]
bot = telepot.aio.Bot(TOKEN)
loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot, handle).run_forever())
print('Listening ...')

# Keep the program running
loop.run_forever()