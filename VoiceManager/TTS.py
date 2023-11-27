import os, time, csv #, sys
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import AudioDataStream
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from XML import XML
from translator import translator
from sentiment import sentiment

## LICENSES
with open('..\\..\\AzureKeys.txt') as f:
    lines = [line.rstrip() for line in f]
# Voice Service API key
speech_key = str(lines[0]) #sys.argv[1]
# Translator Service API key
translator_key = str(lines[1]) #sys.argv[2]
# Language Service Api key
sentiment_key = str(lines[2]) #sys.argv[3]

# SSML Generator
XML = XML()
# Tanslator Service Init
Translator = translator(translator_key)
# Language
Sentiment = sentiment(sentiment_key)

## Variable initialization
lang = 'es-ES'
duration = 1.0
length = 0.0
priority = False

# Service configuration
service_region = "westeurope"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Standard configuration, but then it is applied with different languages
speech_config.speech_synthesis_language = "en-US" 
speech_config.speech_synthesis_voice_name ="en-US-JennyMultilingualNeural"
# Audio output configuration
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
#audio_config = speechsdk.AudioConfig(use_default_microphone=False, filename = "Response/response.wav")
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config,audio_config=audio_config)

while True:      
    time.sleep(1)  
    if os.path.exists('..\\speech.csv'):            
        with open('..\\speech.csv','r') as f:            
            csv_reader = csv.DictReader(f)
            for row in csv_reader:         
                print("--------------------------------------------------------")
                if(str(row['action'])=="say"): 
                    start_time = time.time()     
                    print("Status: Say")
                    # Sentence
                    contents = str(row['response'])
                    # Emotional tag
                    emotion = str(row['emotion'])                   
                    # Animation
                    body_anim = str(row['animation'])   
                    # Emotional tag for Azure
                    emotionAzure = str(row['emotionAzure'])     
                    # multimedia content
                    video = str(row['video'])
                    # multimedia content
                    length = float(row['length']) 
                    # Language
                    lang = str(row['language'])
                    # Avatar
                    avatar = str(row['avatar'])
                    sentiment_analysis = Sentiment.sentiment(contents,lang)
                    # Polarity
                    emo_value = sentiment_analysis
                    # XML - SSML generator               
                    if lang == 'es-ES' or lang == 'eu-ES': ## Spanish or Basque 
                        text_trans = contents
                        XML.esXML(contents,emotion,lang,sentiment_analysis,avatar)
                    elif lang == 'en-US': ## English Emotional
                        # Sentence translation
                        text_trans = Translator.translator(contents,'es',lang[0:2])
                        XML.enSSML(text_trans,emotionAzure,lang)       
                    # Reading SSML file
                    ssml_string = open("Response/respuesta.xml", "r+", encoding="utf-8").read()
                    # Audio generated
                    result = speech_synthesizer.speak_ssml_async(ssml_string).get()
                    # Audio memory stream to file
                    stream = AudioDataStream(result)
                    time_per_phrase = (time.time() - start_time)
                    print("Time per phrase = %s seconds " % time_per_phrase)
                    #stream.save_to_wav_file("Response/respuesta.wav")
                    # Checking the result
                    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                        duration = result.audio_duration.total_seconds()                      
                        print("Virtual personal trainer: {} <{}>".format(text_trans,emotion))
                        print("Audio duration: {} seconds.".format(duration))
                        print("Processing time per phrase = %s seconds " % (time_per_phrase-duration))
                    elif result.reason == speechsdk.ResultReason.Canceled:
                        cancellation_details = result.cancellation_details
                        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
                        if cancellation_details.reason == speechsdk.CancellationReason.Error:
                            print("Error details: {}".format(cancellation_details.error_details))                    
                elif(str(row['action'])=="listen"):
                    archi1 = open("listening.txt","w") 
                    archi1.close()                     
                    print("Status: Listen")
                elif(str(row['action'])=="watch"):
                    output = open("..//..//Kinect.txt","w")
                    lines = [str(row['response'])]
                    output.write('\n'.join(lines))
                    output.close()
                    print("Accion: reconocer zona")
                elif(str(row['action'])=="interface"):
                    output = open("..//..//Interface.txt","w")
                    lines = [str(row['response'])]
                    output.write('\n'.join(lines))
                    output.close()
                    print("Accion: abrir interface")
        os.remove('..\\speech.csv')        
        
