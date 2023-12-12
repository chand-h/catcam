import threading
import signal

import bot
import cam
from sharedstate import shared_state

def run_bot():
    bot.start_bot()

def run_catcam():
    cam.start_catcam()

def signal_handler(sig, frame):
    shared_state.request_shutdown()  # Signal the threads to shut down

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    bot_thread = threading.Thread(target=run_bot)
    catcam_thread = threading.Thread(target=run_catcam)

    bot_thread.start()
    catcam_thread.start()

    bot_thread.join()
    catcam_thread.join()
