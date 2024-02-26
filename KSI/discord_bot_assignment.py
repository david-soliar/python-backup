import string
import requests
import random
from os import getenv
from discord import Intents, Message
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from notifiers import get_notifier

load_dotenv()
TOKEN = getenv("DISCORD_TOKEN")

bot_intents = Intents.default()
bot_intents.message_content = True

bot = commands.Bot(command_prefix="!",
                   case_insensitive=True,
                   intents=bot_intents)


class MemeGenerator:
    def __init__(self) -> None:
        self.url = "https://api.imgflip.com"

    def list_memes(self) -> str:
        memes = list()
        max_len = list()
        formated_memes = list()

        data = requests.get(self.url + "/get_memes").json()
        data = data["data"]["memes"]
        for i in range(25):
            data_memes = data[i]
            memes.append((data_memes["id"], data_memes["name"]))
            max_len.append(data_memes["id"])

        max_len = len(max(max_len, key=len))

        for id_name in memes:
            space = max_len - len(id_name[0]) + 1
            formated_memes.append(id_name[0] + " "*space + id_name[1])

        formated_memes = "\n".join(formated_memes)
        formated_memes = f"**Memes**\n```{formated_memes}```"
        return formated_memes

    def make_meme(self,
                  template_id: int,
                  top_text: str,
                  bottom_text: str) -> str:
        params = {
            'username': "x",
            'password': "x",
            'template_id': template_id,
            'text0': top_text,
            'text1': bottom_text
        }
        response = requests.request('POST',
                                    self.url + "/caption_image",
                                    params=params).json()

        if not response["success"]:
            error = response["error_message"]
            return f"Meme could not be generated. Reason: {error}"

        return response["data"]["url"]


class MentionsNotifier:
    def __init__(self) -> None:
        self.data = dict()

    def subscribe(self,
                  user_id: int,
                  email: str) -> None:
        self.data[user_id] = email

    def unsubscribe(self,
                    user_id: int) -> None:
        if user_id in self.data:
            del self.data[user_id]

    def notify_about_mention(self,
                             user_id: int,
                             msg_content: str) -> None:
        if user_id in self.data:
            email_send = get_notifier('email')

            settings = {
                'host': 'x',
                'port': 465,
                'ssl': True,

                'username': 'x',
                'password': 'x',

                'to': self.data[user_id],
                'from': 'x',

                'subject': "Discord mention",
                'message': f"Someone mentioned you in channel {msg_content}"
            }
            email_send.notify(**settings)


class Hangman:
    def __init__(self) -> None:
        self.data = dict()
        self.data_edit = dict()
        self.letters_list = list(string.ascii_lowercase)

    def start(self,
              player) -> str:
        head = "**Hangman**"
        player_name = f"Player: {player}"
        guesses = "Guesses: "
        lives = "Lives: 7"

        with open("words.txt", "r") as f:
            file = f.readlines()

        word = file[random.randrange(len(file))]
        word = word[:len(word)-1]

        word_hidden = "-"*len(word)
        word_hidden = [*word_hidden]
        word_hidden = " ".join(word_hidden)

        word_status = "Word: " + word_hidden

        text = "\n".join([head,
                          player_name,
                          guesses,
                          lives,
                          word_status])

        self.data[player] = [text, word]
        return text

    def guess_char(self,
                   player,
                   letter) -> str:
        letter = letter.lower()

        if player not in self.data:
            return "You have to start a new game first."

        text = self.data[player][0].split("\n")
        word = self.data[player][1]

        test_checked, result_value = self.letter_check(text, letter)
        if result_value:
            return test_checked

        if letter in text[2].split(": ")[1]:
            text = self.end_message(text,
                                    "You already guessed that.")
            text = "\n".join(text)
            return text

        update = ""
        hidden = text[4].split(": ")[1]
        hidden = hidden.replace(" ", "")

        hidden_char_check = (letter not in text[2].split(": ")[1])

        if (letter in word) and hidden_char_check:
            for i in range(len(word)):
                if (letter == word[i]) and (hidden[i] == "-"):
                    update += letter
                else:
                    update += hidden[i]
            text[4] = "Word: " + " ".join([*update])
            text = self.end_message(text,
                                    "Correct guess.")

        elif (letter not in word):
            lives = text[3].split(": ")
            lives_count = int(lives[1]) - 1
            text[3] = "Lives: " + str(lives_count)
            text = self.end_message(text,
                                    "Wrong guess.")
            if lives_count == 0:
                text = self.end_message(text,
                                        f"You lost! The word was: {word}")
                del self.data[player]
                del self.data_edit[player]
                text = "\n".join(text)
                return text

        text[2] = self.guess_count(letter, text)

        if text[4].split(": ")[1].replace(" ", "") == word:
            text = self.end_message(text, "You won!")
            del self.data[player]
            del self.data_edit[player]
            text = "\n".join(text)
            return text

        text = "\n".join(text)
        self.data[player][0] = text
        return text

    def guess_count(self,
                    letter,
                    text) -> str:
        if letter not in text[2].split(": ")[1]:
            guessed = text[2].split(": ")[1]
            guessed = guessed.split(", ")
            guessed.append(letter)

            g_letters = ", ".join(guessed)
            if g_letters[:2] == ", ":
                g_letters = g_letters[2:]
            return ("Guesses: " + g_letters)

    def letter_check(self,
                     text,
                     letter) -> tuple:
        if len(letter) > 1:
            text = self.end_message(text,
                                    "Enter only 1 letter at a time.")
            text = "\n".join(text)
            return (text, True)

        elif letter not in self.letters_list:
            text = self.end_message(text,
                                    "Enter only letters, no other characters.")
            text = "\n".join(text)
            return (text, True)
        return (False, False)

    def players(self,
                player,
                message) -> None:
        self.data_edit[player] = message

    def get_players(self):
        return self.data_edit

    def get_edit(self,
                 player):
        return self.data_edit[player]

    def end_message(self,
                    text,
                    message) -> list:
        if len(text) == 6:
            text[5] = message

        elif len(text) == 5:
            text.append(message)
        return text


# --------- LEVEL 1 ----------
meme_generator = MemeGenerator()


@bot.command(name="list_memes")
async def list_memes(ctx: Context) -> None:
    await ctx.send(meme_generator.list_memes())


@bot.command(name="make_meme")
async def make_meme(ctx: Context,
                    template_id: int,
                    top_text: str,
                    bottom_text: str) -> None:
    meme_url = meme_generator.make_meme(template_id, top_text, bottom_text)
    await ctx.send(meme_url)


# --------- LEVEL 2 ----------
mentions_notifier = MentionsNotifier()


@bot.command(name="subscribe")
async def subscribe(ctx: Context,
                    email: str) -> None:
    mentions_notifier.subscribe(ctx.author.id, email)


@bot.command(name="unsubscribe")
async def unsubscribe(ctx: Context) -> None:
    mentions_notifier.unsubscribe(ctx.author.id)


@bot.event
async def on_message(message: Message) -> None:
    await bot.process_commands(message)
    for i in range(len(message.mentions)):
        mentions_notifier.notify_about_mention(message.mentions[i].id,
                                               message.jump_url)


# --------- LEVEL 3 ----------
hangman = Hangman()


@bot.command(name="play_hangman")
async def play_hangman(ctx: Context) -> None:
    Hang_text = await ctx.send(hangman.start(ctx.author))
    hangman.players(ctx.author, Hang_text)


@bot.command(name="guess")
async def guess(ctx: Context, letter: str) -> None:
    if ctx.author in hangman.get_players():
        msg = hangman.get_edit(ctx.author)
        await msg.edit(content=hangman.guess_char(ctx.author, letter))
        await ctx.message.delete()
        return None

    await ctx.send(content=hangman.guess_char(ctx.author, letter))


bot.run(TOKEN)
