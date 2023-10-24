# pip install pyinstaller
import subprocess

subprocess.run("rasa run -m models --enable-api --credentials credentials.yml", shell=True)
subprocess.run("rasa run actions", shell=True)
subprocess.run("python VoiceManager\STT.py", shell=True)
subprocess.run("python Servidor.py", shell=True)
subprocess.run("python Cliente.py", shell=True)

#pyinstaller --onefile mi_comando.py