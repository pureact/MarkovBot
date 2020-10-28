import discord
import markovify

ACTIVATION_WORD = "name"
API_KEY = "discord_token"


def append_message(message):
    f = open("data.txt", "a")
    f.write(message.strip() + "\n")
    f.close()


def generate_markov():
    text = open("data.txt", "r").read()
    text_model = markovify.NewlineText(text, well_formed=False)
    return text_model.make_short_sentence(280, tries=100)


class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged in as {}!".format(self.user))

    async def on_message(self, message):
        if message.author.bot:
            return
        if ACTIVATION_WORD in message.content.lower():
            await message.channel.send(generate_markov())
        else:
            append_message(message.content)


client = MyClient()
client.run(API_KEY)
