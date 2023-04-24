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
        self.plugins : list[str] = []
        
        
    def load_new_plugin(self, plugin_name : str) -> None:
        self.plugins.extend(
            [module.name for module in pkgutil.iter_modules([self.plugins_folder_path + plugin_name], prefix=f"plugins.{plugin_name}.")]
        )


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
        command_prefix='!',
        intents=discord.Intents.all()
        )
        
        self.plugin_loader = PluginLoader('scripts/plugins/')
        self.plugin_loader.load_new_plugin('messages_capture_system')

    async def setup_hook(self) -> None:
        print(self.plugin_loader.plugins)
        for plugin in self.plugin_loader.plugins:
            await self.load_extension(plugin)
        
        await self.tree.sync()

    async def on_ready(self):
        print('-------------')
        print(f'Logged in as {self.user}')
        print(f'Bot is ready.')

bot = MyBot()

if __name__ == '__main__':
    dotenv.load_dotenv()
    token = os.getenv('TOKEN')

    if token is None:
        raise ValueError('Token not found')

    bot.run(token)