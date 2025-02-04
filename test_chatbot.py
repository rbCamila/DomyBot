import requests

url = "http://127.0.0.1:5000/chat"
message = {"message": "¿Cuál es el riesgo de la propiedad con el ID 200001?"}

try:
    response = requests.post(url, json=message)  # Envia solicitud al servidor
    print(response.json())  # Muestra respuesta chatbot
except Exception as e:
    print(f"Error al conectar con el chatbot: {e}")
