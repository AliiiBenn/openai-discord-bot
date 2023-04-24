from typing import Optional
import discord
from discord.ext import commands

import openai
from dotenv import load_dotenv
from os import getenv
import arrow

load_dotenv()
openai.api_key = getenv('OPENAI_API_KEY')



class ResponseAsker:
    def __init__(self, model : str, initial_messages : Optional[dict[str, str]] = None) -> None:
        self.model = model 
        
        if initial_messages is None:
            self.messages = []
        else:
            self.messages = [initial_messages]
        
    
    def add_new_message(self, role : str, new_message : str) -> None:
        if not isinstance(role, str):
            raise TypeError("role must be a str")
        
        if not isinstance(new_message, str):
            raise TypeError("new_message must be a str")
        
        self.messages.append({"role" : role, "content" : new_message})
        
        
    def ask_response(self) -> str:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages
        )
        
        text_result : str = response["choices"][0]["message"]["content"] # Where the dict store the response
        
        return text_result
    
    @staticmethod
    def create_empty() -> "ResponseAsker":
        return ResponseAsker("gpt-3.5-turbo")
    
    @staticmethod
    def create_with_initial_messages(initial_messages : dict[str, str]) -> "ResponseAsker":
        if not isinstance(initial_messages, dict):
            raise TypeError("initial_messages must be a dict[str, str]")
        
        return ResponseAsker("gpt-3.5-turbo", initial_messages)


class TimeAskingChecker:
    @staticmethod
    def check_if_time_is_asked(message : str) -> bool:
        messages_demande_heure = ["Excusez-moi, avez-vous l'heure s'il vous plaît ?", 
                        "Pourriez-vous me dire l'heure s'il vous plaît ?", 
                        "Savez-vous quelle heure il est ?", 
                        "Désolé de vous déranger, mais pourriez-vous me dire l'heure ?", 
                        "Avez-vous l'heure sur vous ?", 
                        "Pourriez-vous me donner l'heure exacte s'il vous plaît ?", 
                        "Vous auriez l'heure par hasard ?", 
                        "Pourriez-vous me dire quelle heure il est maintenant ?", 
                        "Pardon, pourriez-vous me donner l'heure s'il vous plaît ?", 
                        "Savez-vous combien il est ?", 
                        "Bonjour, pourriez-vous m'indiquer l'heure actuelle ?", 
                        "Excusez-moi, quelle heure est-il ?", 
                        "Pouvez-vous me donner l'heure s'il vous plaît ?", 
                        "Désolé de vous déranger, mais pourriez-vous me dire l'heure qu'il est ?", 
                        "Vous pourriez me donner l'heure s'il vous plaît ?", 
                        "Excusez-moi, pouvez-vous me dire quelle heure il est ?", 
                        "Bonjour, avez-vous l'heure s'il vous plaît ?", 
                        "Pouvez-vous me donner l'heure exacte s'il vous plaît ?", 
                        "Excusez-moi, pourriez-vous me dire l'heure qu'il est ?", 
                        "Savez-vous l'heure qu'il est actuellement ?", 
                        "Pardon, quelle heure est-il ?", 
                        "Bonjour, pouvez-vous me donner l'heure actuelle s'il vous plaît ?", 
                        "Excusez-moi, pourriez-vous me donner l'heure qu'il est ?", 
                        "Savez-vous quelle heure il est en ce moment ?", 
                        "Pouvez-vous me donner l'heure qu'il est s'il vous plaît ?", 
                        "Désolé de vous déranger, pourriez-vous me dire l'heure exacte ?", 
                        "Bonjour, auriez-vous l'heure sur vous ?", 
                        "Pardon, pouvez-vous me donner l'heure actuelle s'il vous plaît ?", 
                        "Excusez-moi, quelle heure est-il ?", 
                        "Pouvez-vous me dire l'heure qu'il est maintenant ?", 
                        "Savez-vous combien il est ?", 
                        "Pourriez-vous me donner l'heure qu'il est actuellement s'il vous plaît ?", 
                        "Désolé de vous déranger, mais pourriez-vous me dire l'heure qu'il est exactement ?", 
                        "Bonjour, auriez-vous l'heure s'il vous plaît ?", 
                        "Excusez-moi, pouvez-vous me donner l'heure qu'il est actuellement ?", 
                        "Pardon, quelle heure est-il ?", 
                        "Pouvez-vous me donner l'heure qu'il est exactement s'il vous plaît ?", 
                        "Savez-vous l'heure qu'il est maintenant ?", 
                        "Excusez-moi, pouvez-vous me dire quelle heure il est ?", 
                        "Bonjour, pourriez-vous me donner l'heure qu'il est actuellement s'il vous plaît ?"
        ]
        response = ResponseAsker.create_with_initial_messages(
            {"role" : "user", "content" : f"Ton rôle est de savoir si les messages que je vais t'envoyer demandent l'heure ou non. Tu dois uniquement répondre par True ou False. Par exemple si le message est << Je me demande bien quelle heure il est >> tu réponds True et pour << J'aime les chiens >> tu réponds False. Tu ne dois jamais dépasser un unique mot dans ta réponse. Tu dois uniquement répondre par True ou False et absolument aucun autre mot. Ne met pas de point ou autre ponctuation à la fin de ton message. Voici une liste d'exemples de messages qui demandent l'heure : {messages_demande_heure}. Voici le message : {message}"}
        ).ask_response()
        
        return "True" in response



class GetCurrentTime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    
    @commands.Cog.listener("on_message")
    async def send_time_if_asked(self, message : discord.Message) -> None:
        
        if message.author.bot:
            return 
        
        if TimeAskingChecker.check_if_time_is_asked(message.content):
            current_time = arrow.now("Europe/Paris").format("HH:mm")
            
            asker = ResponseAsker.create_with_initial_messages(
                {"role" : "user", "content" : f"Tu dois créer un message pour donner l'heure à un utilisateur à partir de ce temps {current_time} sous la forme << Il est *heure* et *minute* minutes>>. Ton message doit faire 30 mots maximum et ta réponse ne devra pas être trop soutenue. Un exemple de réponse que tu peux donner est << Il est actuellement {current_time} >>. Si tu le souhaites tu peux ajouter des commentaires comme << Il est tard >> ou << c'est bientôt l'heure de manger >> quand cela peut être nécessaire"}
            )
            
            response = asker.ask_response()
            
            await message.channel.send(response)
        
        
        
        
async def setup(bot : commands.Bot):
    await bot.add_cog(GetCurrentTime(bot))