import discord
import markovify
import os
import json
import subprocess

if not os.path.exists("./models"):
    os.makedirs("./models/profiles")
    open("messages.txt", "w+").close()

CONFIG_FILE = "settings.json"

settings = json.load(open(CONFIG_FILE, "r"))

ACTIVATION_WORD = settings.get("activation_word", "bot").lower()
API_KEY = settings.get("api_key", "key")
IGNORED_CHANNELS = settings.get("ignored_channels", [])
ADMIN_ID = settings.get("admin_id", "")
USER_ID_MAP = settings.get("user_id_map")


def append_message(message, userid):
    f = open("./models/messages.txt", "a")
    if not os.path.exists("models/profiles/{}.txt".format(userid)):
        g = open("models/profiles/{}.txt".format(userid), "w+")
    else:
        g = open("models/profiles/{}.txt".format(userid), "a")
    f.write(message.strip() + "\n")
    g.write(message.strip() + "\n")
    f.close()
    g.close()


def map_user(name, userid):
    global USER_ID_MAP
    updated_settings = json.load(open(CONFIG_FILE, "r"))
    if name in updated_settings.get("user_id_map", {}):
        return
    else:
        updated_settings.get("user_id_map", {}).update({name: userid})
    USER_ID_MAP = updated_settings.get("user_id_map")
    json.dump(updated_settings, open(CONFIG_FILE, "w+"))


def generate_markov():
    text = open("./models/messages.txt", "r").read()
    text_model = markovify.NewlineText(text, well_formed=False)
    return text_model.make_short_sentence(280, tries=1000)


class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged in as {}!".format(self.user))

    async def on_message(self, message):
        if message.author.bot:
            return

        message_lower = message.content.lower()

        if (
            message_lower == "{} download channel".format(ACTIVATION_WORD)
            and str(message.author.id) == ADMIN_ID
        ):
            await message.channel.send("Downloading channel history...")
            messages = await message.channel.history(limit=51950).flatten()
            for msg in messages:
                if not msg.author.bot and ACTIVATION_WORD not in msg.content.lower():
                    append_message(msg.content, msg.author.id)
            await message.channel.send("History downloaded!")
            return

        if (
            message_lower.split(" ")[0] == ACTIVATION_WORD
            and message_lower.split(" ")[1] == "profile"
        ):
            if message_lower.split(" ")[2] in USER_ID_MAP:
                response = subprocess.check_output(
                    "pipenv run python3 markov_subprocess.py {}".format(
                        USER_ID_MAP.get(message_lower.split(" ")[2])
                    ),
                    shell=True,
                )
            else:
                response = subprocess.check_output(
                    "pipenv run python3 markov_subprocess.py {}".format(
                        message_lower.split(" ")[2]
                    ),
                    shell=True,
                )
            response = response.decode("utf-8")
            await message.channel.send(response)
            return

        if (
            message_lower.split(" ")[0] == ACTIVATION_WORD
            and message_lower.split(" ")[1] == "map"
        ):
            map_user(message_lower.split(" ")[2], message_lower.split(" ")[3])
            await message.channel.send("User mapped.")
            return

        if ACTIVATION_WORD in message_lower:
            await message.channel.send(generate_markov())
            return

        elif (
            str(message.channel.id) not in IGNORED_CHANNELS
            and ACTIVATION_WORD not in message.content
        ):
            append_message(message.content, message.author.id)
            return


client = MyClient()
client.run(API_KEY)