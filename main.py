import nextcord
import os
import sys

from nextcord.ext import commands
from config import token
from loguru import logger

logger.remove()
logger.add(sys.stderr, format='<white>{time:HH:mm:ss}</white>'
                           ' | <level>{level: <8}</level>'
                           ' | <cyan>{line}</cyan>'
                           ' - <white>{message}</white>')

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix='?', intents=intents)
bot.remove_command('help')

logger.info('Начинаю загружать коги...')
for fn in os.listdir("./cogs"):
	if fn.endswith(".py"):
		bot.load_extension(f"cogs.{fn[:-3]}")
		
bot.run(token)
