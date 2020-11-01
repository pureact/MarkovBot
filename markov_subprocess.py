import markovify
import sys


def generate_markov(user_id):
    text = open("./models/profiles/{}.txt".format(user_id), "r").read()
    text_model = markovify.NewlineText(text, well_formed=False)
    return text_model.make_short_sentence(280, tries=1000)


print(generate_markov(sys.argv[1]))