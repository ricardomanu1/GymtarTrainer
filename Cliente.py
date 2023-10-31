import websocket
import json
import os,time,csv

# Crea una conexión WebSocket al servidor
ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:5059/")  # Asegúrate de que la dirección y el puerto coincidan

# Define el ID del cliente (puedes asignar un ID único)
client_id = 2
content_list = [] 
content_joined = [] 

# Función para enviar un mensaje al servidor
def send_message(content, recipient):
    message = {
        "sender": "Rasa",
        "sender_id": client_id,
        "message": content,
        "metadata": {"event":"say"}
    }
    if recipient is not None:
        message["recipient"] = recipient
    ws.send(json.dumps(message))

while True:
    time.sleep(1)
    if os.path.exists('speech.csv'):
        with open('speech.csv','r') as f:            
            csv_reader = csv.DictReader(f)
            print("--------------------------------------------------------")
            for row in csv_reader:         
                
                if(str(row['action'])=="say"): 
                    content = str(row['response'])
                    content_list.append(content)
                    #print("VINETbot: {}".format(content))
                    #send_message(content, recipient=1) # En este caso, el destinatario es el cliente 1
                    #time.sleep(2)
            #content_joined = " ".join(content_list)
            content_joined = " ".join([frase + '.' if not frase.endswith('.') else frase for frase in content_list])
            print("VINETbot: {}".format(content_joined))
            send_message(content_joined, recipient=1)
        content_list = []
        content_joined = []
        f.close()
        os.remove('speech.csv')   
