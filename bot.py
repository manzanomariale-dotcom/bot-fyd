from datetime import datetime
import threading
import time
from flask import Flask
import schedule
import telebot

TOKEN = "7691909067:AAG4EdkF0-_lpefI9ewFpo6AMhqawBZztAM"
CANAL = "@agenciafyd"
ENLACE_CANAL = "https://t.me/+x4A5d5Jpu44yNzc5"

bot = telebot.TeleBot(TOKEN)

# --- ESTRUCTURAS DE DATOS ---
resultados_horas_en_punto = {
    "08:00": {}, "09:00": {}, "10:00": {}, "11:00": {},
    "12:00": {}, "13:00": {}, "14:00": {}, "15:00": {},
    "16:00": {}, "17:00": {}, "18:00": {}, "19:00": {},
}

resultados_medias_horas = {
    "08:30": {}, "09:30": {}, "10:30": {}, "11:30": {},
    "12:30": {}, "13:30": {}, "14:30": {}, "15:30": {},
    "16:30": {}, "17:30": {}, "18:30": {},
}

LOTERIAS_COMPLETAS = [
    "Lotto Activo", "La Granjita", "Selva Plus", "Lotto Real",
    "Guácharo Activo", "Loto Chaima", "Monje Millonario",
    "Lotto RD", "Lotto Inter", "Guacharito Millonario",
    "Guaca Activa", "Mega Guaca",
]

# --- 1. MENSAJES INDIVIDUALES Y DE MAÑANA ---
def enviar_mensaje_buenos_dias():
    msg = (
        "🍀 **¡BUENOS DÍAS, CARGADOS DE BUENA SUERTE!** 🍀\n\n"
        "☀️ Arrancamos un nuevo día con la mejor energía para ganar.\n"
        f"🎯 Únete a nuestro canal oficial y entérate de todo: {ENLACE_CANAL}\n\n"
        "¡Que la suerte esté de tu lado hoy!"
    )
    try:
        bot.send_message(CANAL, msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error al enviar buenos días: {e}")

def enviar_resultado_individual(nombre_loteria, hora_resultado, resultado):
    msg = (
        f"🎯 **NUEVO RESULTADO** 🎯\n\n"
        f"🎲 **Lotería:** {nombre_loteria}\n"
        f"⏰ **Hora:** {hora_resultado}\n"
        f"🏆 **Resultado:** {resultado}\n\n"
        f"🍀 Agencia F&D"
    )
    try:
        bot.send_message(CANAL, msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error al enviar resultado individual: {e}")

# --- 2. GUARDAR Y CLASIFICAR EN MEMORIA ---
def guardar_resultado_en_memoria(nombre_loteria, hora_resultado, resultado):
    # Primero envía la alerta individual como lo hacías antes
    enviar_resultado_individual(nombre_loteria, hora_resultado, resultado)
    
    # Luego lo clasifica para las tablas automáticas
    try:
        dt = datetime.strptime(hora_resultado, "%H:%M")
        if dt.minute < 15 or dt.minute >= 45:
            slot = dt.replace(minute=0, second=0).strftime("%H:%M")
            if slot in resultados_horas_en_punto:
                resultados_horas_en_punto[slot][nombre_loteria] = resultado
        else:
            slot = dt.replace(minute=30, second=0).strftime("%H:%M")
            if slot in resultados_medias_horas:
                resultados_medias_horas[slot][nombre_loteria] = resultado
    except:
        pass

# --- 3. CONSTRUCTOR DE TABLAS ---
def construir_y_enviar_tabla(tipo_tabla="en_punto"):
    hoy = datetime.now().strftime("%d/%m/%Y")
    
    if tipo_tabla == "en_punto":
        slots_dict = resultados_horas_en_punto
        titulo_seccion = "📊 **RESULTADOS - HORAS EN PUNTO**"
    else:
        slots_dict = resultados_medias_horas
        titulo_seccion = "📊 **RESULTADOS - MEDIAS HORAS**"

    slots_activos = [s for s in sorted(slots_dict.keys()) if slots_dict[s]]

    if not slots_activos:
        if tipo_tabla == "en_punto":
            slots_activos = ["08:00", "09:00"]
            slots_dict["08:00"] = {lot: "12🐎" for lot in LOTERIAS_COMPLETAS[:4]}
            slots_dict["09:00"] = {lot: "25🐔" for lot in LOTERIAS_COMPLETAS[:4]}
        else:
            slots_activos = ["08:30", "09:30"]
            slots_dict["08:30"] = {lot: "31🦫" for lot in LOTERIAS_COMPLETAS[:4]}
            slots_dict["09:30"] = {lot: "18🫏" for lot in LOTERIAS_COMPLETAS[:4]}

    msg = f"🍀 **AGENCIA F&D** 🍀\n"
    msg += f"✨ ¡La suerte comienza aquí! ✨\n"
    msg += f"{titulo_seccion}\n"
    msg += f"📅 {hoy}\n\n"

    bloques = [
        LOTERIAS_COMPLETAS[0:4],
        LOTERIAS_COMPLETAS[4:8],
        LOTERIAS_COMPLETAS[8:12]
    ]

    for bloque in bloques:
        msg += "------------------------------------------\n"
        header = f"{'HORA':<8}"
        for lot in bloque:
            nombre_corto = (lot[:8] + '..') if len(lot) > 8 else lot[:8]
            header += f"{nombre_corto:<9}"
        msg += f"`{header}`\n"

        for slot in slots_activos:
            row = f"{slot:<8}"
            for lot in bloque:
                res = slots_dict[slot].get(lot, "----")
                row += f"{res:<9}"
            msg += f"`{row}`\n"
        
        msg += "\n"

    msg += "🍀 Gracias por preferir Agencia F&D\n"
    msg += "🎯 ¡Mucha suerte en cada jugada!\n"

    try:
        bot.send_message(CANAL, msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error al enviar tabla: {e}")

    for slot in slots_activos:
        slots_dict[slot].clear()

# --- COMANDOS DE PRUEBA DESDE TELEGRAM ---
@bot.message_handler(commands=['tabla', 'probar'])
def enviar_prueba_manual(message):
    try:
        construir_y_enviar_tabla("en_punto")
        bot.reply_to(message, "¡Tabla de horas en punto enviada con éxito!")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['medias'])
def enviar_prueba_medias(message):
    try:
        construir_y_enviar_tabla("medias_horas")
        bot.reply_to(message, "¡Tabla de medias horas enviada con éxito!")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['dia'])
def enviar_prueba_dia(message):
    enviar_mensaje_buenos_dias()
    bot.reply_to(message, "¡Mensaje de buenos días enviado!")

# --- PROGRAMACIÓN DE ENVÍOS CON SCHEDULE ---
# Mensaje de buenos días a las 07:30 AM
schedule.every().day.at("07:30").do(enviar_mensaje_buenos_dias)

# Tablas automáticas en sus horas correspondientes
schedule.every().hour.at(":10").do(lambda: construir_y_enviar_tabla("en_punto"))
schedule.every().hour.at(":40").do(lambda: construir_y_enviar_tabla("medias_horas"))

def ejecutar_programador():
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- SERVIDOR FLASK Y BUCLE DE TELEGRAM ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Telegram activo y operando 24/7."

if __name__ == "__main__":
    hilo_schedule = threading.Thread(target=ejecutar_programador)
    hilo_schedule.daemon = True
    hilo_schedule.start()

    hilo_bot = threading.Thread(target=bot.infinity_polling)
    hilo_bot.daemon = True
    hilo_bot.start()

    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
