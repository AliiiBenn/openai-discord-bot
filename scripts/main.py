import discord
from discord.ext import commands

import os, dotenv, pkgutil
from dataclasses import dataclass 


@dataclass
class Plugin:
    name : str


class PluginLoader:
    def __init__(self, plugins_folder_path : str) -> None:
        self.plugins_folder_path = plugins_folder_path
        
        
    def load_new_plugin(self, plugin_name : str) -> list[str]:
        return [module.name for module in pkgutil.iter_modules([self.plugins_folder_path + plugin_name], prefix=plugin_name + '.')]


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
        command_prefix='!',
        intents=discord.Intents.all()
        )
        
        

    async def setup_hook(self) -> None:
        await self.tree.sync()

    async def on_ready(self):
        print('-------------')
        print(f'Logged in as {self.user}')
        print(f'Bot is ready.')

bot = MyBot()

if __name__ == '__main__':
    dotenv.load_dotenv()
    token = os.getenv('token')

    if token is None:
        raise ValueError('Token not found')

    bot.run(token)