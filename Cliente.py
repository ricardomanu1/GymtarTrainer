import websocket
import json
import os,time,csv

# Crea una conexión WebSocket al servidor
ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:5059/")  # Asegúrate de que la dirección y el puerto coincidan

# Define el ID del cliente (puedes asignar un ID único)
client_id = 2

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
            for row in csv_reader:         
                print("--------------------------------------------------------")
                if(str(row['action'])=="say"): 
                    content = str(row['response'])
                    print("VINETbot: {}".format(content))
                    send_message(content, recipient=1) # En este caso, el destinatario es el cliente 1
                    time.sleep(2)
        f.close()
        os.remove('speech.csv')   
