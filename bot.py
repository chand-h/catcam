import os
from twitchio.ext import commands
import random
import asyncio
import keyboard
import simpleaudio

from twitchapi import TwitchAPI
from sharedstate import shared_state

twitch = TwitchAPI()

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=os.environ['TMI_TOKEN'], prefix='!', initial_channels=['catcam69000'])
        

    async def event_ready(self):
        print(f'chatbot ready | {self.nick}')
        while not keyboard.is_pressed('ctrl+alt+z'):
            await asyncio.sleep(0.1)
        exit()



    async def event_message(self, message):
        if message.echo:
            return

        print(message.content)
        await self.handle_commands(message)

    async def send_msg(self, ctx, msg):
        await ctx.send(f'[bot] {msg}')
    
    @commands.command(name='meow')
    async def meow(self, ctx):
        user_id = str(ctx.author.id)
        channel_id = str(ctx.channel.name)
        if twitch.check_user_follows(user_id, channel_id):
            await self.play_meow(ctx)
        else:
            await ctx.send('[bot] must be a follower to use !meow')
        
    

    async def play_meow(self, ctx):
        meow_folder = 'meows'
        meow_files = [f for f in os.listdir(meow_folder) if f.endswith('.wav')]
        if meow_files:
            random_meow = random.choice(meow_files)
            try:
                # Define a function to play sound
                def play_sound():
                    wave_obj = simpleaudio.WaveObject.from_wave_file(f'{meow_folder}/{random_meow}')
                    play_obj = wave_obj.play()
                    play_obj.wait_done()

                # Run the play_sound function in a separate thread
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, play_sound)

                await ctx.send('[bot] playing meow sound...')
            except Exception as e:
                await ctx.send(f'[bot] Error: {e}')


    @commands.command(name='boxes')
    async def toggle_boxes(self, ctx):
        await ctx.send('[bot] hiding boxes...') if shared_state.get_show_boxes() else await ctx.send('[bot] showing boxes...')
        shared_state.toggle_show_boxes()

    @commands.command(name='text')
    async def toggle_text(self, ctx):
        await ctx.send('[bot] hiding text...') if shared_state.get_show_text() else await ctx.send('[bot] showing text...')
        shared_state.toggle_show_text()

    


def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    bot = Bot()
    bot.run()