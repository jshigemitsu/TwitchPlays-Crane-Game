import concurrent.futures
import keyboard
import pyautogui
import TwitchPlays_Connection
import serial
import time
import os
from TwitchPlays_KeyCodes import *

##################### GAME VARIABLES #####################

# Replace this with your Twitch username. Must be all lowercase.
TWITCH_CHANNEL = 'USERNAME_HERE' 

# If streaming on Youtube, set this to False
STREAMING_ON_TWITCH = True

# If you're streaming on Youtube, replace this with your Youtube's Channel ID
# Find this by clicking your Youtube profile pic -> Settings -> Advanced Settings
YOUTUBE_CHANNEL_ID = "YOUTUBE_CHANNEL_ID_HERE" 

# If you're using an Unlisted stream to test on Youtube, replace "None" below with your stream's URL in quotes.
# Otherwise you can leave this as "None"
YOUTUBE_STREAM_URL = None

arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to initialize

##################### MESSAGE QUEUE VARIABLES #####################

# MESSAGE_RATE controls how fast we process incoming Twitch Chat messages. It's the number of seconds it will take to handle all messages in the queue.
# This is used because Twitch delivers messages in "batches", rather than one at a time. So we process the messages over MESSAGE_RATE duration, rather than processing the entire batch at once.
# A smaller number means we go through the message queue faster, but we will run out of messages faster and activity might "stagnate" while waiting for a new batch. 
# A higher number means we go through the queue slower, and messages are more evenly spread out, but delay from the viewers' perspective is higher.
# You can set this to 0 to disable the queue and handle all messages immediately. However, then the wait before another "batch" of messages is more noticeable.
MESSAGE_RATE = 0.5
# MAX_QUEUE_LENGTH limits the number of commands that will be processed in a given "batch" of messages. 
# e.g. if you get a batch of 50 messages, you can choose to only process the first 10 of them and ignore the others.
# This is helpful for games where too many inputs at once can actually hinder the gameplay.
# Setting to ~50 is good for total chaos, ~5-10 is good for 2D platformers
MAX_QUEUE_LENGTH = 20
MAX_WORKERS = 100 # Maximum number of threads you can process at a time 

last_time = time.time()
message_queue = []
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
active_tasks = []
pyautogui.FAILSAFE = False

##########################################################

# Count down before starting, so you have time to load up the game
countdown = 5
while countdown > 0:
    print(countdown)
    countdown -= 1
    time.sleep(1)

if STREAMING_ON_TWITCH:
    t = TwitchPlays_Connection.Twitch()
    t.twitch_connect(TWITCH_CHANNEL)
else:
    t = TwitchPlays_Connection.YouTube()
    t.youtube_connect(YOUTUBE_CHANNEL_ID, YOUTUBE_STREAM_URL)

def handle_message(message):
    try:
        msg = message['message'].lower()
        username = message['username'].lower()
        special_user = "USERNAME_HERE"

        print("Got this message from " + username + ": " + msg)

        # Admin commands
        if msg == "up" and username == special_user:
            command = "up\n"  # Append newline since Arduino reads until newline
            arduino.write(command.encode('utf-8'))
            print("Sent command to have the crane to go up")
        
        if msg == "down" and username == special_user:
            command = "down\n"  # Append newline since Arduino reads until newline
            arduino.write(command.encode('utf-8'))
            print("Sent command to have the crane try to go down")
        
        if msg == "return" and username == special_user:
            command = "return\n"  # Append newline since Arduino reads until newline
            arduino.write(command.encode('utf-8'))
            print("Sent command to have the crane try to go down")

        # chat controlled commands
        # If the message is exactly "grab", send it to the Arduino
        if msg == "grab":
            command = "grab\n"  # Append newline since Arduino reads until newline
            arduino.write(command.encode('utf-8'))
            print("Sent command to have the crane try to grab")
            os._exit(0)

        # If the message is exactly "left", send it to the Arduino
        if msg == "left":
            command = "left\n"  # Append newline since Arduino reads until newline
            arduino.write(command.encode('utf-8'))
            print("Sent command to move crane left")

        # If the message is exactly "right", send it to the Arduino
        if msg == "right":
            command = "right\n"  # Append newline since Arduino reads until newline
            arduino.write(command.encode('utf-8'))
            print("Sent command to move crane right")

        # If the message is exactly "fwd", send it to the Arduino
        if msg == "fwd":
            command = "fwd\n"  # Append newline since Arduino reads until newline
            arduino.write(command.encode('utf-8'))
            print("Sent command to move crane fwd")

        # If the message is exactly "back", send it to the Arduino
        if msg == "back":
            command = "back\n"  # Append newline since Arduino reads until newline
            arduino.write(command.encode('utf-8'))
            print("Sent command to move crane back")

    except Exception as e:
        print("Encountered exception: " + str(e))

while True:

    active_tasks = [t for t in active_tasks if not t.done()]

    #Check for new messages
    new_messages = t.twitch_receive_messages();
    if new_messages:
        message_queue += new_messages; # New messages are added to the back of the queue
        message_queue = message_queue[-MAX_QUEUE_LENGTH:] # Shorten the queue to only the most recent X messages

    messages_to_handle = []
    if not message_queue:
        # No messages in the queue
        last_time = time.time()
    else:
        # Determine how many messages we should handle now
        r = 1 if MESSAGE_RATE == 0 else (time.time() - last_time) / MESSAGE_RATE
        n = int(r * len(message_queue))
        if n > 0:
            # Pop the messages we want off the front of the queue
            messages_to_handle = message_queue[0:n]
            del message_queue[0:n]
            last_time = time.time();

    # If user presses Shift+Backspace, automatically end the program
    if keyboard.is_pressed('shift+backspace'):
        exit()

    if not messages_to_handle:
        continue
    else:
        for message in messages_to_handle:
            if len(active_tasks) <= MAX_WORKERS:
                active_tasks.append(thread_pool.submit(handle_message, message))
            else:
                print(f'WARNING: active tasks ({len(active_tasks)}) exceeds number of workers ({MAX_WORKERS}). ({len(message_queue)} messages in the queue)')
 