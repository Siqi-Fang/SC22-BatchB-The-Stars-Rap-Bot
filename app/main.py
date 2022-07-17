# Run by typing python3 main.py

# **IMPORTANT:** only collaborators on the project where you run
# this can access this web server!

"""
    Bonus points if you want to have internship at AI Camp
    1. How can we save what user built? And if we can save them, like allow them to publish, can we load the saved results back on the home page? 
    2. Can you add a button for each generated item at the frontend to just allow that item to be added to the story that the user is building? 
    3. What other features you'd like to develop to help AI write better with a user? 
    4. How to speed up the model run? Quantize the model? Using a GPU to run the model? 
"""

# import basics
import os
import text2emotion as te
from textblob import TextBlob
import boto3
#import utils
from multiprocessing import Process, Queue
import random

# import stuff for our web server
from flask import Flask, request, redirect, url_for, render_template, session
from utils import get_base_url
from chatbot import produce_prompt, create_mp3_files, easy_postproc,generate_lyrics
from aitextgen import aitextgen

# import stuff for our models
ai = aitextgen(model_folder="model/", to_gpu=False)

# setup the webserver
# port may need to be changed if there are multiple flask servers running on same server
port = 5000
base_url = get_base_url(port)


# if the base url is not empty, then the server is runn    ing in development, and we need to specify the static folder so that the static files are served
if base_url == '/':
    app = Flask(__name__)
else:
    app = Flask(__name__, static_url_path=base_url+'static')

app.secret_key = os.urandom(64)

# set up the routes and logic for the webserver


@app.route(f'{base_url}')
def home():
    return render_template('index.html')

# redirect to demo.html
@app.route(f'{base_url}', methods=['POST'])
def home_post():
    return redirect(url_for('results'))

# redirect to about.html
@app.route(f'{base_url}/about/')
def about_page():
    return render_template('about.html')


@app.route(f'{base_url}/results/')
def results():
    if 'data' in session:
        data = session['data']
        #create_mp3_files(data)
        
        return render_template('demo.html', generated=data['generated'],track=data['track'], chatbot="")
    else:
        return render_template('demo.html', generated="The generated rap will show up here!",track="2-backtrack-lyric-006.90bpm_sad.mp3", chatbot="Tell us how's your day?")


@app.route(f'{base_url}/generate_text/', methods=["POST"])
def generate_text():
    """
    view function that will return json response for generated text.
    """

    response = request.form['response']
    # sentiment analysis
    secondary_emotions = te.get_emotion(response)
    primary = "Positive" if TextBlob(response).sentiment.polarity > 0 else "Negative"
    # grabs emotion with highest score
    secondary_emotion = ""
    max_score = -1
    for key in secondary_emotions:
        if secondary_emotions[key] >= max_score:
            secondary_emotion = key.lower()

    res = produce_prompt(primary, secondary_emotion) # returns(prompt, backing genre)
    prompt, track, bpm = res[0], res[1], res[2]
    print("#PROMPT# :: "+prompt, "TRACK:", track)

    #output = ai.generate(prompt=prompt, min_length=400, max_length=500, temperature=1, top_p=.98, return_as_list=True)[0]
    candidates = [['or who could stare at the windows at the moment', "that's who you want to be, man, and that's how i feel romant", "so you wonder why that dude's still around", 'so much krill, you want me to make you lie down'],['i want a hippopotamus for christmas', "yoo, you see, i'm just a man of my opinion  isthmus", 'just learn to be humble and stand up to people', 'they want a n*** with a heart of th and creeple'],["so are you sure you haven't been gone a while", 'and i can touch your light skin while i work with hair style', "don't wanna stare in your face, for the time ever", "don't wanna look at your face, for fear fo your endeavor"],['in the 6 lane with the hoes in the garage', 'we could take the bus home, and if not do some without sabotage', 'we could do it again, n*** you know i promise you', 'and i promise the real n***, we will be the up to'],['you need to watch out for these n*** that never stop', "if you heard the chorus, you know i'm like this on top", "you don't know my name, you just know i'm like me", 'i got a big burner and cut up some tree'],["I spit these raps like I'm spongebob marble", 'you better hit me when you see my voice and garble', "you tryin' to play with my s***? get f*** now", "you just don't know what to write on the side of that you sow"]]
    #generated_list = easy_postproc(output)
    #genrerated_list = generate_lyrics(output, prompt)
    generated_list = random.choice(candidates)
    generated_str = "<br>".join(generated_list)
    data = {'generated': generated_str,
           'track':track}
    session['data'] =  data # # original output
    
    create_mp3_files(generated_list, bpm)
    
    return redirect(url_for('results'))


#     secondary_emotions = emotion_fix(primary, secondary_emotion)

#     return redirect(url_for('second_question',emotions = (primary,secondary_emotions))) # pass variable to second_question()

    
def _gen_text_helper(output, prompt, queue):
    
    generated_list = queue.get()
   
    generated_list = generate_lyrics(output,prompt) # list
    create_mp3_files(generated_list)
    
    queue.put(generated_list)

        
# # define additional routes here
# # for example:
# @app.route(f'{base_url}/second_question/<emotions>')
# def second_question(emotions):
#     if emotions[1].len() == 1:
#         secondary = emotions[1][0]
#         return redirect(url_for("output_result",emotions=(emotions[0],secondary)))
#     else:
#         second_question = "we've detected these emotions from your input; choose the one that best fits:\n" + "\n".join(emotions) + "which one do you feel the strongest about:"
#         return render_template('demo.html', chatbot=second_question)

    
    
# @app.route(f'{base_url}/output_result/<emotions>', methods=["POST"])
# def output_result(emotions):
#     # emotions : (primary, secondary)
    
#     prompt = produce_prompt(emotions[0], emotions[1])

#     generated = ai.generate(
#             n=1,
#             batch_size=3,
#             prompt=str(prompt),
#             max_length=300,
#             temperature=0.9,
#             return_as_list=True
#        )
   
#     data = {'generated_ls': generated}
#     session['data'] = generated[0] # this is where to put the final output
#     return redirect(url_for('results'))



if __name__ == '__main__':
    # IMPORTANT: change url to the site where you are editing this file.
    website_url = 'cocalc10.ai-camp.dev'

    print(f'Try to open\n\n    https://{website_url}' + base_url + '\n\n')
    app.run(host='0.0.0.0', port=port, debug=True,use_reloader=False)


