import requests
import json

class interaction_manager(object):
    def __init__(self):
        self.url_R = 'http://127.0.0.1:5005/webhooks/myio/webhook'
        self.url_U = 'http://127.0.0.1:5010/toUnreal'

# Rasa
    def say(self,text,lang,emotion,polarity):
        r = requests.post(self.url_R, json={
        "sender": "Vinet_user",
        "message": "{}".format(text),
        "metadata": {"event":"say","emotion":"{}".format(emotion),"language":"{}".format(lang),"polarity":"{}".format(polarity)} 
        })

    def know(self,text,var,value):
        if var == 'people':
            r = requests.post(self.url_R, json={
            "sender": "Vinet_user",
            "message": "{}".format(text),
            "metadata": {"event":"know","people":value} 
            })
        elif var == 'chapter':
            r = requests.post(self.url_R, json={
            "sender": "Vinet_user",
            "message": "{}".format(text),
            "metadata": {"event":"know","zone":value} 
            })
        elif var == 'emotion':
            r = requests.post(self.url_R, json={
            "sender": "Vinet_user",
            "message": "{}".format(text),
            "metadata": {"event":"know","emotion":value} 
            })

    def know(self,text):
        r = requests.post(self.url_R, json={
            "sender": "Vinet_user",
            "message": "{}".format(text),
            "metadata": {"event":"know"} 
            })
# Unreal
    def toUnreal(self,text):
        try:
            data = {"Text": text, "key2": "value2"}
            # Convierte los datos a formato JSON
            json_data = json.dumps(data)
            # Configura el encabezado de la solicitud para indicar que estás enviando JSON
            headers = {'Content-Type': 'application/json'}
            r = requests.post(self.url_U, data=json_data, headers=headers)
            #r = requests.post(self.url_U, data=data)
            '''
            r = requests.post(self.url_U, json={
                "sender": "Vinet_user",
                "message": "{}".format(text),
                "metadata": {"event":"know"} 
                })
            '''
            # Verifica el código de estado de la respuesta
            if r.status_code == 200:
                print("Solicitud exitosa. Respuesta del servidor:", r.text)
            else:
                print("Error en la solicitud. Código de estado:", r.status_code)
        except requests.exceptions.ConnectionError as e:
            print("Error de conexión:", e)
        except Exception as e:
            print("Error general:", e)

    def tts(self):
        r = requests.get('http://127.0.0.1:5005/webhooks/myio')
        print(r.json())
        return r.json()

    def stt(self,text):
        r = requests.post('http://localhost:5055/webhooks', json={
        "sender": "Vinet_user",
        "message": "{}".format(text),
        "metadata": {"event":"know"} 
        })




