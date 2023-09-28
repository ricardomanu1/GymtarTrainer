import csv, json, os, typing
from pickle import NONE
import datetime as dt
import xml.etree.cElementTree as ET
import numpy as np

from EBDI.emotions_manager import emotions_manager
from EBDI.belief_manager import belief_manager
from EBDI.desires_manager import desires_manager
from EBDI.intents_manager import intents_manager 

from DDBB.SQL import database 

from os import listdir
from typing import Any, Text, Dict, List

from rasa_sdk import events
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, BotUttered, UserUttered, EventType
from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLReader
from rasa.shared.nlu.training_data.loading import load_data

if typing.TYPE_CHECKING:
    from rasa_sdk.trackers import DialogueStateTracker
    from rasa_sdk.dispatcher import Dispatcher
    from rasa_sdk.domain import Domain

# Variables globales
user_intent = ''
count = 0
Bi = ''
Be = ''
lang = 'es-ES'
polarity = 0
inter1 = False
date = ''

## Kinect
watch = False
watchResponse = ''

## Interface
interface = False
interfaceResponse = ''

## Database
routine_say = False
exercises = []

# Gestor EBDI
Emotions = emotions_manager()
Beliefs = belief_manager()
Desires = desires_manager()        
Intents = intents_manager()
context = Intents.get_context()


# Memoria del Bot
slot_name = ''
slot_data = 'nodata'
slot_daytime = ''
slot_rol = ''
slot_avatar = 'Carlos'
id_user = 0
user_rutine = []
ejercicio = ''
slot_user = 0
avatar = 'm'
contenido_user = []

# DDBB
db = database()
db.connection()

# Methods
def __init__(self):
    self.agent_id = 'actions'

# Number of responses
def contador():    
    global count
    count = count + 1
    return []

# Last event that has been generated to capture the response that has been selected from the Domain file
def get_latest_event(events):    
    latest_actions = []
    for e in events:
        if e['event'] == 'bot':
            latest_actions.append(e)
    return latest_actions

# Time of day
def part_of_day(x):    
    if (x > 4) and (x <= 12 ):
        return 'morning'
    elif (x > 12) and (x <= 16):
        return'afternoon'
    elif (x > 16) and (x <= 24) :
        return 'evening'
    elif (x > 24) and (x <= 4):
        return'none'

# The day in spanish
def the_day(x):
    if x == "Monday":
        return 'lunes'
    if x == "Tuesday":
        return 'martes'
    if x == "Wednesday":
        return 'miercoles'
    if x == "Thursday":
        return 'jueves'
    if x == "Friday":
        return 'viernes'
    if x == "Saturday":
        return 'sabado'
    if x == "Sunday":
        return 'domingo'

## Estructura BOT
class ChatBot(Action):
    def name(self) -> Text:
        return "chatbot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        # Acceso a variables globales
        global Bi
        global Be
        global lang
        global polarity
        global avatar
        global inter1
        global date

        global slot_name
        global slot_daytime
        global slot_rol
        global slot_avatar
        global slot_data
        global slot_ejercicio
        global id_user
        global user_rutine
        global ejercicio
        global db

        print("--------------------------------------------------------------------------------------------")
        
        inter1 = True

        ## Actualizacion de fecha
        now = dt.datetime.now()
        date = now.strftime("%Y-%m-%d")
        
        ## Valores de entrada, si es un texto
        intent = tracker.latest_message['intent']
        text = tracker.latest_message['text']
        entities = tracker.latest_message['entities']
        metadata = tracker.latest_message['metadata']  

        Bi = intent['name']
        id_event = metadata['event']
        
        slot_ejercicio = tracker.get_slot('ejercicio')
        
        ## Slots: Almacenado en memoria
        slot_avatar = tracker.get_slot('avatar') ## cuando entra una entidad            
        slot_daytime = part_of_day(int(f"{dt.datetime.now().strftime('%H')}"))     

        # Entities:
        for e in entities:
            print("entidad: {} = {}".format(e['entity'],e['value']))

        # Metadata:
        for key, value in metadata.items():
            print(key, value)
            if 'id' in metadata:
                id_user = metadata['id']       
            if 'ejercicio' in metadata:
                ejercicio = metadata['ejercicio'] 
                slot_ejercicio = ejercicios_lista[ejercicio] #NO SE ALMACENA EN LA PRIMERA ITERACION
                ## POSIBILIDADE DE METER UNA FRASE ANTES (ALTA PRIORIDAD)

        ## Metadata: Voice input     
        if (id_event == 'say'):
            if 'emotion' in metadata:
                Be = metadata['emotion']            
            if 'language' in metadata:
                lang = metadata['language']
            if 'polarity' in metadata:
                polarity = metadata['polarity']                  
            if Bi not in context:
                Bi = 'out_of_scope'
            user_event = [id_event,Bi,Be,text,slot_name,entities,lang,polarity] 
            print('EVENT: ' + str(user_event))
            EBDI.run(self, dispatcher, tracker, domain, user_event)                
                
        ## Entradas de conocimiento
        elif (id_event == 'know'):
            objInterest = None                    
            user_event = [id_event,text,objInterest,'']             
            print('EVENT: ' + str(user_event)) 
            if text in context:
                EBDI.run(self, dispatcher, tracker, domain, user_event)
            else:
                print('No se que hacer con este conocimiento.')
                
        ## Entrada de acciones a realizar
        elif (id_event == 'do'):
            print('Ahora lo hago')
        else:
            print('Comando no conocido')            

        ## comprobacion del diccionario de sinonimos de entidades
        synonyms_dict = Dictionary.get_synonym_mapper()
        for value, synonyms in synonyms_dict.items():
            ## print("Value:", value)
            ## print("Synonyms:", str(synonyms))
            Ricardo_synonyms = synonyms      
        
        return [SlotSet("daytime", slot_daytime),
                SlotSet("data", slot_data),
                SlotSet("rol", slot_rol),
                SlotSet("avatar", slot_avatar),
                SlotSet("ejercicio", slot_ejercicio)]

## Estructura EBDI
class EBDI(Action):

    def name(self) -> Text:
        return "ebdi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
            user_event) -> List[Dict[Text, Any]]:          
        ## Conjunto E B D I
        global Emotions
        global Beliefs
        global Desires
        global Intents 
        global inter1

        Beliefs.inter = inter1
        inter1 = False
        print(Beliefs.inter)
        # Establecen las nuevas creencias a partir del evento
        newBelief = Beliefs.new_belief(user_event)     
        
        Beliefs.del_belief(Emotions.estado)
        for e in Beliefs.emotionalBeliefs:
            Beliefs.del_belief(e)
        # Primera gestion del estado emocional
        E1 = Emotions.euf1(Intents,newBelief)
        print('PRIMARY EMOTION: ' + E1) 
        
        newBelief.append(['know',E1,True])        

        # BDI actualizacion        
        BDI.bdi(self,newBelief)             

        # Segunda gestion del estado emocional
        E2 = Emotions.euf2(Intents,Beliefs)
        print('SECONDARY EMOTION: ' + E2) 

        #if (inTime and E1 != E2):
        #   BDI.bdi(self,Beliefs.agent_beliefs)

        print('ACTIONS:') 
        p = Plan.plan(self, Intents.agent_intents)  
        if Intents.agent_intents:
            del Intents.agent_intents[0]
            
        for i in p:
            print('--->' + i)
            exec(i) 

        return []

# actualizacion Beliefs Desires Intents
class BDI:

    def bdi(self,newBelief):     
        ## Conjunto E B D I
        global Emotions
        global Beliefs
        global Desires
        global Intents 

        #B = brf_in(E,I,Bm) # se actualizan las creencias
        Beliefs.brf_in(Emotions,Intents,newBelief)
        print('BELIEFS:')
        for belief in Beliefs.agent_beliefs:
            print(" -", belief[0], belief[1], belief[2])

        #D = options(B,I) # se crean los deseos
        Desires.options(Beliefs,Intents)
        print('DESIRES:')
        for desire in Desires.agent_desires:
            print(" -", desire[0], desire[1], desire[2])     

        #I = filterI(E,B,D,I)
        Intents.filterI(Emotions,Beliefs,Desires.agent_desires)
        print('INTENTS:')
        for intent in Intents.agent_intents:
            print(" -", intent)

        # se estan manteniendo deseos, asi que esta linea los elimina, pero... ¿se pueden mantener deseos?
        Desires.agent_desires = [] 

        return []

class Plan:

    def plan(self, Intents):
        p = []    
        for intent in Intents:
            for idx, val in enumerate(intent):    
                # Seleccionamos la primera intencion y las acciones correspondientes        
                if val == 'a_say':  
                    resp = intent[idx+1]
                    s = "Say.run(self, dispatcher, tracker, domain,'{0}')".format(str(resp))
                    p.append((s))

                if val == 'a_nB':
                    user_event = ['say',intent[idx+1],'none','','','','']   
                    s = "EBDI.run(self, dispatcher, tracker, domain,{0})".format(user_event)
                    p.append((s))

                if val == 'a_dB':
                    s = "Beliefs.del_belief('{0}')".format(str(intent[idx+1]))
                    p.append(s)

                if val == 'a_fB':
                    s = "Beliefs.fulfill_belief('{0}')".format(str(intent[idx+1]))
                    p.append(s)

                if val == 'a_rB':
                    s = "Beliefs.reset_beliefs()"
                    p.append(s)

                # solicitud de camara
                if val == 'ki':
                    s = "Kinect.name('{0}')".format(str(intent[idx+1]))
                    p.append(s)
                # solicitud de interfaz
                if val == 'in':
                    s = "Interface.name('{0}')".format(str(intent[idx+1]))
                    p.append(s)
                # solicitud de base de datos
                if val == 'db':
                    s = "Database.name('{0}')".format(str(intent[idx+1]))
                    p.append(s)
                # 
                if val == 'co':
                    s = "Coach.name('{0}')".format(str(intent[idx+1]))
                    p.append(s)
        return p

## Acciones ##
class Say(Action):

    def name(self) -> Text:
        return "say"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
            resp) -> List[Dict[Text, Any]]:
        hours = str(f"{dt.datetime.now().strftime('%H:%M')}")
        day = the_day(str(f"{dt.datetime.now().strftime('%A')}"))             

        dispatcher.utter_message(
            response = resp,           
            hours = hours,
            day = day,
            daytime = slot_daytime,
            name = slot_name,
            rol = slot_rol,
            data = slot_data,
            avatar = slot_avatar)

        contador()
        print("dispatcher: " + str(count))           
        tracker.get_slot('daytime')
        tracker.get_slot('rol')
        tracker.get_slot('avatar')
        tracker.get_slot('data')


        return []

## Generar los ficheros de salida
class To_Speech(Action):

    def name(self) -> Text:
        return "to_speech"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
            ) -> List[Dict[Text, Any]]:
        global msg
        global count   
        global Emotions        

        print('----RESPONSES----')  
        tracker.get_slot('daytime') 
        tracker.get_slot('rol') 
        tracker.get_slot('data') 

        if count > 0:
            msg = get_latest_event(tracker.applied_events())     
            responses = msg[-count:]  
            CSV().name(responses) 
        count = 0

        return []

class Kinect():
    def name(response):
        global watch
        global watchResponse
        watch = True
        watchResponse = response
        return "echo"

class Interface():
    def name(response):
        global interface
        global interfaceResponse
        interface = True
        interfaceResponse = response
        return "echo"

class Database():
    def name (response):
        global id_user
        global slot_name
        global slot_rol        
        global slot_data 
        global slot_user 
        if response == "login":
            contenido_user = getattr(db, response)(id_user,127)
            if contenido_user is not None:
                slot_name = contenido_user['name']
                slot_rol = contenido_user['rol']
                slot_user = id_user
        if response == "select_routine" :           
            now = dt.datetime.now()
            date = now.strftime("%Y-%m-%d")
            contenido_user = getattr(db, "select_routine")(slot_user,date)
            if contenido_user is not None: 
                Database.routine(contenido_user)
                slot_data = "data"
            else:
                print("No hay datos para esta fecha")
                slot_data = "nodata"
        if response == "select_next_routine" :           
            now = dt.datetime.now()
            next_day = now + dt.timedelta(days=1)
            date = next_day.strftime("%Y-%m-%d")
            contenido_user = getattr(db, "select_routine")(slot_user,date)
            if contenido_user is not None: 
                Database.routine(contenido_user)
                slot_data = "data"
            else:
                print("No hay datos para esta fecha")
                slot_data = "nodata"
        if response == "select_previous_routine" :           
            now = dt.datetime.now()
            previous_day = now - dt.timedelta(days=1)
            date = previous_day.strftime("%Y-%m-%d")
            contenido_user = getattr(db, "select_routine")(slot_user,date)
            if contenido_user is not None: 
                Database.routine(contenido_user)
                slot_data = "data"
            else:
                print("No hay datos para esta fecha")
                slot_data = "nodata"
        print("slot_name: " + str(slot_name))
        print("slot_rol: " + str(slot_rol))
        print("slot_data: " + str(slot_data))
        print("slot_user: " + str(slot_user))
        return "echo"

    def routine(contenido_user):
        global routine_say
        global exercises
        exercises = []
        routine_say = True        
        print(contenido_user)       
        e = contenido_user['ejercicios']
        e_array = [int(x) for x in e.split(",")]
        r = contenido_user['repeticiones']        
        r_array = [int(x) for x in r.split(",")]
        t = contenido_user['tiempos']        
        t_array = [int(x) for x in t.split(",")]
        select_exercise = "select_exercise"
        for i in range(len(e_array)):                   
            e_name = getattr(db, select_exercise)(e_array[i])
            if r_array[i] != 1:
                new_string = "{} con {} repeticiones de {} segundos.".format(
                e_name['name'],r_array[i],t_array[i])
            else:
                new_string = "{} con {} repetición de {} segundos.".format(
                e_name['name'],r_array[i],t_array[i])
            exercises.append(new_string)
        
    def login(user_id,user_pass):
        global slot_name
        global slot_rol
        global slot_user        
        contenido_user = getattr(db, "login")(user_id,user_pass)
        if contenido_user is not None:
            slot_name = contenido_user['name']
            slot_rol = contenido_user['rol']
            slot_user = user_id        
        print("Usuario: " + str(slot_name))

    def routine_today(user_id):
        global slot_data
        global contenido_user
        global date
        global user_rutine
        now = dt.datetime.now()
        date = now.strftime("%Y-%m-%d")
        contenido_user = getattr(db, "select_routine")(slot_user,date)
        if contenido_user is not None: 
            #Database.routine(contenido_user)
            slot_data = "data"
            print("Tenemos datos para hoy")
            print("Rutina: " + str(contenido_user))
            user_rutine = contenido_user
            return True
        else:
            print("No hay datos para hoy")
            slot_data = "nodata"
            return False

    def exercises_today(exercises_id):
        exercises = getattr(db, "select_exercises")(exercises_id)
        if exercises is not None: 
            return exercises
        else:
            return None


class Coach():
    def name (response):
        global slot_avatar
        slot_avatar = "m"
        print("Cambio de Voz")

## Salida de las respuestas csv
class CSV():
    def name(self,responses):
        global watch, watchResponse
        global interface, interfaceResponse
        global routine_say, exercises
        output_csv = open('speech.csv','w+',newline='')
        writer = csv.writer(output_csv, delimiter =',')
        writer.writerow(['action','response','emotion','language','animation','emotionAzure','video','length','avatar'])
        animation_tag = 'informar'  
        video = ''  
        length = 0
        for response in responses:
            if 'metadata' in response['metadata']:
                if 'subtext' in response['metadata']['metadata']:
                    animation_tag = str(response['metadata']['metadata']['subtext'])
                else:
                    animation_tag = 'informar'
                if 'img' in response['metadata']['metadata']:
                    video = str(response['metadata']['metadata']['img'])
                else:
                    video = ''
                if 'length' in response['metadata']['metadata']:
                    length = float(response['metadata']['metadata']['length'])
                else:
                    length = 0
            print(' -' + str(response['text']))
            writer.writerow(['say',str(response['text']), str(Emotions.estado),lang,animation_tag,str(Emotions.tag()),str(video),length,avatar])
        if(watch):
            writer.writerow(['watch',str(watchResponse)])
            watch = False
        elif(interface):
            writer.writerow(['interface',str(interfaceResponse)])
            interface = False
        elif(routine_say):
            for exercise in exercises:
                writer.writerow(['say',str(exercise), str(Emotions.estado),lang,animation_tag,str(Emotions.tag()),str(video),length,avatar])
            routine_say = False
            writer.writerow(['listen'])
        else:
            writer.writerow(['listen'])
        output_csv.close()

## Se ejecuta una sola vez al principio de una conversacion
class Dictionary:

    def get_synonym_mapper():
        result_dict = {}
        for nlu_md in os.listdir("data"):
            if nlu_md == 'nlu.md':
                path_md = "data/{0}".format(nlu_md)
                nlu_md_file = load_data(path_md)
                nlu_md_json = nlu_md_file.nlu_as_json()
                for item in json.loads(nlu_md_json)['rasa_nlu_data']['entity_synonyms']:
                    result_dict[item['value']] = item['synonyms']
        return result_dict

class Aprendizaje(Action):

    def name(self) -> Text:
        return "aprendizaje"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        entities = tracker.latest_message['entities']
        intent = tracker.latest_message['intent']
        text = tracker.latest_message['text']
        print(intent)
        print(entities)        
        print(text)
        message = "Comando de aprendizaje"
        dispatcher.utter_message(text=message)
        for e in entities:
            if e['entity'] == 'name':
                name = e['value']
            if name == "ricardo":
                message = "Hola Ricardo, estoy listo para aprender"
                '''a = tracker.'''
            if name != "ricardo":
                message = "Lo siento, no estas autorizado"     
        dispatcher.utter_message(text=message)
        return []
    
Database.login("101","127")
if(Database.routine_today("101")):
    user_event = ['know','with_routine',True]
    ejercicios_id = [int(x) for x in user_rutine['ejercicios'].split(',')]
    ejercicios_lista = Database.exercises_today(ejercicios_id)
    print(user_rutine)
    print(ejercicios_id)
    print(ejercicios_lista)
else:
    user_event = ['know','without_routine',True]   
Beliefs.agent_beliefs.append(user_event)
slot_daytime = part_of_day(int(f"{dt.datetime.now().strftime('%H')}"))   