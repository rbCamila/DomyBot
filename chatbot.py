from flask import Flask, request, jsonify
import pandas as pd
import spacy
import json
import re  

# Configuración inicial
app = Flask(__name__)
nlp = spacy.load("es_core_news_sm")  

# Cargar base de datos desde un archivo JSON
def load_documents():
    with open('C:/Users/USER/Documents/idea chatbot/data.json', 'r') as file:
        data = json.load(file)
    return pd.DataFrame(data["properties"])  

# Carga documentos al iniciar la aplicación
documents = load_documents()

# Función para procesar la intención del usuario
def identify_intent(message):
    message = message.lower().strip()  # Convierte a minúsculas y elimina los espacios
    doc = nlp(message)
    if "documento" in message or "buscar" in message:
        return "buscar_documento"
    elif "riesgo" in message:
        return "consultar_riesgo"
    elif "qué es" in message or "qué significa" in message or "definición" in message:
        return "consulta_general"
    else:
        return "desconocido"

# Rutas del chatbot
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    intent = identify_intent(user_message)
    print(f"Intención detectada: {intent}, Mensaje del usuario: {user_message}")  # Depuración

    if intent == "buscar_documento":
        return buscar_documento(user_message)
    elif intent == "consultar_riesgo":
        return consultar_riesgo(user_message)
    elif intent == "consulta_general":
        return consulta_general(user_message)
    else:
        return jsonify({"response": "Lo siento, no entendí tu pregunta."})

# Función para buscar documentos
def buscar_documento(message):
    message = message.lower() 
    if "partida registral" in message:
        result = documents[documents["partida_registral"].notnull()]
    elif "hoja resumen" in message:
        result = documents[documents["study"].apply(lambda x: "hoja resumen" in str(x).lower())]
    elif "estudio de títulos" in message:
        result = documents[documents["study"].apply(lambda x: "estudio de títulos" in str(x).lower())]
    else:
        return jsonify({"response": "No encontré documentos relacionados con tu búsqueda."})

    if result.empty:
        return jsonify({"response": "No encontré documentos relacionados con tu búsqueda."})

    # Crear respuesta
    docs = result.to_dict(orient="records")
    return jsonify({"response": "Documentos encontrados:", "data": docs})

# Función para consultar riesgos
def consultar_riesgo(message):
    # Buscar ID en el mensaje
    match = re.search(r'ID (\d+)', message)  # \d+ para buscar números
    if match:
        # Extraer el ID de la propiedad
        property_id = match.group(1)
        print(f"Buscando propiedad con ID: {property_id}") 

        # Verificar si el ID(type:string) está en los documentos
        result = documents[documents["id"] == property_id]
        if not result.empty:
            risk_level = result.iloc[0]["summary"]["risk_level"]
            return jsonify({
                "response": f"El riesgo de la propiedad con ID {property_id} es: {risk_level}",
                "data": result.to_dict(orient="records")
            })
        else:
            print(f"No se encontró la propiedad con ID {property_id}")  
            return jsonify({"response": f"No encontré la propiedad con ID {property_id}."})
    else:
        return jsonify({"response": "Por favor, proporciona un ID de propiedad para consultar el riesgo."})

# Función para respuestas generales
def consulta_general(message):
    if "partida registral" in message:
        return jsonify({"response": "Una partida registral es el documento legal que acredita la propiedad de un inmueble."})
    elif "hoja resumen" in message:
        return jsonify({"response": "La hoja resumen contiene los detalles principales de una transacción inmobiliaria."})
    elif "estudio de títulos" in message:
        return jsonify({"response": "Un estudio de títulos verifica la validez legal de una propiedad."})
    elif "gravamen" in message:
        return jsonify({"response": "Un gravamen es una carga o deuda que afecta a una propiedad."})
    elif "hipoteca" in message:
        return jsonify({"response": "Una hipoteca es un derecho real de garantía que se constituye sobre bienes inmuebles."})
    else:
        return jsonify({"response": "Lo siento, no tengo información sobre eso."})

# Ejecutar el servidor
if __name__ == '__main__':
    app.run(debug=True)
