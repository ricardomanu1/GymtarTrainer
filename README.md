# GYMTAR
training avatar
## Instalaci�n con Anaconda
```
conda create -n gymtarbot python==3.8
conda activate gymtarbot
conda install ujson
conda install tensorflow
pip install rasa
pip install --upgrade rasa==2.8.0
```
## Instalaci�n del componente para fragmentar texto en espa�ol
```
pip3 install rasa[spacy]
python -m spacy download es_core_news_md
```
## Instalaci�n del componente sentiment
```
pip install nltk
```
## Instalaci�n de base de datos
```
conda install -c anaconda mysql-connector-python
```
## Antes de realizar la ejecuci�n, mirar la configuracion personalizada

# Ejecuci�n con API 
## Consola 1 (Desde el fichero GYMTAR)
```
rasa run -m models --enable-api --credentials credentials.yml --debug
```
## Consola 2 (Desde el fichero GYMTAR)
```
rasa run actions
```
# Construcci�n de los mensajes Json
## Direcci�n de mensajes Json:
http://localhost:5005/webhooks/myio/webhook

## Ejemplo de mensaje 'saludar' Json
```ruby
{
    "sender": "Gymtar_user",
    "message": "Hola",
    "metadata": {"event":"say","sentiment":"isHappy","language":"es-ES"} 
}
```
### Mas ejemplos en inputs.txt

# Configuraciones personalizadas 
## Tras descargar el proyecto es necesario realizar un entrenamiento
## Rasa Train
```
rasa train --domain domains
```
## Voice manager
### Solo almacena algunos scripts para otra secci�n que usa Azure para incorporar la voz, ver al final.

## Uso con OpenSmile
Pregunta: �Qu� tal estas?<br/>
El Json con el mensaje tambi�n tiene que llevar una de las siguientes emociones:<br/>
['isHappy','isSad','isFear','isAnger','isSurprise','isBored','isAnxious','isLonely','isTired']<br/>
El sistema actualmente esta actuando con un gestor de emociones espejo, si pregunto mientras estoy feliz (isHappy),
me contesta estando feliz (Happy), de la misma manera, si estoy triste (isSad), me responde estando triste (Sad)<br/>
La salida textual: speech.txt

# Ejemplos Json con emociones:
## input:
```ruby
{
    "sender": "Gymtar_user",
    "message": "�Qu� tal estas?",
    "metadata": {"event":"say","sentiment":"isHappy","language":"es-ES"}
}
```
## output:
	Me siento genial. (happy)
## input:
```ruby
{
    "sender": "Gymtar_user",
    "message": "�Qu� tal estas?",
    "metadata": {"event":"say","sentiment":"isSad","language":"es-ES"}
}
```
## output:
	Muy triste. (sad)

# Ejecuci�n usando Azure
## Instalaci�n Azure 
```
pip install keyboard
pip install azure-cognitiveservices-speech
```
## Instalaci�n del componente sentiment Azure
```
pip install azure-ai-textanalytics
```
# Ejecuci�n con Azure 
## Consola 3 (Dentro del fichero VoiceManager)
```
python STT.py
```
## Consola 4 (Dentro del fichero VoiceManager)
```
python TTS.py
```
## Requiere un documento AzureKey.txt con el siguiente contenido:
VoiceServiceKey<br/> TranslatorServiceKey<br/> LanguageKey<br/>
"# GymtarTrainer" 
