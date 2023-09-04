# GYMTAR
training avatar
## Instalación con Anaconda
```
conda create -n gymtarbot python==3.8
conda activate gymtarbot
conda install ujson
conda install tensorflow
pip install rasa
pip install --upgrade rasa==2.8.0
```
## Instalación del componente para fragmentar texto en español
```
pip3 install rasa[spacy]
python -m spacy download es_core_news_md
```
## Instalación del componente sentiment
```
pip install nltk
```
## Instalación de base de datos
```
conda install -c anaconda mysql-connector-python
```
## Antes de realizar la ejecución, mirar la configuracion personalizada

# Ejecución con API 
## Consola 1 (Desde el fichero GYMTAR)
```
rasa run -m models --enable-api --credentials credentials.yml --debug
```
## Consola 2 (Desde el fichero GYMTAR)
```
rasa run actions
```
# Construcción de los mensajes Json
## Dirección de mensajes Json:
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
### Solo almacena algunos scripts para otra sección que usa Azure para incorporar la voz, ver al final.

## Uso con OpenSmile
Pregunta: ¿Qué tal estas?<br/>
El Json con el mensaje también tiene que llevar una de las siguientes emociones:<br/>
['isHappy','isSad','isFear','isAnger','isSurprise','isBored','isAnxious','isLonely','isTired']<br/>
El sistema actualmente esta actuando con un gestor de emociones espejo, si pregunto mientras estoy feliz (isHappy),
me contesta estando feliz (Happy), de la misma manera, si estoy triste (isSad), me responde estando triste (Sad)<br/>
La salida textual: speech.txt

# Ejemplos Json con emociones:
## input:
```ruby
{
    "sender": "Gymtar_user",
    "message": "¿Qué tal estas?",
    "metadata": {"event":"say","sentiment":"isHappy","language":"es-ES"}
}
```
## output:
	Me siento genial. (happy)
## input:
```ruby
{
    "sender": "Gymtar_user",
    "message": "¿Qué tal estas?",
    "metadata": {"event":"say","sentiment":"isSad","language":"es-ES"}
}
```
## output:
	Muy triste. (sad)

# Ejecución usando Azure
## Instalación Azure 
```
pip install keyboard
pip install azure-cognitiveservices-speech
```
## Instalación del componente sentiment Azure
```
pip install azure-ai-textanalytics
```
# Ejecución con Azure 
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
