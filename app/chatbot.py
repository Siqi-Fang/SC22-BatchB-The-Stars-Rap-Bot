#DON'T upload anywhere public until key in function create_mp3_files is REMOVED!!!!
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

import random
from flask import url_for
from moviepy.editor import concatenate_audioclips, AudioFileClip
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import RobertaTokenizer, RobertaForMaskedLM
import torch, requests
import random
import better_profanity
from PyDictionary import PyDictionary
import nltk
from nltk.corpus import words
#nltk.download('words')
dictionary = PyDictionary()
global rhyme_inp
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
model = RobertaForMaskedLM.from_pretrained('roberta-base')
import cmudict
from math import floor
import boto3


def emotion_fix(primary_emotion, multi): # helper keep here
    
    """ Makes secondary emoiton less ambigious by primary"""
    if primary_emotion=="Positive" and (multi["Sad"] >0 or multi["Fear"] >0 or multi["Angry"] >0) :
        multi["Happy"] = multi['Happy']+0.5
    elif primary_emotion=="Negative" and (multi["Happy"] >0):
        further=input("we've detected that your emotion has both negative and positive aspects. Tell us more about the negative: do you feel more sad, angry, or fear?")
        if further.lower()=="sad":
            multi["Sad"] = multi['Sad']+0.5
        elif further.lower()=="angry":
            multi["Angry"] = multi['Angry']+0.5
        elif further.lower()=="fear":
            multi["Fear"] = multi['Fear']+0.5
    else:
          pass
    # finetune
    
    emotions = []
    for key in multi:
        if multi[key] >= 0.5:
            emotions.append(key)

    return emotions

#     if emotion=="happy":
#         secondary_emotion="happy"
#     elif emotion.lower() in["sad", "angry", "fear"]:
#         secondary_emotion=emotion.lower()
#     elif emotion=="surprised":
#         secondary_emotion="surprised"
            
#     return secondary_emotion

def easy_postproc(output):
    sent_list = output.split("\n")

    print(sent_list[0])
    main_sentences = []
    # grabs good sentence with good syllable count
    for sent in sent_list:
        if(sent):
            syllables = total_syllables(sent)
        else:
            syllables = 0

        if(10 < syllables and syllables < 14):
            main_sentences.append(censor_sentence(sent))


    follow_words = ["and","but"]
    for i in range(len(main_sentences)):
        first_word = remove_punc(main_sentences[0].split(" ")[0])
        if(first_word in follow_words):
            main_sentences.append(main_sentences.pop(0))
        else:
            break
    # quick fix
    if len(main_sentences) < 4:
        for i in range(4-len(main_sentences)):
            main_sentences.append(main_sentences[-1])
    print("EASY PROC FUNCT")
    for i in main_sentences[:4]:
        print("[[["+i)
    return main_sentences[:4]

bpm_of_song = ""
def produce_prompt(primary_emotion, secondary_emotion): # helper leave here
    nouns=["cats","dogs","children","animals","people","penguins","mammoths","trees","sticks","cars","computers","high-schoolers"]
    happy_adj=["content", "energetic","confident","joyous","inspiring","carefree","high spirit","positively attituded"]
    #verb_link=["seem","are","were","have been"]
    quantity=["Those","Three","Two","Multiple","A few","The","A bunch of","A crowd of","Many","A lot of",]
    happy=["contently", "energetically","confidently","joyously","inspiringly","carefreely","in high spirits","with positive attitude"]
    verb_act=["danced","played","sang","whistled","ran","walked","talked","thought","drank","ate","slept"]

    Angry=["Angry"
    "irate",
    "annoyed",
    "cross",
    "vexed"  ,
    "irritated",
    "exasperated",
    "indignant",
    "aggrieved",
    "irked",
    "piqued",
    "displeased",
    "provoked"]
    Fear=[
    "scared",
    "frighful",
    "afraid",
    "fearful",
    "nervous",
    "panicked",
    "agitated",
    "alarmed",
    "worried"]
    Surprised=[
    "surprised",
    "astonished",
    "amazed",
    "nonplused",
    "startled",
    "astounded",
    "stunneded",
    "flabbergasted",
    "staggered",
    "shocked"]
    Sad=[
    "unhappy",
    "sorrowful",
    "dejected",
    "regretful",
    "depressed",
    "downcast",
    "miserable",
    "downhearted",
    "despondent",
    "despairing",
    "disconsolate",
    "out of sorts",
    "desolate",
    "wretched",
    "glum",
    "gloomy",
    "doleful",
    "dismal"    
    ]
    preposition=[
    "Above",
    "Against",
    "Alongside",
    "Among",
    "At",
    "Behind",
    "Below",
    "Beneath",
    "Beside",
    "Between",
    "By",
    "Close to",
    "Far",
    "Far from",
    "From",
    "In",
    "In between",
    "In front of",
    "of",
    "off",
    "on",
    "onto",
    "opposite",
    "over"
    ]
    adverbs={"Angrily":[
    "irately",
    "annoyedly",
    "crossly",
    "vexedly"  ,
    "irritatedly",
    "exasperatedly",
    "indignantly",
    "aggrievedly",
    "irkedly",
    "piquedly",
    "displeasedly",
    "provokedly",
    "galledly",
    "resentfully",
    "furiously",
    "enragedly",
    "infuriatedly",
    "temperously",
    "incensedly",
    "ragingly"],
    "Fear":[
    "scarily"
    "frighfully"
    "afraidedly",
    "fearfully",
    "nervously",
    "panicky",
    "agitately",
    "alarmedly",
    "worrily",
    "intimidatedly",
    "terrifiyingly",
    "petrifiyingly",
    "horrifiyingly",
    "panic-strickenly"],

    "Surprised":[
    "surprisingly",
    "astonishingly",
    "amazingly",
    "nonplused",
    "startlingly",
    "astoundedly",
    "stunningly",
    "flabbergastedly",
    "staggeringly",
    "shockingly",
    "stupefyingly",
    "dumbfoundingly",
    "dazingly",
    "benumbingly"
    ],
    "Sad":[
    "unhappily",
    "sorrowfully",
    "dejectedly",
    "regretfully",
    "depressedly",
    "downcastly",
    "miserablely",
    "downheartedly",
    "down",
    "despondently",
    "despairingly",
    "disconsolate",
    "out of sorts",
    "desolately",
    "bowed down",
    "wretchedly",
    "glum",
    "gloomily",
    "dolefully",
    "dismally",
    "blue",
    "melancholically",
    "low-spiritedly",
    "mournfully",
    "woefully",
    "woebegone",
    "forlorn",
    "crestfallenly",
    "broken-heartedly",
    "heartbrokenly",
    "inconsolably",
    "grief-strickenously",
    ] }
    #quantity+adjective_simple+nouns+verb_link+adjective+prep+quantity+noun
    a=(adverbs["Sad"][random.randint(0,len(adverbs["Sad"])-1)])
    b=(adverbs["Fear"][random.randint(0,len(adverbs["Fear"])-1)])
    c=(adverbs["Angrily"][random.randint(0,len(adverbs["Angrily"])-1)])
    d=(adverbs["Surprised"][random.randint(0,len(adverbs["Surprised"])-1)])
    aa=(random.choice(Sad))
    bb=(random.choice(Fear))
    cc=(random.choice(Angry))
    dd=(random.choice(Surprised))
    hs=(random.choice(happy_adj))
    h=(random.choice(happy))
    i=(random.choice(nouns))
    p=(random.choice(preposition))
    n=(random.choice(nouns))
    t=(random.choice(quantity))
    q=(random.choice(quantity))
    v=(random.choice(verb_act))


    """ Return our prompt(string) base on 1st and 2nd emotion"""
    if primary_emotion=="Positive" and secondary_emotion=="happy":
        return(q+" "+hs+" "+n+" "+h+" "+v+" "+p+" "+t+" "+i, "14-backtrack-lyric-003_happy_85bpm.mp3",85)
    elif primary_emotion=="Positive" and secondary_emotion=="angry":
        return(q+" "+hs+" "+n+" "+c+" "+v+" "+p+" "+t+" "+i, "6-backtrack-lyric-003_angry87bpm.mp3",87)
    elif primary_emotion=="Positive" and secondary_emotion=="fear":
        return(q+" "+hs+" "+n+" "+b+" "+v+" "+p+" "+t+" "+i, "5-backtrack-lyric-005_cool88bpm.mp3",88)
    elif primary_emotion=="Positive" and secondary_emotion=="sad":
        return(q+" "+hs+" "+n+" "+a+" "+v+" "+p+" "+t+" "+i, "3-backtrack-lyric-004_90bpm_confused.mp3",90)
    elif primary_emotion=="Positive" and secondary_emotion=="surprised":
        return(q+" "+hs+" "+n+" "+d+" "+v+" "+p+" "+t+" "+i, "5-backtrack-lyric-005_cool88bpm.mp3",88)
    elif primary_emotion=='Negative'and secondary_emotion=="angry":
        return(q+" "+cc+" "+n+" "+c+" "+v+" "+p+" "+t+" "+i, "1-backtrack-lyric-005_90bpm_cool", 90)
    elif primary_emotion=="Negative" and secondary_emotion=="happy":
        return(q+" "+aa+" "+n+" "+h+" "+v+" "+p+" "+t+" "+i, "7-backtrack-lyric-004_confused90bpm.mp3",90)
    elif primary_emotion=="Negative" and secondary_emotion=="sad":
        return(q+" "+aa+" "+n+" "+a+" "+v+" "+p+" "+t+" "+i, "2-backtrack-lyric-006.90bpm_sad.mp3",90)
    elif primary_emotion=="Negative" and secondary_emotion=="fear":
        return(q+" "+bb+" "+n+" "+b+" "+v+" "+p+" "+t+" "+i, "8-backtrack-lyric-005_chill89bpm.mp3",89)
    elif primary_emotion=="Negative" and secondary_emotion=="surprised":
        return(q+" "+dd+" "+n+" "+d+" "+v+" "+p+" "+t+" "+i, "7-backtrack-lyric-004_confused90bpm.mp3",90)


# # ============================================================
# # Model Generation and lyric generation by Leo and Vincent and some leo :P

# import os
# os.environ['CUDA_LAUNCH_BLOCKING'] = "1"
# import logging
# logging.basicConfig(
#         format="%(asctime)s — %(levelname)s — %(name)s — %(message)s",
#         datefmt="%m/%d/%Y %H:%M:%S",
#         level=logging.INFO
#     )

# import numpy as np



def lookup_word(word_s):
    return cmudict.dict().get(word_s)
def word_syllables(word_s):
    count = 0
    vowels = "aeiouy"
    if(not word_s):
        return 0
    if word_s[0] in vowels:
        count += 1
    for index in range(1, len(word_s)):
        if word_s[index] in vowels and word_s[index - 1] not in vowels:
            count += 1
            if word_s.endswith("e"):
                count -= 1
    if count == 0:
        count += 1
    return count

def censor_sentence(sent):
    cen_sent = better_profanity.profanity.censor(sent).split(" ")
    sent_out = ""
    for i in range(len(cen_sent)):
        if cen_sent[i].find("**")+1:
            sent_out+=cen_sent[i].replace("*",sent.split(" ")[i][0],1)+" "
        else:
            sent_out+=cen_sent[i]+" "
    return sent_out.strip()

def remove_punc(word):
    punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~''' 
    for c in word:
        if c in punc:
            word = word.replace(c,"")
    return word

def total_syllables(sent):
    count = 0
    for w in sent.strip().split(" "):
        w=remove_punc(w)
        count+= word_syllables(w)
    return count

def check_word(word):
    return 0 if dictionary.meaning(word,True) == None else 1

def get_prediction (sent, *args):
    global looper_index
    global rhyming_words
    if args: #ADD PROMPT AT THE BEGINNIGN OF SENTENCE
        sent = args[0] +". "+sent+"."

    token_ids = tokenizer.encode(sent, return_tensors='pt')
    masked_position = (token_ids.squeeze() == tokenizer.mask_token_id).nonzero()
    masked_pos = [mask.item() for mask in masked_position]

    with torch.no_grad():
        output = model(token_ids)

    last_hidden_state = output[0].squeeze()

    list_of_list =[]
    for index,mask_index in enumerate(masked_pos):
        mask_hidden_state = last_hidden_state[mask_index]
        idx = torch.topk(mask_hidden_state, k=4, dim=0)[1]
        mask_words = [tokenizer.decode(i.item()).strip() for i in idx]
        print("MASKWORDS",mask_words)
        numbers = {'1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five',
          '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine', '10': 'ten'}
        for i in range(len(mask_words)):
            if mask_words[i] in numbers:
                mask_words[i] = numbers[mask_words[i]]

        #black_listed = ["synonym"]
        good_words = []
        for word in mask_words:
            if word.replace('\'','').isalpha() and word != "synonym":
                good_words.append(word)
        #put words that don't make sense at the end
        for i in range(len(good_words)):
            if '\'' in good_words[i] or good_words[i] in words.words() or check_word(good_words[i]):
                pass
            else:
                good_words.append(good_words.pop(i))


        looper_index = looper_index+1 if looper_index < min(3,len(good_words)-1) else 0
        try:
            gen_word = good_words[looper_index]
        except:
            list_of_list.append("")
            continue
        
        another_looper = 0
        while not gen_rhyme(gen_word):
            gen_word = good_words[another_looper]
            if(another_looper < len(good_words)-1):
                another_looper += 1
            else:
                print("Couldn't find rhyme")
                break
            
        gen_rhyme(gen_word)

        try:
            list_of_list.append(good_words[looper_index].lower())
        except:
            print(str(looper_index)+"Looper_index error: "+ str(good_words)+" in sent {"+sent+"}")


        for i in range(len(list_of_list)):
            rhyme_inp = list_of_list[i]
            gen_rhyme(rhyme_inp)

    return list_of_list

def gen_rhyme(rhyme_inp):
    parameter = {}
    parameter["rel_rhy"] = rhyme_inp
    try:
        request = requests.get('https://api.datamuse.com/words', parameter) 
        rhyme = request.json()
    except:
        print("REQUEST TO DATAMUSE.COM FAILED")

    try:
        rhyming_words.append(rhyme[0]['word'])#random.randint(0,min(1,len(rhyme)-1)) if you want to randomize
    except:
        return 0
    print("GENERATE RHYME")
    return 1

def next_line(rhyming_words): 
    #append only to the end of the sentence/ not for multiple rhymings
    global next_sentence


    # MUST CHANGE THE APPENDED RHYMING WORDS
    next_sent_words = next_sentence.split(" ")
    try:
        next_sent_words[-1] = rhyming_words[0]
    except:
        print("TRY FAIL: RHYMING WORDS ,"+str(rhyming_words))

    for i in range(-2,-5,-1):
        if(next_sent_words[i] == "," and i==-4):
            break
        next_sent_words[i] = "<mask>"

    next_sentence = " ".join(next_sent_words)

    fill_in_words = get_prediction(next_sentence)
    if len(set(fill_in_words)) != len(fill_in_words):
        next_sentence = next_sentence.replace(' <mask>','',1)

    next_sentence = next_sentence.replace('<mask>',fill_in_words[0],1)

    fill_in_words = get_prediction(next_sentence)
    for word in fill_in_words:
        next_sentence = next_sentence.replace('<mask>',word,1)

    return next_sentence



def process_verse(verse,prompt): # Need at least 4 sentences or error
    global sentence
    global next_sentence
    global rhyming_words
    global looper_index

    prompt_sent = prompt
    looper_index = 0
    verse_out = []

    for i in range(0,4,2):
        rhyming_words = []

        sentence = verse[i].strip() + " "
        next_sentence = verse[i+1].strip() + " "
        #Add <mask> label
        sentence = add_mask_label(sentence) #good

        masked_word = get_prediction(sentence,prompt_sent)
        verse_out.append(sentence.replace('<mask>',masked_word[0]))

        verse_out.append(next_line(rhyming_words))

#     for i in range(len(verse_out)):
#         verse_out[i] = censor_sentence(verse_out[i])

    return verse_out


#NOT USING
def generate_lyrics(output,generated_prompt):
    """
        :param: str, str
    """
    
    #while True:
    sent_list = output.split("\n")

    main_sentences = []
    for sent in sent_list:
        if(sent):
            syllables = total_syllables(sent)
        else:
            syllables = 0

        if(10 < syllables and syllables < 14):
            main_sentences.append(sent)


    follow_words = ["and","but"]
    for i in range(len(main_sentences)):
        first_word = remove_punc(main_sentences[0].split(" ")[0])
        if(first_word in follow_words) or (random.random() > 0.35 and better_profanity.profanity.contains_profanity(main_sentences[i])):
            main_sentences.append(main_sentences.pop(0))
        else:
            break

#     for i in range(len(main_sentences)):
        
    #UP TO HERE IN EZ POSTPROC

    if len(main_sentences) >= 4:
        print("Generate Done")
        return process_verse(main_sentences[:4],generated_prompt)
    
    #End of while true

    if len(main_sentences) < 4:
        print("need more lines:")
        return process_verse(main_sentences[:4],generated_prompt)#(NO RECURSION FOR NOW) generate_lyrics(generated_prompt)
    else:
        return process_verse(main_sentences[:4],generated_prompt)



    #LYRICS TO MP3 AUDIO FILE by Vincent

def create_mp3_files(inp_lyrics, bpm_of_song):
    
#     emotion_songs = {"cool":["/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/1-backtrack-lyric-005_90bpm_cool.mp3",
#                             "/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/4-backtrack-lyric-003_cool86bpm.mp3",
#                             "/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/5-backtrack-lyric-005_cool88bpm.mp3"],
#                      "confused":["/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/3-backtrack-lyric-004_90bpm_confused.mp3",
#                                 "/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/7-backtrack-lyric-004_confused90bpm.mp3"],
#                      "angry":["/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/6-backtrack-lyric-003_angry87bpm.mp3",
#                              "/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/12-backtrack-lyric-002_92bpm_angry.mp3"],
#                      "chill":["/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/8-backtrack-lyric-005_chill89bpm.mp3",
#                              "/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/10-backtrack-lyric-006_chill_80bpm.mp3",
#                              "/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/13-backtrack-lyric-001_88bpm_chill.mp3",
#                              "/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/13-backtrack-lyric-001_88bpm_chill.mp3"],
#                      "sad":["/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/2-backtrack-lyric-006.90bpm_sad.mp3",
#                            "/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/9-backtrack-lyric-003_sad80bpmbpm.mp3",
#                            "/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/11-backtrack-lyric-002_sad_80bpm.mp3"],
#                      "happy":["/projects/ab6b9f32-4b18-411a-bce3-bf454bdd198d/omni_nlp/app/static/14-backtrack-lyric-003_happy_85bpm.mp3"]}

#     song_bpm=[90,90,90,86,88,87,90,89,80,80,80,88,88,85]
    four_bars_total = '"' +str(int((240/bpm_of_song) * 1000)) + 'ms">' #60seconds*4 beats = 240 cross multiply
    unused_time = str(0) + 'ms"'

    syllables = []
    for line in inp_lyrics:
        syllables.append(total_syllables(line))

    polly_client = boto3.Session(
            aws_access_key_id= '',
            aws_secret_access_key='', #CHANGE THIS SO VINCENT DOESN'T GET CHARGED o_O
            region_name='us-west-2').client('polly')

    for i in range(4): 
        Lyrics  = '''<speak>
                <break time="''' + unused_time +  '''/>
                <prosody amazon:max-duration=''' + four_bars_total + inp_lyrics[i] + '''</prosody>
            </speak>'''

        response = polly_client.synthesize_speech(
                VoiceId='Joey',
                OutputFormat='mp3',
                Text = Lyrics,
                Engine = 'standard',
                TextType = "ssml",
        )
        one_syllable = int((240/bpm_of_song) * 1000)/23
        unused_time = str((15-syllables[i])*one_syllable) + 'ms"'

        file = open('tts_line_'+ str(i) + '.mp3', 'wb') # might need to change to {{url_for}}
        file.write(response['AudioStream'].read())
        file.close()
        
    
#audio clips path is a list of paths
    audio_clip_paths = ["tts_line_0.mp3", "tts_line_1.mp3","tts_line_2.mp3","tts_line_3.mp3"]

    clips = [AudioFileClip(c) for c in audio_clip_paths]
    final_clip = concatenate_audioclips(clips)
    final_clip.write_audiofile("./static/audio/final.mp3")
    



def add_mask_label(sent):
    words = sent.strip().split(" ")
    if len(words) > 1:
        words[-1] = "<mask>"
    return " ".join(words)

