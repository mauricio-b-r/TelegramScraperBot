import asyncio
import datetime
import re
import requests
import telepot
import telepot.aio

from bs4 import BeautifulSoup
from dotenv import dotenv_values
from pprint import pprint
from telepot.aio.loop import MessageLoop

config = dotenv_values('.env')

ethermine_url = f'https://api.ethermine.org/miner/{config["ADDRESS"]}/dashboard'
dictionary_url = 'https://www.oxfordlearnersdictionaries.com/definition/english/'

async def handle(msg):
	async def commands(text):
		help = """
		Commands:
		/start
		/help
		/dictionary {text}
		/money
		♬ ♪ ♮♫♭♩
		Never gonna give you up
		Never gonna let you down
		Never gonna run around and desert you
		Never gonna make you cry
		Never gonna say goodbye
		Never gonna tell a lie and hurt you 
		♬ ♪ ♮♫♭♩
		"""
		command_list = re.findall(r'(/[A-Za-z]+)', text)

		try:
			command=command_list[0]
		except IndexError:
			command = ''

		text = text.replace(command, '').strip().lower()
		switcher = {
			'/start': lambda: bot.sendMessage(chat_id, 'Hi buddy'),
			'/help': lambda: bot.sendMessage(chat_id, help),
			'/dictionary': lambda: getMeaning(text),
			'/money': lambda: getMinerData(),
		}
		return await switcher.get(command.strip().lower(), lambda: bot.sendMessage(chat_id, help))()

	global chat_id
	# These are some useful variables
	content_type, chat_type, chat_id = telepot.glance(msg)
	# Log variables
	print(content_type, chat_type, chat_id)
	pprint(msg)
	global username
	username = msg['chat']['first_name']
	# Check that the content type is text and not the starting
	if content_type == 'text':
		text = str(msg['text'])
		await commands(text)


def fetchEthermineData():
	try:
		r = requests.get(ethermine_url)
		data = r.json()['data']['currentStatistics']
		return dict(data), r.status_code
	except:
		return None, r.status_code


async def getMinerData():
	data, status = fetchEthermineData()
	if data:
		response = f"""Hello {username}!
		Reporting...
		active workers: {data['activeWorkers']}
		current hashrate: {data['currentHashrate']/1_000_000} MHz
		reported hashrate: {data['reportedHashrate']/1_000_000} MHz
		lastSeen: {datetime.datetime.utcfromtimestamp(data['lastSeen']).isoformat()}
		unpaid: {data['unpaid']/10**18} ethers
		Goodbye...
		""" 
	else:
		response = f"Error {status}"
	await bot.sendMessage(chat_id, response)

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
