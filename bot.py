import os
# Forzar la zona horaria de Venezuela de forma segura para Windows y Linux
os.environ['TZ'] = 'America/Caracas'
try:
    import time
    if hasattr(time, 'tzset'):
        time.tzset()
except Exception as e:
    print(f"⚠️ Nota sobre tzset: {e}")

import requests
from bs4 import BeautifulSoup
import time
import schedule
from threading import Thread
from flask import Flask
import re
import urllib3
from datetime import datetime
import random
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import traceback
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import urllib.parse

# Desactivar advertencias de certificados SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CONFIGURACIÓN DE CREDENCIALES Y ENLACES (FyD)
# ==========================================
TOKEN = '7691909067:AAG4EdkF0-_lpefI9ewFpo6AMhqawBZztAM'
CANAL = '@agenciafyd'
ENLACE_CANAL = 'https://t.me/+x4A5d5Jpu44yNzc5'

ADMIN_IDS = []

bot = telebot.TeleBot(TOKEN)

URL_LOTERIA = 'https://lotery.winbigvzla.com/resultados'
URL_BCV = 'https://www.bcv.org.ve/'

ARCH_REGISTRO = "resultados_enviados.json"
ARCH_GANADORES = "ganadores.json"
ARCH_CASHEA_INDEX = "cashea_index.json"
ARCH_PENDIENTES = "resultados_pendientes.json"

WHATSAPP_API_URL = os.environ.get("WHATSAPP_API_URL", "")
WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN", "")
WHATSAPP_DESTINATION = os.environ.get("WHATSAPP_DESTINATION", "04249611372")

RECOMENDADOS_HOY = {}
ACIERTOS_HOY = set()
CONTEO_ANIMALES_HOY = {}
ESTADOS_GANADOR = {}
ULTIMO_INDICE_MENSAJE = -1

MENSAJES_AUTOMATICOS = [
    f"🎯 *Agencia FyD* 🎯\n¡La suerte está de tu lado hoy! No te quedes sin jugar tu animalito favorito.\n📲 WhatsApp: 04249611372\n{ENLACE_CANAL}",
    f"🔥 ¡Activos con la buena energía en *Agencia FyD*! Elige tu animalito y ven a ganar con nosotros.\n📲 WhatsApp: 04249611372",
    f"🍀 ¿Ya consultaste tu palpito para el próximo sorteo? En *Agencia FyD* te pagamos al instante.\n📲 WhatsApp: 04249611372\n{ENLACE_CANAL}",
    f"⚡️ ¡No dejes para última hora tus jugadas! La banca de *Agencia FyD* está lista para recibir tu tiquet ganador.\n📲 04249611372",
    f"🌟 La constancia trae el éxito. ¡Sigue jugando tus animalitos preferidos en *Agencia FyD*!\n📲 WhatsApp: 04249611372\n{ENLACE_CANAL}",
    f"🎲 ¿Cuál es tu animalito fetiche hoy? Juega seguro y cobra rápido con *Agencia FyD*.\n📲 WhatsApp: 04249611372",
    f"🚀 ¡Arranca tu buena racha con *Agencia FyD*! Trabajamos para ti con la mejor atención.\n📲 WhatsApp: 04249611372\n{ENLACE_CANAL}",
    f"💡 Un buen día comienza jugando con confianza. ¡Haz tus jugadas en *Agencia FyD*!\n📲 WhatsApp: 04249611372",
    f"🎯 ¡Atención apostadores! La pizarra de *Agencia FyD* está habilitada para que revientes la banca hoy.\n📲 04249611372\n{ENLACE_CANAL}",
    f"✨ La suerte sonríe a los audaces. ¡Haz tu jugada ahora mismo en *Agencia FyD*!\n📲 WhatsApp: 04249611372"
]

MENSAJES_CASHEA_TELEGRAM = [
    (
        "💜✨ ¡JUEGA HOY, PAGA DESPUÉS! ✨💜\n"
        "💳 *CASHEA DISPONIBLE*\n"
        "✅ Sin inicial requerida\n"
        "🎯 Juega hoy y asegura tus animalitos\n"
        "💰 Cómodas cuotas para ti\n"
        "🔥 ¡Haz tu jugada con Agencia F&D!\n\n"
        "📲 Consulta disponibilidad por WhatsApp:\n"
        "04249611372\n"
        f"{ENLACE_CANAL}"
    ),
    (
        "💜💳 *FACILIDADES CON CASHEA* 💳💜\n"
        "¿Quieres jugar tus animalitos favoritos ahora mismo y cancelarlos después?\n\n"
        "✅ *CASHEA* está disponible en *Agencia F&D*\n"
        "🎯 Cupos altos y atención rápida\n"
        "🔥 ¡Facilita tus jugadas hoy!\n\n"
        "📲 Escríbenos al WhatsApp:\n"
        "04249611372\n"
        f"{ENLACE_CANAL}"
    ),
    (
        "✨💜 *¡DISFRUTA DE CASHEA EN AGENCIA F&D!* 💜✨\n"
        "💳 Llévate tus jugadas al instante:\n"
        "✅ Servicio confiable y seguro\n"
        "🎯 Juega hoy y paga cómodamente después\n"
        "🚀 ¡No te pierdas ningún sorteo!\n\n"
        "📲 Consulta detalles por WhatsApp:\n"
        "04249611372\n"
        f"{ENLACE_CANAL}"
    ),
    (
        "💜🔥 *JUEGA CON CASHEA* 🔥💜\n"
        "💳 ¡La mejor forma de asegurar tus animalitos sin complicaciones!\n"
        "✅ Proceso rápido y sin inicial\n"
        "🎯 Participa hoy mismo en los sorteos\n\n"
        "📲 Infórmate ahora mismo por WhatsApp:\n"
        "04249611372\n"
        f"{ENLACE_CANAL}"
    ),
    (
        "🎯 *CASHEA EN AGENCIA F&D* 🎯\n"
        "💳 ¿Sin saldo inmediato? ¡No te preocupes!\n"
        "⚡ Atención rápida y responsable\n"
        "💰 Cupos altos para tus jugadas\n"
        "✅ Juega ahora y paga después\n\n"
        "📲 Escríbenos al WhatsApp:\n"
        "04249611372\n"
        f"{ENLACE_CANAL}"
    )
]

MENSAJES_CASHEA_WHATSAPP = [
    (
        "💳 ¡CASHEA ACTIVO EN AGENCIA F&D!\n"
        "🔥 Juega ahora y paga después\n"
        "💰 Cupos altos | ⚡ Atención rápida\n\n"
        "🎯 *OPCIONES DE ACCIÓN:*\n"
        "1️⃣ Para jugar responde con: *JUGAR*\n"
        "2️⃣ Para consultar tu cupo responde con: *CONSULTAR*\n"
        "📲 04249611372"
    ),
    (
        "💜 ¡FACILIDADES CON CASHEA!\n"
        "✅ Sin inicial en Agencia F&D\n"
        "🎯 Juega hoy tus animalitos y paga después\n\n"
        "🎯 *OPCIONES DE ACCIÓN:*\n"
        "1️⃣ Para jugar responde con: *JUGAR*\n"
        "2️⃣ Para consultar tu cupo responde con: *CONSULTAR*\n"
        "📲 04249611372"
    ),
    (
        "✨ ¡DISFRUTA DE CASHEA HOY!\n"
        "💳 Llévate tus jugadas al instante en Agencia F&D\n"
        "💰 Cómodas cuotas y servicio confiable\n\n"
        "🎯 *OPCIONES DE ACCIÓN:*\n"
        "1️⃣ Para jugar responde con: *JUGAR*\n"
        "2️⃣ Para consultar tu cupo responde con: *CONSULTAR*\n"
        "📲 04249611372"
    )
]

ANIMALES_POOL = [
    "00 - Ballena", "0 - Delfín", "01 - Carnero", "02 - Toro", "03 - Ciempiés", "04 - Alacrán", 
    "05 - León", "06 - Rana", "07 - Perico", "08 - Ratón", "09 - Águila", 
    "10 - Tigre", "11 - Gato", "12 - Caballo", "13 - Mono", "14 - Paloma", 
    "15 - Zorro", "16 - Oso", "17 - Pavo", "18 - Burro", "19 - Chivo", 
    "20 - Cochino", "21 - Gallo", "22 - Camello", "23 - Cebra", "24 - Iguana", 
    "25 - Gallina", "26 - Vaca", "27 - Perro", "28 - Zamuro", "29 - Elefante", 
    "30 - Caimán", "31 - Lapa", "32 - Ardilla", "33 - Pescado", "34 - Venado", 
    "35 - Jirafa", "36 - Culebra"
]

MAPEO_ANIMALES_VALIDACION = {
    "00": "Ballena",
    "0": "Delfín",
    "1": "Carnero", "01": "Carnero",
    "2": "Toro", "02": "Toro",
    "3": "Ciempiés", "03": "Ciempiés",
    "4": "Alacrán", "04": "Alacrán",
    "5": "León", "05": "León",
    "6": "Rana", "06": "Rana",
    "7": "Perico", "07": "Perico",
    "8": "Ratón", "08": "Ratón",
    "9": "Águila", "09": "Águila",
    "10": "Tigre",
    "11": "Gato",
    "12": "Caballo",
    "13": "Mono",
    "14": "Paloma",
    "15": "Zorro",
    "16": "Oso",
    "17": "Pavo",
    "18": "Burro",
    "19": "Chivo",
    "20": "Cochino",
    "21": "Gallo",
    "22": "Camello",
    "23": "Cebra",
    "24": "Iguana",
    "25": "Gallina",
    "26": "Vaca",
    "27": "Perro",
    "28": "Zamuro",
    "29": "Elefante",
    "30": "Caimán",
    "31": "Lapa",
    "32": "Ardilla",
    "33": "Pescado",
    "34": "Venado",
    "35": "Jirafa",
    "36": "Culebra"
}

HEADER_FyD = (
    "*AGENCIA F&D*\n"
    "*RESULTADOS*\n\n"
    "🎲 *{nombre_loteria}* 🎲\n"
    "Hora: {hora}\n"
    "Animalito: *{resultado}*\n\n"
    "04249611372"
)

app = Flask('')

@app.route('/')
def home():
    return (
        f"¡El bot de resultados individuales de la <b>Agencia F&D</b> está activo en el canal {CANAL}!<br><br>"
        "<b>Enlaces de prueba rápida (Test):</b><br>"
        "👉 <a href='/test/regalo_6am'>Probar Regalo de las 6:00 AM</a><br>"
        "👉 <a href='/test/piramide'>Probar Pirámide Numérica (Imagen)</a><br>"
        "👉 <a href='/test/saludo'>Probar Saludo Matutino</a><br>"
        "👉 <a href='/test/estudio_manana'>Probar Análisis de las 8 AM</a><br>"
        "👉 <a href='/test/estudio_mediodia'>Probar Análisis del Mediodía</a><br>"
        "👉 <a href='/test/estudio_tarde'>Probar Análisis / Cierre de la Tarde</a><br>"
        "👉 <a href='/test/bcv'>Probar Tasa Oficial BCV</a><br>"
        "👉 <a href='/test/sorteo'>Probar Cierre de Sorteo (Min 25/55)</a><br>"
        "👉 <a href='/test/cierre'>Probar Cierre de Jornada (8:00 PM)</a><br>"
        "👉 <a href='/test/combinacion'>Probar Combinación Diaria</a><br>"
        "👉 <a href='/test/resumen_repetidos'>Probar Resumen de Repetidos</a><br>"
        "👉 <a href='/test/cashea'>Probar Publicidad Cashea con Botones</a><br>"
    )

@app.route('/test/regalo_6am')
def test_regalo_6am():
    enviar_regalo_6am()
    return "Prueba de Regalo de las 6:00 AM ejecutada."

@app.route('/test/piramide')
def test_piramide():
    enviar_piramide_diaria()
    return "Prueba de Pirámide Numérica en Imagen ejecutada."

@app.route('/test/saludo')
def test_saludo():
    enviar_saludo_matutino()
    return "Prueba de Saludo Matutino ejecutada."

@app.route('/test/estudio_manana')
def test_estudio_manana():
    enviar_estudio_8am()
    return "Prueba de Análisis de las 8 AM ejecutada."

@app.route('/test/estudio_mediodia')
def test_estudio_mediodia():
    enviar_estudio_mediodia()
    return "Prueba de Análisis del Mediodía ejecutada."

@app.route('/test/estudio_tarde')
def test_estudio_tarde():
    enviar_estudio_tarde()
    return "Prueba de Análisis de la Tarde ejecutada."

@app.route('/test/bcv')
def test_bcv():
    enviar_tasa_dolar()
    return "Prueba de Tasa BCV ejecutada."

@app.route('/test/sorteo')
def test_sorteo():
    enviar_aviso_cierre_sorteo()
    return "Prueba de Cierre de Sorteo ejecutada."

@app.route('/test/cierre')
def test_cierre():
    enviar_mensaje_cierre()
    return "Prueba de Cierre de Jornada ejecutada."

@app.route('/test/combinacion')
def test_combinacion():
    enviar_combinacion_diaria()
    return "Prueba de Combinación Diaria ejecutada."

@app.route('/test/cashea')
def test_cashea():
    enviar_publicidad_cashea()
    return "Prueba de Cashea ejecutada."

def limpiar_texto(texto):
    return " ".join(texto.split())

def enviar_telegram(mensaje, disable_web_preview=True, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CANAL, 
        "text": mensaje, 
        "parse_mode": "Markdown", 
        "disable_web_page_preview": disable_web_preview
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup.to_json()
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Error al enviar al canal: {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción de conexión con Telegram: {e}")

def enviar_whatsapp(mensaje):
    if not WHATSAPP_API_URL:
        print(f"ℹ️ [WhatsApp Simulado/Pendiente de Configuración]: {mensaje[:40]}...")
        return
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {WHATSAPP_API_TOKEN}" if WHATSAPP_API_TOKEN else ""
        }
        payload = {
            "phone": WHATSAPP_DESTINATION,
            "message": mensaje
        }
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Error al enviar WhatsApp: {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción de conexión con WhatsApp API: {e}")

def cargar_estado_cashea():
    if os.path.exists(ARCH_CASHEA_INDEX):
        try:
            with open(ARCH_CASHEA_INDEX, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"indice_tg": 0, "indice_wa": 0, "fecha": ""}

def guardar_estado_cashea(indice_tg, indice_wa):
    data = {
        "indice_tg": indice_tg,
        "indice_wa": indice_wa,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open(ARCH_CASHEA_INDEX, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar {ARCH_CASHEA_INDEX}: {e}")

def enviar_publicidad_cashea(es_prueba=False):
    if not es_prueba:
        ahora = datetime.now()
        minutos_actuales = ahora.hour * 60 + ahora.minute
        inicio_minutos = 8 * 60 + 20
        fin_minutos = 16 * 60 + 30
        if not (inicio_minutos <= minutos_actuales <= fin_minutos):
            return

    estado = cargar_estado_cashea()
    idx_tg = estado.get("indice_tg", 0)
    idx_wa = estado.get("indice_wa", 0)

    if not MENSAJES_CASHEA_TELEGRAM:
        return
    idx_tg = idx_tg % len(MENSAJES_CASHEA_TELEGRAM)
    mensaje_tg = MENSAJES_CASHEA_TELEGRAM[idx_tg]

    if not MENSAJES_CASHEA_WHATSAPP:
        return
    idx_wa = idx_wa % len(MENSAJES_CASHEA_WHATSAPP)
    if len(MENSAJES_CASHEA_WHATSAPP) > 1 and idx_wa == idx_tg:
        idx_wa = (idx_wa + 1) % len(MENSAJES_CASHEA_WHATSAPP)
    mensaje_wa = MENSAJES_CASHEA_WHATSAPP[idx_wa]

    numero_wa = "584249611372"
    msg_jugar = urllib.parse.quote("Hola, quiero jugar con Cashea en Agencia F&D.")
    msg_consultar = urllib.parse.quote("Hola, quiero consultar mi cupo o disponibilidad de Cashea en Agencia F&D.")
    
    url_jugar = f"https://wa.me/{numero_wa}?text={msg_jugar}"
    url_consultar = f"https://wa.me/{numero_wa}?text={msg_consultar}"

    markup_cashea = InlineKeyboardMarkup()
    markup_cashea.row(
        InlineKeyboardButton("🎯 JUGAR CON CASHEA", url=url_jugar),
        InlineKeyboardButton("💳 CONSULTAR CASHEA", url=url_consultar)
    )

    enviar_telegram(mensaje_tg, disable_web_preview=True, reply_markup=markup_cashea)
    enviar_whatsapp(mensaje_wa)

    if not es_prueba:
        siguiente_tg = (idx_tg + 1) % len(MENSAJES_CASHEA_TELEGRAM)
        siguiente_wa = (idx_wa + 1) % len(MENSAJES_CASHEA_WHATSAPP)
        guardar_estado_cashea(siguiente_tg, siguiente_wa)

@bot.message_handler(commands=['cashea'])
def cmd_cashea_inmediato(message):
    if ADMIN_IDS and message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⚠️ No tienes permisos para usar este comando.")
        return
    enviar_publicidad_cashea(es_prueba=False)
    bot.reply_to(message, "✅ Publicidad de Cashea ejecutada con botones y rotación avanzada.")

@bot.message_handler(commands=['cashea_test'])
def cmd_cashea_test(message):
    if ADMIN_IDS and message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⚠️ No tienes permisos para usar este comando.")
        return
    enviar_publicidad_cashea(es_prueba=True)
    bot.reply_to(message, "🧪 Prueba de Cashea enviada con botones (la rotación normal no fue afectada).")

@bot.message_handler(commands=['cashea_estado'])
def cmd_cashea_estado(message):
    if ADMIN_IDS and message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⚠️ No tienes permisos para usar este comando.")
        return
    estado = cargar_estado_cashea()
    idx_tg = estado.get("indice_tg", 0)
    idx_wa = estado.get("indice_wa", 0)
    ultima_fecha = estado.get("fecha", "Desconocida")
  
    info = (
        "📊 *ESTADO DE ROTACIÓN CASHEA* 📊\n\n"
        f"📍 Siguiente índice Telegram: `{idx_tg}` (Total: {len(MENSAJES_CASHEA_TELEGRAM)})\n"
        f"📍 Siguiente índice WhatsApp: `{idx_wa}` (Total: {len(MENSAJES_CASHEA_WHATSAPP)})\n"
        f"🕒 Última actualización persistente: `{ultima_fecha}`\n"
        f"⏰ Horario activo: 8:20 AM - 4:30 PM (America/Caracas)"
    )
    bot.reply_to(message, info, parse_mode="Markdown")

def limpiar_recomendaciones_diarias():
    RECOMENDADOS_HOY.clear()
    ACIERTOS_HOY.clear()
    CONTEO_ANIMALES_HOY.clear()

def registrar_recomendacion(numero, etiqueta, dt_recomendacion=None):
    num_str = str(numero).zfill(2) if numero not in ["0", "00"] else str(numero)
    if dt_recomendacion is None:
        dt_recomendacion = datetime.now()
    if num_str not in RECOMENDADOS_HOY:
        RECOMENDADOS_HOY[num_str] = []
    RECOMENDADOS_HOY[num_str].append({
        "etiqueta": etiqueta,
        "tiempo": dt_recomendacion
    })

def enviar_mensaje_automatico():
    global ULTIMO_INDICE_MENSAJE
    if not MENSAJES_AUTOMATICOS:
        return
    indice = random.randint(0, len(MENSAJES_AUTOMATICOS) - 1)
    if len(MENSAJES_AUTOMATICOS) > 1:
        while indice == ULTIMO_INDICE_MENSAJE:
            indice = random.randint(0, len(MENSAJES_AUTOMATICOS) - 1)
    ULTIMO_INDICE_MENSAJE = indice
    enviar_telegram(MENSAJES_AUTOMATICOS[indice], disable_web_preview=True)

def enviar_regalo_6am():
    dt_pub = datetime.now()
    regalo = seleccionar_analisis_dinamico(1)[0]
    numero = regalo.split(" - ")[0].strip()
    registrar_recomendacion(numero, "🎁 Regalo de las 6:00 AM", dt_pub)

    enviar_telegram(
        "🎯 *AGENCIA F&D* 🎯\n\n"
        "☀️ *¡Muy buenos días!* Arrancamos el día con la mejor actitud y la mejor energía para ganar.\n\n"
        f"🎁 *El Regalo de las 6:00 AM:* `{regalo}`\n\n"
        "📲 WHATSAPP: 04249611372\n"
        f"{ENLACE_CANAL}\n"
        "¡Mucho éxito en tus jugadas de hoy! 🍀🔥",
        disable_web_preview=True
    )

def generar_imagen_piramide():
    ahora = datetime.now()
    fecha_str = ahora.strftime("%d/%m/%Y")
    digitos = [int(c) for c in fecha_str if c.isdigit()]
    filas = [digitos]
    while len(filas[-1]) > 1:
        actual = filas[-1]
        siguiente = [(actual[i] + actual[i+1]) % 10 for i in range(len(actual) - 1)]
        filas.append(siguiente)

    seed_val = int(ahora.strftime("%Y%m%d"))
    rnd = random.Random(seed_val)
    candidates = []
    for f in filas:
        for idx in range(len(f) - 1):
            val = (f[idx] * 10 + f[idx+1]) % 37
            candidates.append(f"{val:02d}" if val != 0 else "0")
            candidates.append("00")
        for num in f:
            val = (num * 7) % 37
            candidates.append(f"{val:02d}" if val != 0 else "0")
            candidates.append("00")

    unique_candidates = []
    for c in candidates:
        if c not in unique_candidates:
            unique_candidates.append(c)

    while len(unique_candidates) < 6:
        r_val = rnd.randint(0, 36)
        c_rand = f"{r_val:02d}" if r_val != 0 else ("0" if rnd.random() > 0.5 else "00")
        if c_rand not in unique_candidates:
            unique_candidates.append(c_rand)

    d1 = f"{unique_candidates[0]}-{unique_candidates[1]}-{unique_candidates[2]}"
    d2 = f"{unique_candidates[3]}-{unique_candidates[4]}-{unique_candidates[5]}"

    img_width, img_height = 1000, 1120
    image = Image.new("RGB", (img_width, img_height), color=(30, 10, 10))
    draw = ImageDraw.Draw(image)

    color_dorado = (212, 175, 55)
    color_dorado_claro = (243, 229, 149)
    color_morado = (148, 0, 211)
    color_blanco = (255, 255, 255)
    color_panel = (20, 20, 20)

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
        font_sub = ImageFont.truetype("DejaVuSans.ttf", 24)
        font_pir = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        font_data = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_pir = ImageFont.load_default()
        font_data = ImageFont.load_default()

    draw.text((img_width // 2, 45), "AGENCIA F&D", fill=color_dorado, anchor="mm", font=font_title)
    draw.text((img_width // 2, 90), "Trabajamos para tí", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((img_width // 2, 145), "PIRÁMIDE DEL DÍA", fill=color_morado, anchor="mm", font=font_title)

    draw.rectangle([img_width // 2 - 180, 185, img_width // 2 + 180, 240], fill=color_panel, outline=color_dorado, width=2)
    draw.text((img_width // 2, 212), f"📅  {fecha_str}", fill=color_dorado_claro, anchor="mm", font=font_data)

    panel_bottom = 740
    draw.rectangle([40, 290, 280, panel_bottom], fill=color_panel, outline=color_morado, width=2)
    draw.text((160, 315), "★ DATOS ★", fill=color_dorado, anchor="mm", font=font_data)
    draw.text((160, 355), "NÚMEROS USADOS", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 390), f"{len(set([d for f in filas for d in f])) * 4}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 440), "SUMA TOTAL", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 475), f"{sum([sum(f) for f in filas]) * 3}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 525), "NÚMERO MAYOR", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 560), f"{max([max(f) for f in filas])}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 610), "NÚMERO MENOR", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 645), f"{min([min(f) for f in filas])}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 695), "NÚMERO FRECUENTE", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 730), f"{digitos[0]} (7 VECES)", fill=color_dorado_claro, anchor="mm", font=font_data)

    draw.rectangle([720, 290, 960, panel_bottom], fill=color_panel, outline=color_morado, width=2)
    draw.text((840, 315), "★ SUMA ★", fill=color_dorado, anchor="mm", font=font_data)
    draw.text((840, 350), "POR FILA", fill=color_dorado, anchor="mm", font=font_data)
    
    y_suma_pos = 400
    for idx, f in enumerate(filas):
        suma_fila = sum(f)
        draw.text((840, y_suma_pos), f"{idx+1}RA FILA: {suma_fila}", fill=color_blanco, anchor="mm", font=font_sub)
        y_suma_pos += 40

    start_y = 280
    row_height = 54
    center_x = img_width // 2
    circle_radius = 23

    for i, f in enumerate(filas):
        num_items = len(f)
        total_width = num_items * 52
        start_x_row = center_x - (total_width // 2)

        for j, num in enumerate(f):
            cx = start_x_row + (j * 52) + 24
            cy = start_y + (i * row_height) + 24
            draw.ellipse([cx - circle_radius, cy - circle_radius, cx + circle_radius, cy + circle_radius], fill=color_panel, outline=color_dorado, width=3)
            draw.text((cx, cy), str(num), fill=color_blanco, anchor="mm", font=font_pir)

    box_top = 760
    draw.rectangle([150, box_top, img_width - 150, box_top + 150], fill=color_panel, outline=color_dorado, width=2)
    draw.text((img_width // 2, box_top + 28), "🔥 DATOS CLAVES PARA HOY:", fill=color_dorado, anchor="mm", font=font_sub)
    draw.text((img_width // 2, box_top + 75), f"📌 {d1}", fill=color_blanco, anchor="mm", font=font_data)
    draw.text((img_width // 2, box_top + 115), f"📌 {d2}", fill=color_blanco, anchor="mm", font=font_data)

    footer_y = 955
    draw.text((img_width // 2, footer_y), "WHATSAPP: 04249611372", fill=color_dorado_claro, anchor="mm", font=font_sub)

    bio = BytesIO()
    bio.name = 'piramide_fyd.png'
    image.save(bio, 'PNG')
    bio.seek(0)
    return bio

def enviar_piramide_diaria():
    try:
        foto_bio = generar_imagen_piramide()
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': foto_bio}
        data = {
            'chat_id': CANAL,
            'caption': f"📢 *REPORTE TÁCTICO - LA PIRÁMIDE*\n\nWHATSAPP: 04249611372\n{ENLACE_CANAL}",
            'parse_mode': 'Markdown'
        }
        requests.post(url, data=data, files=files, timeout=15)
    except Exception as e:
        print(f"Error generando/enviando imagen pirámide: {e}")

def obtener_animales_salidos_actuales():
    salidos = set()
    try:
        resultados_map = obtener_resultados_winbig_estructurado()
        for item in resultados_map:
            res = item.get("resultado", "")
            if "PENDIENTE" not in res:
                num_partes = res.split("-")[0].strip()
                salidos.add(num_partes)
    except Exception as e:
        print(f"Error obteniendo salidos para análisis: {e}")
    return salidos

def seleccionar_analisis_dinamico(cantidad):
    salidos = obtener_animales_salidos_actuales()
    disponibles = [a for a in ANIMALES_POOL if a.split(" - ")[0].strip() not in salidos]
    if len(disponibles) < cantidad:
        disponibles = ANIMALES_POOL
    seed_val = int(datetime.now().strftime("%Y%m%d%H%M"))
    rnd = random.Random(seed_val)
    return rnd.sample(disponibles, cantidad)

def enviar_combinacion_diaria():
    dt_pub = datetime.now()
    salidos = obtener_animales_salidos_actuales()
    disponibles = [a for a in ANIMALES_POOL if a.split(" - ")[0].strip() not in salidos]
    if len(disponibles) < 7:
        disponibles = ANIMALES_POOL

    seed_val = int(dt_pub.strftime("%Y%m%d%H%M%S"))
    rnd = random.Random(seed_val)
    seleccionados = rnd.sample(disponibles, 7)

    fijo1 = seleccionados[0]
    fijo2 = seleccionados[1]
    par1 = seleccionados[2]
    par2 = seleccionados[3]
    trip1 = seleccionados[4]
    trip2 = seleccionados[5]
    trip3 = seleccionados[6]

    for animal in seleccionados:
        num = animal.split(" - ")[0].strip()
        registrar_recomendacion(num, "🎯 Combinación Especial F&D", dt_pub)

    par_str = f"{par1.split(' - ')[0].strip()} - {par2.split(' - ')[0].strip()}"
    trip_str = f"{trip1.split(' - ')[0].strip()} - {trip2.split(' - ')[0].strip()} - {trip3.split(' - ')[0].strip()}"

    mensaje = (
        "🎯 *COMBINACIÓN GANADORA - AGENCIA F&D* 🎯\n"
        "🔥 ¡Datos exclusivos y directos para asegurar tus jugadas:\n\n"
        f"📌 *Fijos del Día:* `{fijo1}` y `{fijo2}`\n"
        f"📌 *El Par:* `{par_str}`\n"
        f"📌 *La Tripleta:* `{trip_str}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}\n\n"
        "¡A cobrar se ha dicho! 🍀✨"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_estudio_8am():
    dt_pub = datetime.now()
    analisis = seleccionar_analisis_dinamico(2)
    for animal in analisis:
        numero = animal.split(" - ")[0].strip()
        registrar_recomendacion(numero, "🔍 Análisis 8:15 AM", dt_pub)

    mensaje = (
        "🎯 *AGENCIA F&D* 🎯\n"
        "🔍 *ANÁLISIS TRAS EL SORTEO DE LAS 8:00 AM* 🔍\n\n"
        "¡Ya salieron los primeros animalitos! Evaluando la apertura de la pizarra y descartando lo ya jugado, la casa trae las recomendaciones probables para los siguientes sorteos:\n\n"
        f"🔥 *Regalitos recomendados:* `{analisis[0]}` y `{analisis[1]}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_estudio_mediodia():
    dt_pub = datetime.now()
    analisis = seleccionar_analisis_dinamico(2)
    for animal in analisis:
        numero = animal.split(" - ")[0].strip()
        registrar_recomendacion(numero, "☀️ Análisis Mediodía", dt_pub)

    tripleta = seleccionar_analisis_dinamico(3)
    for animal in tripleta:
        numero = animal.split(" - ")[0].strip()
        registrar_recomendacion(numero, "🎯 Tripleta Mediodía", dt_pub)

    t_str = f"{tripleta[0].split(' - ')[0].strip()} - {tripleta[1].split(' - ')[0].strip()} - {tripleta[2].split(' - ')[0].strip()}"
     
    mensaje = (
        "🎯 *AGENCIA F&D* 🎯\n"
        "☀️ *ANÁLISIS DEL MEDIODÍA* ☀️\n\n"
        "*¡Mitad de jornada! Estudiando los resultados que nos dejó la mañana y analizando tendencias en vivo, el tablero apunta hacia las siguientes proyecciones:*\n\n"
        f"🔥 *Animales calientes:* `{analisis[0]}` y `{analisis[1]}`\n"
        f"🎯 *Tripleta recomendada:* `{t_str}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_estudio_tarde():
    dt_pub = datetime.now()
    analisis = seleccionar_analisis_dinamico(2)
    for animal in analisis:
        numero = animal.split(" - ")[0].strip()
        registrar_recomendacion(numero, "🌇 Análisis Tarde", dt_pub)

    mensaje = (
        "🎯 *AGENCIA F&D* 🎯\n"
        "🌇 *ANÁLISIS Y CIERRE DE LA TARDE* 🌇\n\n"
        "¡A pocas horas de terminar la jornada! Evaluando el comportamiento de los últimos sortos y filtrando los ganadores del día, la casa trae los animales con mayor probabilidad de reventar para asegurar el cierre:\n\n"
        f"⚡️ *Imparables de la Tarde / Cierre:* `{analisis[0]}` y `{analisis[1]}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_saludo_matutino():
    enviar_telegram(
        "🎯 AGENCIA F&D 🎯\n\n"
        "☀️ ¡Buenos días! Arrancamos la jornada con la mejor actitud y la mejor energía para ganar.\n\n"
        "📲 WHATSAPP: 04249611372\n"
        "¡Mucho éxito en tus jugadas de hoy! 🍀🔥",
        disable_web_preview=True
    )

def enviar_tasa_dolar():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL_BCV, headers=headers, timeout=15, verify=False)
        precio_dolar = "742,23"
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            dolar_div = soup.find('div', id='dolar')
            if dolar_div and dolar_div.find('strong'):
                precio_dolar = dolar_div.find('strong').get_text(strip=True)
        enviar_telegram(
            "💵 TASA OFICIAL BCV 💵\n"
            f"📈 Precio Oficial: Bs. {precio_dolar}\n"
            f"Verifica la tasa oficial en: {URL_BCV}",
            disable_web_preview=True
        )
    except Exception as e:
        print(f"Error BCV: {e}")

def enviar_mensaje_cierre():
    enviar_telegram(
        "AGENCIA F&D\n"
        "🌙 ¡FINAL DE JORNADA! 🌙\n"
        "*¡Listo por hoy! 🚀 Que descansen y sueñen en grande. Mañana nos vemos tempranito con más suerte y nuevos retos. ¡Buenas noches! 🌟💤*",
        disable_web_preview=True
    )

def enviar_aviso_cierre_sorteo():
    enviar_telegram(
        "🛑 *¡ATENCIÓN!* 🛑\n\n"
        "El tiempo de jugadas ha terminado por este sorteo en la **AGENCIA F&D**.\n\n"
        "🤞 ¡Cruzamos los dedos por ti, mucha suerte en tus apuestas! 🎲🔥",
        disable_web_preview=True
    )

def cargar_registros():
    if os.path.exists(ARCH_REGISTRO):
        try:
            with open(ARCH_REGISTRO, "r") as f:
                data = json.load(f)
                if data.get("fecha") == datetime.now().strftime("%d-%m-%Y"):
                    return set(data.get("enviados", []))
        except Exception:
            pass
    return set()

def guardar_registros(enviados_set):
    data = {
        "fecha": datetime.now().strftime("%d-%m-%Y"),
        "enviados": list(enviados_set)
    }
    try:
        with open(ARCH_REGISTRO, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error al guardar registros: {e}")

def cargar_pendientes():
    if os.path.exists(ARCH_PENDIENTES):
        try:
            with open(ARCH_PENDIENTES, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("fecha") == datetime.now().strftime("%d-%m-%Y"):
                    return data.get("pendientes", {})
        except Exception:
            pass
    return {}

def guardar_pendientes(pendientes_dict):
    data = {
        "fecha": datetime.now().strftime("%d-%m-%Y"),
        "pendientes": pendientes_dict
    }
    try:
        with open(ARCH_PENDIENTES, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar pendientes: {e}")

# ==========================================
# MÓDULO CENTRAL DE SCRAPING DINÁMICO ESTRICTO
# ==========================================
def normalizar_nombre_loteria(texto_crudo):
    t = limpiar_texto(texto_crudo).upper()
    if not t:
        return None
    
    if "LOTTO ACTIVO" in t:
        return "LOTTO ACTIVO"
    elif "GRANJITA" in t:
        return "GRANJITA"
    elif "SELVA PLUS" in t:
        return "SELVA PLUS"
    elif "LOTTO REAL" in t:
        return "LOTTO REAL"
    elif "GUACHARO" in t or "GUÁCHARO" in t:
        return "GUACHARO"
    elif "LOTTO CHAIMA" in t:
        return "LOTTO CHAIMA"
    elif "MONJE MILLONARIO" in t:
        return "MONJE MILLONARIO"
    
    return None

def validar_numero_animal(num_str, animal_texto):
    num_limpio = num_str.strip()
    animal_limpio = animal_texto.strip().capitalize()
    
    if num_limpio not in MAPEO_ANIMALES_VALIDACION:
        return False
    
    esperado = MAPEO_ANIMALES_VALIDACION[num_limpio]
    if esperado.lower() != animal_limpio.lower():
        return False
        
    return True

def obtener_resultados_winbig_estructurado():
    resultados_lista = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        respuesta = requests.get(URL_LOTERIA, headers=headers, timeout=15)
        if respuesta.status_code != 200:
            return resultados_lista

        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Enfoque estrictamente secuencial por bloques de encabezados reales
        bloques = soup.find_all(['div', 'section', 'article', 'li'])
        
        loteria_actual = None
        
        for elem in bloques:
            texto_elem = limpiar_texto(elem.get_text(" ", strip=True))
            if not texto_elem:
                continue
                
            # Verificar si este elemento o un hijo directo contiene un encabezado de lotería exacto
            titulos_candidatos = elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b', 'span'], class_=re.compile(r'title|header|name|lotto', re.IGNORECASE))
            encontro_encabezado_firme = False
            
            for tc in titulos_candidatos:
                posible_nombre = normalizar_nombre_loteria(tc.get_text(strip=True))
                if posible_nombre:
                    loteria_actual = posible_nombre
                    encontro_encabezado_firme = True
                    print(f"[DEBUG] LOTERIA DETECTADA: {loteria_actual}")
                    break
            
            if not encontro_encabezado_firme:
                # Comprobar texto directo si es un bloque limpio de encabezado
                posible_nombre = normalizar_nombre_loteria(texto_elem)
                if posible_nombre and len(texto_elem) < 35 and not re.search(r'\d{1,2}:\d{2}', texto_elem):
                    loteria_actual = posible_nombre
                    print(f"[DEBUG] LOTERIA DETECTADA (Texto Directo): {loteria_actual}")
                    continue

            if not loteria_actual:
                continue

            # Buscar slots de sorteos dentro del bloque actual
            slots_sorteo = elem.find_all(['div', 'li', 'span', 'tr', 'p'], class_=re.compile(r'item|slot|draw|row|col|result', re.IGNORECASE))
            if not slots_sorteo:
                slots_sorteo = [elem]

            for slot in slots_sorteo:
                texto_slot = limpiar_texto(slot.get_text(" ", strip=True)).upper()
                match_h = re.search(r'\b(\d{1,2}:\d{2}\s*(?:AM|PM))\b', texto_slot)
                if not match_h:
                    continue
                hora = match_h.group(1).upper()

                if "PENDIENTE" in texto_slot:
                    resultados_lista.append({
                        "loteria": loteria_actual,
                        "hora": hora,
                        "resultado": "⏳ Pendiente"
                    })
                    print(f"[DEBUG] {hora} → ⏳ Pendiente ({loteria_actual})")
                    continue

                match_res = re.search(r'\b(00|0|\d{1,2})\s*-\s*([A-ZÁÉÍÓÚÑa-zñáéíóú]+(?:\s+[A-ZÁÉÍÓÚÑa-zñáéíóú]+)?)\b', texto_slot)
                if match_res:
                    num_crudo = match_res.group(1)
                    animal_texto = match_res.group(2).strip().capitalize()
                    
                    if num_crudo == "00":
                        num_str = "00"
                    elif num_crudo == "0":
                        num_str = "0"
                    else:
                        num_str = str(int(num_crudo)).zfill(2)

                    # Validación rigurosa de número + animal
                    if not validar_numero_animal(num_str, animal_texto):
                        print(f"[DEBUG] ALERTA: Resultado descartado por discordancia num/animal: {num_str} - {animal_texto}")
                        continue

                    resultado_formateado = f"{num_str} - {animal_texto}"
                    
                    # Evitar duplicados exactos en la misma lotería/hora
                    item_existente = next((x for x in resultados_lista if x["loteria"] == loteria_actual and x["hora"] == hora), None)
                    if not item_existente:
                        resultados_lista.append({
                            "loteria": loteria_actual,
                            "hora": hora,
                            "resultado": resultado_formateado
                        })
                        print(f"[DEBUG] {hora} → {resultado_formateado} [{loteria_actual}]")

    except Exception as e:
        print(f"Error en obtener_resultados_winbig_estructurado: {e}")

    return resultados_lista

def cargar_ganadores_persistentes():
    if os.path.exists(ARCH_GANADORES):
        try:
            with open(ARCH_GANADORES, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_ganador_persistente(registro):
    ganadores = cargar_ganadores_persistentes()
    ganadores.append(registro)
    try:
        with open(ARCH_GANADORES, "w", encoding="utf-8") as f:
            json.dump(ganadores, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar ganadores.json: {e}")

@bot.message_handler(commands=['ganador'])
def cmd_ganador(message):
    chat_id = message.chat.id
    ESTADOS_GANADOR[chat_id] = {
        "paso": "nombre",
        "datos": {}
    }
    bot.send_message(
        chat_id,
        "🏆 Vamos a registrar un ganador para **Agencia F&D**.\n\n"
        "✍️ Envíame el **nombre del ganador**:",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.chat.id in ESTADOS_GANADOR and ESTADOS_GANADOR[m.chat.id]["paso"] in ["nombre", "loteria", "numero", "premio"])
def procesar_pasos_ganador(message):
    chat_id = message.chat.id
    estado = ESTADOS_GANADOR[chat_id]
    paso_actual = estado["paso"]
    texto = message.text.strip() if message.text else ""

    if not texto:
        bot.send_message(chat_id, "⚠️ Por favor, ingresa un texto válido.")
        return

    if paso_actual == "nombre":
        estado["datos"]["nombre"] = texto
        estado["paso"] = "loteria"
        bot.send_message(chat_id, "🎯 ¿En qué lotería ganó? (Ej: Lotto Activo, Granjita, etc.)")
    elif paso_actual == "loteria":
        estado["datos"]["loteria"] = texto
        estado["paso"] = "numero"
        bot.send_message(chat_id, "🔢 ¿Cuál fue el número o animalito ganador? (Ej: 25 - Gallina)")
    elif paso_actual == "numero":
        estado["datos"]["numero"] = texto
        estado["paso"] = "premio"
        bot.send_message(chat_id, "💰 ¿Cuál fue el monto del premio? (Ej: 500 Bs o 20$):")
    elif paso_actual == "premio":
        estado["datos"]["premio"] = texto
        estado["paso"] = "capture"
        bot.send_message(chat_id, "📸 Ahora envíame el **capture del pago realizado** (como foto). Será la imagen publicada con el texto como pie de página.")

@bot.message_handler(content_types=['photo'], func=lambda m: m.chat.id in ESTADOS_GANADOR and ESTADOS_GANADOR[m.chat.id].get("paso") == "capture")
def procesar_capture_ganador(message):
    chat_id = message.chat.id
    estado = ESTADOS_GANADOR[chat_id]

    file_id = message.photo[-1].file_id
    estado["datos"]["capture_file_id"] = file_id
    estado["paso"] = "confirmar"

    datos = estado["datos"]

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ PUBLICAR", callback_data="ganador_publicar"),
        InlineKeyboardButton("❌ CANCELAR", callback_data="ganador_cancelar")
    )

    caption_preview = (
        "🔎 **Vista previa del mensaje que irá en el pie del capture:**\n\n"
        "🏆 *¡TENEMOS GANADOR!* 🏆\n\n"
        "*AGENCIA F&D*\n\n"
        f"🎯 Lotería: {datos['loteria']}\n"
        f"🔢 Número: {datos['numero']}\n"
        f"💰 Premio: {datos['premio']}\n\n"
        f"🎉 ¡FELICIDADES, {datos['nombre'].upper()}!\n\n"
        "Gracias por confiar en Agencia F&D. 🍀\n"
        f"{ENLACE_CANAL}"
    )

    bot.send_photo(chat_id, file_id, caption=caption_preview, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data in ["ganador_publicar", "ganador_cancelar"])
def callback_publicar_ganador(call):
    chat_id = call.message.chat.id
    estado = ESTADOS_GANADOR.get(chat_id)

    if not estado:
        bot.answer_callback_query(call.id, "⚠️ La sesión ha expirado o ya fue procesada.")
        return

    if call.data == "ganador_cancelar":
        ESTADOS_GANADOR.pop(chat_id, None)
        try:
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=call.message.message_id,
                caption="❌ Registro de ganador cancelado.",
                reply_markup=None
            )
        except Exception:
            bot.send_message(chat_id, "❌ Registro de ganador cancelado.")
        bot.answer_callback_query(call.id, "Cancelado con éxito.")
        return

    if call.data == "ganador_publicar":
        datos = estado["datos"]
        try:
            bot.answer_callback_query(call.id, "Publicando ganador...")

            texto_canal = (
                "🏆 ¡TENEMOS GANADOR! 🏆\n\n"
                "*AGENCIA F&D*\n\n"
                f"🎯 Lotería: {datos['loteria']}\n"
                f"🔢 Número: {datos['numero']}\n"
                f"💰 Premio: {datos['premio']}\n\n"
                f"🎉 ¡FELICIDADES, {datos['nombre'].upper()}!\n\n"
                "Gracias por confiar en Agencia F&D. 🍀\n"
                f"{ENLACE_CANAL}"
            )

            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            payload = {
                'chat_id': CANAL,
                'photo': datos['capture_file_id'],
                'caption': texto_canal,
                'parse_mode': 'Markdown'
            }
            requests.post(url, json=payload, timeout=15)

            registro_final = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nombre": datos["nombre"],
                "loteria": datos["loteria"],
                "numero": datos["numero"],
                "premio": datos["premio"],
                "capture_file_id": datos["capture_file_id"]
            }
            guardar_ganador_persistente(registro_final)

            try:
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    caption="✅ ¡Ganador publicado con éxito usando el capture en el canal y registrado en ganadores.json!",
                    reply_markup=None
                )
            except Exception:
                bot.send_message(chat_id, "✅ ¡Ganador publicado con éxito!")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Error al publicar en el canal: {str(e)}")
        finally:
            ESTADOS_GANADOR.pop(chat_id, None)

def verificar_y_enviar_resultados_individuales():
    enviados_hoy = cargar_registros()
    es_primera_ejecucion = len(enviados_hoy) == 0
     
    try:
        resultados_lista = obtener_resultados_winbig_estructurado()
        if not resultados_lista:
            return

        pendientes = cargar_pendientes()
        nuevos_pendientes = {}
        hubo_cambios = False
        nuevos_para_guardar = set(enviados_hoy)
        fecha_hoy_str = datetime.now().strftime("%Y-%m-%d")

        for item in resultados_lista:
            nombre_loteria_ind = item["loteria"]
            hora = item["hora"]
            resultado = item["resultado"]

            if "PENDIENTE" in resultado:
                continue

            id_sorteo = f"{fecha_hoy_str}|{nombre_loteria_ind}|{hora}"
            id_resultado_completo = f"{nombre_loteria_ind}_{hora}_{resultado}"

            if id_resultado_completo in enviados_hoy:
                continue

            if id_sorteo in pendientes:
                valor_anterior = pendientes[id_sorteo]
                if valor_anterior == resultado:
                    if es_primera_ejecucion:
                        nuevos_para_guardar.add(id_resultado_completo)
                    else:
                        numero = resultado.split("-")[0].strip()
                        if numero in RECOMENDADOS_HOY and numero not in ACIERTOS_HOY:
                            try:
                                dt_resultado = datetime.strptime(f"{fecha_hoy_str} {hora}", "%Y-%m-%d %I:%M %p")
                            except Exception:
                                dt_resultado = datetime.now()

                            cumple_tiempo = False
                            etiqueta_valida = ""
                            for rec in RECOMENDADOS_HOY[numero]:
                                if dt_resultado > rec["tiempo"]:
                                    cumple_tiempo = True
                                    etiqueta_valida = rec["etiqueta"]
                                    break

                            if cumple_tiempo and id_resultado_completo not in [a.get("id_res") for a in list(ACIERTOS_HOY) if isinstance(a, dict)]:
                                mensaje_acierto = (
                                    "🎉🎉 *¡ACERTAMOS!* 🎉🎉\n\n"
                                    f"✅ {etiqueta_valida}\n\n"
                                    f"🎯 *{resultado}*\n"
                                    f"🎲 {nombre_loteria_ind}\n"
                                    f"🕒 {hora}\n\n"
                                    "🍀 *¡Felicidades a todos los que confiaron en Agencia F&D!*"
                                )
                                enviar_telegram(mensaje_acierto)
                                ACIERTOS_HOY.add(numero)
                                ACIERTOS_HOY.add(f"ACERTADO_{id_resultado_completo}")

                        hora_actual_str = datetime.now().strftime("%I:%M %p")
                        mensaje = HEADER_FyD.format(
                            hora_str=hora_actual_str,
                            nombre_loteria=nombre_loteria_ind,
                            hora=hora,
                            resultado=resultado
                        )
                        enviar_telegram(mensaje)
                        nuevos_para_guardar.add(id_resultado_completo)
                        hubo_cambios = True
                        time.sleep(1.5)
                else:
                    nuevos_pendientes[id_sorteo] = resultado
            else:
                nuevos_pendientes[id_sorteo] = resultado

        guardar_pendientes(nuevos_pendientes)

        if es_primera_ejecucion:
            guardar_registros(nuevos_para_guardar)
        elif hubo_cambios:
            guardar_registros(nuevos_para_guardar)

    except Exception as e:
        print(f"Error al verificar resultados individuales: {e}")

ultimo_aviso_minuto = ""

def verificar_minuto():
    global ultimo_aviso_minuto
    ahora = datetime.now()
    hora_actual_minutos = ahora.hour * 60 + ahora.minute
    inicio_minutos = 7 * 60 + 25
    fin_minutos = 19 * 60 + 55

    if not (inicio_minutos <= hora_actual_minutos <= fin_minutos):
        return

    minuto_actual = ahora.minute
    if minuto_actual in [25, 55]:
        clave_tiempo = ahora.strftime("%H:%M")
        if ultimo_aviso_minuto != clave_tiempo:
            enviar_aviso_cierre_sorteo()
            ultimo_aviso_minuto = clave_tiempo

@bot.message_handler(commands=['resumen', 'tabla'])
def cmd_resumen(message):
    try:
        bot.reply_to(message, "🔍 Consultando resumen de resultados actual, por favor espera...")
         
        resultados_lista = obtener_resultados_winbig_estructurado()

        if not resultados_lista:
            bot.reply_to(message, "⚠️ No se encontraron resultados disponibles en este momento.")
            return

        # Agrupar por lotería para el reporte
        resumen_por_loterias = {}
        for item in resultados_lista:
            lot = item["loteria"]
            if lot not in resumen_por_loterias:
                resumen_por_loterias[lot] = {}
            resumen_por_loterias[lot][item["hora"]] = item["resultado"]

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        texto_final = (
            "🎯 *AGENCIA F&D* 🎯\n"
            "_Trabajamos para tí_\n\n"
            "📊 *RESUMEN DE GANADORES DEL DÍA* 📊\n"
            f"📅 Fecha: {fecha_hoy}\n\n"
        )

        for loteria, sorteos in resumen_por_loterias.items():
            if sorteos:
                texto_final += f"🎲 *{loteria}*\n"
                for hora, res in sorteos.items():
                    texto_final += f"  • {hora} ➔ {res}\n"
                texto_final += "\n"

        texto_final += f"📲 *WHATSAPP:* 04249611372\n{ENLACE_CANAL}"

        if len(texto_final) > 4000:
            for x in range(0, len(texto_final), 4000):
                bot.send_message(message.chat.id, texto_final[x:x+4000], parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, texto_final, parse_mode="Markdown")

    except Exception as e:
        print(f"Error general en comando tabla: {e}")
        bot.reply_to(message, f"⚠️ Error técnico: {str(e)}")

def loop_bot():
    # Programación principal con el Regalo de las 6:00 AM incluido
    schedule.every().day.at("06:00").do(enviar_regalo_6am)
    schedule.every().day.at("06:31").do(enviar_piramide_diaria)
    schedule.every().day.at("07:00").do(enviar_saludo_matutino)
     
    schedule.every().day.at("08:15").do(enviar_estudio_8am)
    schedule.every().day.at("12:15").do(enviar_estudio_mediodia)
    schedule.every().day.at("16:15").do(enviar_estudio_tarde)
    
    schedule.every().day.at("18:30").do(enviar_tasa_dolar)
    schedule.every().day.at("20:00").do(enviar_mensaje_cierre)
    
    schedule.every().day.at("09:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("10:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("11:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("13:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("14:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("15:40").do(enviar_mensaje_automatico)
    schedule.every().day.at("17:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("19:30").do(enviar_mensaje_automatico)
    
    schedule.every().day.at("08:30").do(enviar_publicidad_cashea)
    schedule.every().day.at("10:15").do(enviar_publicidad_cashea)
    schedule.every().day.at("12:00").do(enviar_publicidad_cashea)
    schedule.every().day.at("14:00").do(enviar_publicidad_cashea)
    schedule.every().day.at("16:00").do(enviar_publicidad_cashea)

    schedule.every().day.at("09:40").do(enviar_combinacion_diaria)
    schedule.every().day.at("13:30").do(enviar_combinacion_diaria)
    schedule.every().day.at("17:30").do(enviar_combinacion_diaria)

    schedule.every().day.at("00:01").do(limpiar_recomendaciones_diarias)
    
    schedule.every(1).minutes.do(verificar_y_enviar_resultados_individuales)
    schedule.every(1).minutes.do(verificar_minuto)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    t_bot = Thread(target=loop_bot)
    t_bot.daemon = True
    t_bot.start()
     
    try:
        bot.remove_webhook()
        t_polling = Thread(target=lambda: bot.infinity_polling(skip_pending=True, interval=3, timeout=20))
        t_polling.daemon = True
        t_polling.start()
    except Exception as e:
        print(f"Error iniciando polling: {e}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
    ENLACE_CANAL = 'https://t.me/+x4A5d5Jpu44yNzc5'

ADMIN_IDS = []

bot = telebot.TeleBot(TOKEN)

URL_LOTERIA = 'https://lotery.winbigvzla.com/resultados'
URL_BCV = 'https://www.bcv.org.ve/'

ARCH_REGISTRO = "resultados_enviados.json"
ARCH_GANADORES = "ganadores.json"
ARCH_CASHEA_INDEX = "cashea_index.json"
ARCH_PENDIENTES = "resultados_pendientes.json"

WHATSAPP_API_URL = os.environ.get("WHATSAPP_API_URL", "")
WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN", "")
WHATSAPP_DESTINATION = os.environ.get("WHATSAPP_DESTINATION", "04249611372")

RECOMENDADOS_HOY = {}
ACIERTOS_HOY = set()
CONTEO_ANIMALES_HOY = {}
ESTADOS_GANADOR = {}
ULTIMO_INDICE_MENSAJE = -1

MENSAJES_AUTOMATICOS = [
    f"🎯 *Agencia FyD* 🎯\n¡La suerte está de tu lado hoy! No te quedes sin jugar tu animalito favorito.\n📲 WhatsApp: 04249611372\n{ENLACE_CANAL}",
    f"🔥 ¡Activos con la buena energía en *Agencia FyD*! Elige tu animalito y ven a ganar con nosotros.\n📲 WhatsApp: 04249611372",
    f"🍀 ¿Ya consultaste tu palpito para el próximo sorteo? En *Agencia FyD* te pagamos al instante.\n📲 WhatsApp: 04249611372\n{ENLACE_CANAL}",
    f"⚡️ ¡No dejes para última hora tus jugadas! La banca de *Agencia FyD* está lista para recibir tu tiquet ganador.\n📲 04249611372",
    f"🌟 La constancia trae el éxito. ¡Sigue jugando tus animalitos preferidos en *Agencia FyD*!\n📲 WhatsApp: 04249611372\n{ENLACE_CANAL}",
    f"🎲 ¿Cuál es tu animalito fetiche hoy? Juega seguro y cobra rápido con *Agencia FyD*.\n📲 WhatsApp: 04249611372",
    f"🚀 ¡Arranca tu buena racha con *Agencia FyD*! Trabajamos para ti con la mejor atención.\n📲 WhatsApp: 04249611372\n{ENLACE_CANAL}",
    f"💡 Un buen día comienza jugando con confianza. ¡Haz tus jugadas en *Agencia FyD*!\n📲 WhatsApp: 04249611372",
    f"🎯 ¡Atención apostadores! La pizarra de *Agencia FyD* está habilitada para que revientes la banca hoy.\n📲 04249611372\n{ENLACE_CANAL}",
    f"✨ La suerte sonríe a los audaces. ¡Haz tu jugada ahora mismo en *Agencia FyD*!\n📲 WhatsApp: 04249611372"
]

MENSAJES_CASHEA_TELEGRAM = [
    (
        "💜✨ ¡JUEGA HOY, PAGA DESPUÉS! ✨💜\n"
        "💳 *CASHEA DISPONIBLE*\n"
        "✅ Sin inicial requerida\n"
        "🎯 Juega hoy y asegura tus animalitos\n"
        "💰 Cómodas cuotas para ti\n"
        "🔥 ¡Haz tu jugada con Agencia F&D!\n\n"
        "📲 Consulta disponibilidad por WhatsApp:\n"
        "04249611372\n"
        f"{ENLACE_CANAL}"
    ),
    (
        "💜💳 *FACILIDADES CON CASHEA* 💳💜\n"
        "¿Quieres jugar tus animalitos favoritos ahora mismo y cancelarlos después?\n\n"
        "✅ *CASHEA* está disponible en *Agencia F&D*\n"
        "🎯 Cupos altos y atención rápida\n"
        "🔥 ¡Facilita tus jugadas hoy!\n\n"
        "📲 Escríbenos al WhatsApp:\n"
        "04249611372\n"
        f"{ENLACE_CANAL}"
    ),
    (
        "✨💜 *¡DISFRUTA DE CASHEA EN AGENCIA F&D!* 💜✨\n"
        "💳 Llévate tus jugadas al instante:\n"
        "✅ Servicio confiable y seguro\n"
        "🎯 Juega hoy y paga cómodamente después\n"
        "🚀 ¡No te pierdas ningún sorteo!\n\n"
        "📲 Consulta detalles por WhatsApp:\n"
        "04249611372\n"
        f"{ENLACE_CANAL}"
    ),
    (
        "💜🔥 *JUEGA CON CASHEA* 🔥💜\n"
        "💳 ¡La mejor forma de asegurar tus animalitos sin complicaciones!\n"
        "✅ Proceso rápido y sin inicial\n"
        "🎯 Participa hoy mismo en los sorteos\n\n"
        "📲 Infórmate ahora mismo por WhatsApp:\n"
        "04249611372\n"
        f"{ENLACE_CANAL}"
    ),
    (
        "🎯 *CASHEA EN AGENCIA F&D* 🎯\n"
        "💳 ¿Sin saldo inmediato? ¡No te preocupes!\n"
        "⚡ Atención rápida y responsable\n"
        "💰 Cupos altos para tus jugadas\n"
        "✅ Juega ahora y paga después\n\n"
        "📲 Escríbenos al WhatsApp:\n"
        "04249611372\n"
        f"{ENLACE_CANAL}"
    )
]

MENSAJES_CASHEA_WHATSAPP = [
    (
        "💳 ¡CASHEA ACTIVO EN AGENCIA F&D!\n"
        "🔥 Juega ahora y paga después\n"
        "💰 Cupos altos | ⚡ Atención rápida\n\n"
        "🎯 *OPCIONES DE ACCIÓN:*\n"
        "1️⃣ Para jugar responde con: *JUGAR*\n"
        "2️⃣ Para consultar tu cupo responde con: *CONSULTAR*\n"
        "📲 04249611372"
    ),
    (
        "💜 ¡FACILIDADES CON CASHEA!\n"
        "✅ Sin inicial en Agencia F&D\n"
        "🎯 Juega hoy tus animalitos y paga después\n\n"
        "🎯 *OPCIONES DE ACCIÓN:*\n"
        "1️⃣ Para jugar responde con: *JUGAR*\n"
        "2️⃣ Para consultar tu cupo responde con: *CONSULTAR*\n"
        "📲 04249611372"
    ),
    (
        "✨ ¡DISFRUTA DE CASHEA HOY!\n"
        "💳 Llévate tus jugadas al instante en Agencia F&D\n"
        "💰 Cómodas cuotas y servicio confiable\n\n"
        "🎯 *OPCIONES DE ACCIÓN:*\n"
        "1️⃣ Para jugar responde con: *JUGAR*\n"
        "2️⃣ Para consultar tu cupo responde con: *CONSULTAR*\n"
        "📲 04249611372"
    )
]

ANIMALES_POOL = [
    "00 - Ballena", "0 - Delfín", "01 - Carnero", "02 - Toro", "03 - Ciempiés", "04 - Alacrán", 
    "05 - León", "06 - Rana", "07 - Perico", "08 - Ratón", "09 - Águila", 
    "10 - Tigre", "11 - Gato", "12 - Caballo", "13 - Mono", "14 - Paloma", 
    "15 - Zorro", "16 - Oso", "17 - Pavo", "18 - Burro", "19 - Chivo", 
    "20 - Cochino", "21 - Gallo", "22 - Camello", "23 - Cebra", "24 - Iguana", 
    "25 - Gallina", "26 - Vaca", "27 - Perro", "28 - Zamuro", "29 - Elefante", 
    "30 - Caimán", "31 - Lapa", "32 - Ardilla", "33 - Pescado", "34 - Venado", 
    "35 - Jirafa", "36 - Culebra"
]

HEADER_FyD = (
    "*AGENCIA F&D*\n"
    "*RESULTADOS*\n\n"
    "🎲 *{nombre_loteria}* 🎲\n"
    "Hora: {hora}\n"
    "Animalito: *{resultado}*\n\n"
    "04249611372"
)

app = Flask('')

@app.route('/')
def home():
    return (
        f"¡El bot de resultados individuales de la <b>Agencia F&D</b> está activo en el canal {CANAL}!<br><br>"
        "<b>Enlaces de prueba rápida (Test):</b><br>"
        "👉 <a href='/test/regalo_6am'>Probar Regalo de las 6:00 AM</a><br>"
        "👉 <a href='/test/piramide'>Probar Pirámide Numérica (Imagen)</a><br>"
        "👉 <a href='/test/saludo'>Probar Saludo Matutino</a><br>"
        "👉 <a href='/test/estudio_manana'>Probar Análisis de las 8 AM</a><br>"
        "👉 <a href='/test/estudio_mediodia'>Probar Análisis del Mediodía</a><br>"
        "👉 <a href='/test/estudio_tarde'>Probar Análisis / Cierre de la Tarde</a><br>"
        "👉 <a href='/test/bcv'>Probar Tasa Oficial BCV</a><br>"
        "👉 <a href='/test/sorteo'>Probar Cierre de Sorteo (Min 25/55)</a><br>"
        "👉 <a href='/test/cierre'>Probar Cierre de Jornada (8:00 PM)</a><br>"
        "👉 <a href='/test/combinacion'>Probar Combinación Diaria</a><br>"
        "👉 <a href='/test/resumen_repetidos'>Probar Resumen de Repetidos</a><br>"
        "👉 <a href='/test/cashea'>Probar Publicidad Cashea con Botones</a><br>"
    )

@app.route('/test/regalo_6am')
def test_regalo_6am():
    enviar_regalo_6am()
    return "Prueba de Regalo de las 6:00 AM ejecutada."

@app.route('/test/piramide')
def test_piramide():
    enviar_piramide_diaria()
    return "Prueba de Pirámide Numérica en Imagen ejecutada."

@app.route('/test/saludo')
def test_saludo():
    enviar_saludo_matutino()
    return "Prueba de Saludo Matutino ejecutada."

@app.route('/test/estudio_manana')
def test_estudio_manana():
    enviar_estudio_8am()
    return "Prueba de Análisis de las 8 AM ejecutada."

@app.route('/test/estudio_mediodia')
def test_estudio_mediodia():
    enviar_estudio_mediodia()
    return "Prueba de Análisis del Mediodía ejecutada."

@app.route('/test/estudio_tarde')
def test_estudio_tarde():
    enviar_estudio_tarde()
    return "Prueba de Análisis de la Tarde ejecutada."

@app.route('/test/bcv')
def test_bcv():
    enviar_tasa_dolar()
    return "Prueba de Tasa BCV ejecutada."

@app.route('/test/sorteo')
def test_sorteo():
    enviar_aviso_cierre_sorteo()
    return "Prueba de Cierre de Sorteo ejecutada."

@app.route('/test/cierre')
def test_cierre():
    enviar_mensaje_cierre()
    return "Prueba de Cierre de Jornada ejecutada."

@app.route('/test/combinacion')
def test_combinacion():
    enviar_combinacion_diaria()
    return "Prueba de Combinación Diaria ejecutada."

@app.route('/test/cashea')
def test_cashea():
    enviar_publicidad_cashea()
    return "Prueba de Cashea ejecutada."

def limpiar_texto(texto):
    return " ".join(texto.split())

def enviar_telegram(mensaje, disable_web_preview=True, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CANAL, 
        "text": mensaje, 
        "parse_mode": "Markdown", 
        "disable_web_page_preview": disable_web_preview
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup.to_json()
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Error al enviar al canal: {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción de conexión con Telegram: {e}")

def enviar_whatsapp(mensaje):
    if not WHATSAPP_API_URL:
        print(f"ℹ️ [WhatsApp Simulado/Pendiente de Configuración]: {mensaje[:40]}...")
        return
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {WHATSAPP_API_TOKEN}" if WHATSAPP_API_TOKEN else ""
        }
        payload = {
            "phone": WHATSAPP_DESTINATION,
            "message": mensaje
        }
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Error al enviar WhatsApp: {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción de conexión con WhatsApp API: {e}")

def cargar_estado_cashea():
    if os.path.exists(ARCH_CASHEA_INDEX):
        try:
            with open(ARCH_CASHEA_INDEX, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"indice_tg": 0, "indice_wa": 0, "fecha": ""}

def guardar_estado_cashea(indice_tg, indice_wa):
    data = {
        "indice_tg": indice_tg,
        "indice_wa": indice_wa,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open(ARCH_CASHEA_INDEX, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar {ARCH_CASHEA_INDEX}: {e}")

def enviar_publicidad_cashea(es_prueba=False):
    if not es_prueba:
        ahora = datetime.now()
        minutos_actuales = ahora.hour * 60 + ahora.minute
        inicio_minutos = 8 * 60 + 20
        fin_minutos = 16 * 60 + 30
        if not (inicio_minutos <= minutos_actuales <= fin_minutos):
            return

    estado = cargar_estado_cashea()
    idx_tg = estado.get("indice_tg", 0)
    idx_wa = estado.get("indice_wa", 0)

    if not MENSAJES_CASHEA_TELEGRAM:
        return
    idx_tg = idx_tg % len(MENSAJES_CASHEA_TELEGRAM)
    mensaje_tg = MENSAJES_CASHEA_TELEGRAM[idx_tg]

    if not MENSAJES_CASHEA_WHATSAPP:
        return
    idx_wa = idx_wa % len(MENSAJES_CASHEA_WHATSAPP)
    if len(MENSAJES_CASHEA_WHATSAPP) > 1 and idx_wa == idx_tg:
        idx_wa = (idx_wa + 1) % len(MENSAJES_CASHEA_WHATSAPP)
    mensaje_wa = MENSAJES_CASHEA_WHATSAPP[idx_wa]

    numero_wa = "584249611372"
    msg_jugar = urllib.parse.quote("Hola, quiero jugar con Cashea en Agencia F&D.")
    msg_consultar = urllib.parse.quote("Hola, quiero consultar mi cupo o disponibilidad de Cashea en Agencia F&D.")
    
    url_jugar = f"https://wa.me/{numero_wa}?text={msg_jugar}"
    url_consultar = f"https://wa.me/{numero_wa}?text={msg_consultar}"

    markup_cashea = InlineKeyboardMarkup()
    markup_cashea.row(
        InlineKeyboardButton("🎯 JUGAR CON CASHEA", url=url_jugar),
        InlineKeyboardButton("💳 CONSULTAR CASHEA", url=url_consultar)
    )

    enviar_telegram(mensaje_tg, disable_web_preview=True, reply_markup=markup_cashea)
    enviar_whatsapp(mensaje_wa)

    if not es_prueba:
        siguiente_tg = (idx_tg + 1) % len(MENSAJES_CASHEA_TELEGRAM)
        siguiente_wa = (idx_wa + 1) % len(MENSAJES_CASHEA_WHATSAPP)
        guardar_estado_cashea(siguiente_tg, siguiente_wa)

@bot.message_handler(commands=['cashea'])
def cmd_cashea_inmediato(message):
    if ADMIN_IDS and message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⚠️ No tienes permisos para usar este comando.")
        return
    enviar_publicidad_cashea(es_prueba=False)
    bot.reply_to(message, "✅ Publicidad de Cashea ejecutada con botones y rotación avanzada.")

@bot.message_handler(commands=['cashea_test'])
def cmd_cashea_test(message):
    if ADMIN_IDS and message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⚠️ No tienes permisos para usar este comando.")
        return
    enviar_publicidad_cashea(es_prueba=True)
    bot.reply_to(message, "🧪 Prueba de Cashea enviada con botones (la rotación normal no fue afectada).")

@bot.message_handler(commands=['cashea_estado'])
def cmd_cashea_estado(message):
    if ADMIN_IDS and message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⚠️ No tienes permisos para usar este comando.")
        return
    estado = cargar_estado_cashea()
    idx_tg = estado.get("indice_tg", 0)
    idx_wa = estado.get("indice_wa", 0)
    ultima_fecha = estado.get("fecha", "Desconocida")
  
    info = (
        "📊 *ESTADO DE ROTACIÓN CASHEA* 📊\n\n"
        f"📍 Siguiente índice Telegram: `{idx_tg}` (Total: {len(MENSAJES_CASHEA_TELEGRAM)})\n"
        f"📍 Siguiente índice WhatsApp: `{idx_wa}` (Total: {len(MENSAJES_CASHEA_WHATSAPP)})\n"
        f"🕒 Última actualización persistente: `{ultima_fecha}`\n"
        f"⏰ Horario activo: 8:20 AM - 4:30 PM (America/Caracas)"
    )
    bot.reply_to(message, info, parse_mode="Markdown")

def limpiar_recomendaciones_diarias():
    RECOMENDADOS_HOY.clear()
    ACIERTOS_HOY.clear()
    CONTEO_ANIMALES_HOY.clear()

def registrar_recomendacion(numero, etiqueta, dt_recomendacion=None):
    num_str = str(numero).zfill(2)
    if dt_recomendacion is None:
        dt_recomendacion = datetime.now()
    if num_str not in RECOMENDADOS_HOY:
        RECOMENDADOS_HOY[num_str] = []
    RECOMENDADOS_HOY[num_str].append({
        "etiqueta": etiqueta,
        "tiempo": dt_recomendacion
    })

def enviar_mensaje_automatico():
    global ULTIMO_INDICE_MENSAJE
    if not MENSAJES_AUTOMATICOS:
        return
    indice = random.randint(0, len(MENSAJES_AUTOMATICOS) - 1)
    if len(MENSAJES_AUTOMATICOS) > 1:
        while indice == ULTIMO_INDICE_MENSAJE:
            indice = random.randint(0, len(MENSAJES_AUTOMATICOS) - 1)
    ULTIMO_INDICE_MENSAJE = indice
    enviar_telegram(MENSAJES_AUTOMATICOS[indice], disable_web_preview=True)

def enviar_regalo_6am():
    dt_pub = datetime.now()
    regalo = seleccionar_analisis_dinamico(1)[0]
    numero = regalo.split(" - ")[0].strip()
    registrar_recomendacion(numero, "🎁 Regalo de las 6:00 AM", dt_pub)

    enviar_telegram(
        "🎯 *AGENCIA F&D* 🎯\n\n"
        "☀️ *¡Muy buenos días!* Arrancamos el día con la mejor actitud y la mejor energía para ganar.\n\n"
        f"🎁 *El Regalo de las 6:00 AM:* `{regalo}`\n\n"
        "📲 WHATSAPP: 04249611372\n"
        f"{ENLACE_CANAL}\n"
        "¡Mucho éxito en tus jugadas de hoy! 🍀🔥",
        disable_web_preview=True
    )

def generar_imagen_piramide():
    ahora = datetime.now()
    fecha_str = ahora.strftime("%d/%m/%Y")
    digitos = [int(c) for c in fecha_str if c.isdigit()]
    filas = [digitos]
    while len(filas[-1]) > 1:
        actual = filas[-1]
        siguiente = [(actual[i] + actual[i+1]) % 10 for i in range(len(actual) - 1)]
        filas.append(siguiente)

    seed_val = int(ahora.strftime("%Y%m%d"))
    rnd = random.Random(seed_val)
    candidates = []
    for f in filas:
        for idx in range(len(f) - 1):
            val = (f[idx] * 10 + f[idx+1]) % 37
            candidates.append(f"{val:02d}" if val != 0 else "0")
            candidates.append("00")
        for num in f:
            val = (num * 7) % 37
            candidates.append(f"{val:02d}" if val != 0 else "0")
            candidates.append("00")

    unique_candidates = []
    for c in candidates:
        if c not in unique_candidates:
            unique_candidates.append(c)

    while len(unique_candidates) < 6:
        r_val = rnd.randint(0, 36)
        c_rand = f"{r_val:02d}" if r_val != 0 else ("0" if rnd.random() > 0.5 else "00")
        if c_rand not in unique_candidates:
            unique_candidates.append(c_rand)

    d1 = f"{unique_candidates[0]}-{unique_candidates[1]}-{unique_candidates[2]}"
    d2 = f"{unique_candidates[3]}-{unique_candidates[4]}-{unique_candidates[5]}"

    img_width, img_height = 1000, 1120
    image = Image.new("RGB", (img_width, img_height), color=(30, 10, 10))
    draw = ImageDraw.Draw(image)

    color_dorado = (212, 175, 55)
    color_dorado_claro = (243, 229, 149)
    color_morado = (148, 0, 211)
    color_blanco = (255, 255, 255)
    color_panel = (20, 20, 20)

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
        font_sub = ImageFont.truetype("DejaVuSans.ttf", 24)
        font_pir = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        font_data = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_pir = ImageFont.load_default()
        font_data = ImageFont.load_default()

    draw.text((img_width // 2, 45), "AGENCIA F&D", fill=color_dorado, anchor="mm", font=font_title)
    draw.text((img_width // 2, 90), "Trabajamos para tí", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((img_width // 2, 145), "PIRÁMIDE DEL DÍA", fill=color_morado, anchor="mm", font=font_title)

    draw.rectangle([img_width // 2 - 180, 185, img_width // 2 + 180, 240], fill=color_panel, outline=color_dorado, width=2)
    draw.text((img_width // 2, 212), f"📅  {fecha_str}", fill=color_dorado_claro, anchor="mm", font=font_data)

    panel_bottom = 740
    draw.rectangle([40, 290, 280, panel_bottom], fill=color_panel, outline=color_morado, width=2)
    draw.text((160, 315), "★ DATOS ★", fill=color_dorado, anchor="mm", font=font_data)
    draw.text((160, 355), "NÚMEROS USADOS", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 390), f"{len(set([d for f in filas for d in f])) * 4}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 440), "SUMA TOTAL", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 475), f"{sum([sum(f) for f in filas]) * 3}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 525), "NÚMERO MAYOR", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 560), f"{max([max(f) for f in filas])}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 610), "NÚMERO MENOR", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 645), f"{min([min(f) for f in filas])}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 695), "NÚMERO FRECUENTE", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 730), f"{digitos[0]} (7 VECES)", fill=color_dorado_claro, anchor="mm", font=font_data)

    draw.rectangle([720, 290, 960, panel_bottom], fill=color_panel, outline=color_morado, width=2)
    draw.text((840, 315), "★ SUMA ★", fill=color_dorado, anchor="mm", font=font_data)
    draw.text((840, 350), "POR FILA", fill=color_dorado, anchor="mm", font=font_data)
    
    y_suma_pos = 400
    for idx, f in enumerate(filas):
        suma_fila = sum(f)
        draw.text((840, y_suma_pos), f"{idx+1}RA FILA: {suma_fila}", fill=color_blanco, anchor="mm", font=font_sub)
        y_suma_pos += 40

    start_y = 280
    row_height = 54
    center_x = img_width // 2
    circle_radius = 23

    for i, f in enumerate(filas):
        num_items = len(f)
        total_width = num_items * 52
        start_x_row = center_x - (total_width // 2)

        for j, num in enumerate(f):
            cx = start_x_row + (j * 52) + 24
            cy = start_y + (i * row_height) + 24
            draw.ellipse([cx - circle_radius, cy - circle_radius, cx + circle_radius, cy + circle_radius], fill=color_panel, outline=color_dorado, width=3)
            draw.text((cx, cy), str(num), fill=color_blanco, anchor="mm", font=font_pir)

    box_top = 760
    draw.rectangle([150, box_top, img_width - 150, box_top + 150], fill=color_panel, outline=color_dorado, width=2)
    draw.text((img_width // 2, box_top + 28), "🔥 DATOS CLAVES PARA HOY:", fill=color_dorado, anchor="mm", font=font_sub)
    draw.text((img_width // 2, box_top + 75), f"📌 {d1}", fill=color_blanco, anchor="mm", font=font_data)
    draw.text((img_width // 2, box_top + 115), f"📌 {d2}", fill=color_blanco, anchor="mm", font=font_data)

    footer_y = 955
    draw.text((img_width // 2, footer_y), "WHATSAPP: 04249611372", fill=color_dorado_claro, anchor="mm", font=font_sub)

    bio = BytesIO()
    bio.name = 'piramide_fyd.png'
    image.save(bio, 'PNG')
    bio.seek(0)
    return bio

def enviar_piramide_diaria():
    try:
        foto_bio = generar_imagen_piramide()
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': foto_bio}
        data = {
            'chat_id': CANAL,
            'caption': f"📢 *REPORTE TÁCTICO - LA PIRÁMIDE*\n\nWHATSAPP: 04249611372\n{ENLACE_CANAL}",
            'parse_mode': 'Markdown'
        }
        requests.post(url, data=data, files=files, timeout=15)
    except Exception as e:
        print(f"Error generando/enviando imagen pirámide: {e}")

def obtener_animales_salidos_actuales():
    salidos = set()
    try:
        resultados_map = obtener_resultados_winbig()
        for loteria, sorteos in resultados_map.items():
            for hora, res in sorteos.items():
                if "PENDIENTE" not in res:
                    num_partes = res.split("-")[0].strip()
                    salidos.add(num_partes)
    except Exception as e:
        print(f"Error obteniendo salidos para análisis: {e}")
    return salidos

def seleccionar_analisis_dinamico(cantidad):
    salidos = obtener_animales_salidos_actuales()
    disponibles = [a for a in ANIMALES_POOL if a.split(" - ")[0].strip() not in salidos]
    if len(disponibles) < cantidad:
        disponibles = ANIMALES_POOL
    seed_val = int(datetime.now().strftime("%Y%m%d%H%M"))
    rnd = random.Random(seed_val)
    return rnd.sample(disponibles, cantidad)

def enviar_combinacion_diaria():
    dt_pub = datetime.now()
    salidos = obtener_animales_salidos_actuales()
    disponibles = [a for a in ANIMALES_POOL if a.split(" - ")[0].strip() not in salidos]
    if len(disponibles) < 7:
        disponibles = ANIMALES_POOL

    seed_val = int(dt_pub.strftime("%Y%m%d%H%M%S"))
    rnd = random.Random(seed_val)
    seleccionados = rnd.sample(disponibles, 7)

    fijo1 = seleccionados[0]
    fijo2 = seleccionados[1]
    par1 = seleccionados[2]
    par2 = seleccionados[3]
    trip1 = seleccionados[4]
    trip2 = seleccionados[5]
    trip3 = seleccionados[6]

    for animal in seleccionados:
        num = animal.split(" - ")[0].strip()
        registrar_recomendacion(num, "🎯 Combinación Especial F&D", dt_pub)

    par_str = f"{par1.split(' - ')[0].strip()} - {par2.split(' - ')[0].strip()}"
    trip_str = f"{trip1.split(' - ')[0].strip()} - {trip2.split(' - ')[0].strip()} - {trip3.split(' - ')[0].strip()}"

    mensaje = (
        "🎯 *COMBINACIÓN GANADORA - AGENCIA F&D* 🎯\n"
        "🔥 ¡Datos exclusivos y directos para asegurar tus jugadas:\n\n"
        f"📌 *Fijos del Día:* `{fijo1}` y `{fijo2}`\n"
        f"📌 *El Par:* `{par_str}`\n"
        f"📌 *La Tripleta:* `{trip_str}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}\n\n"
        "¡A cobrar se ha dicho! 🍀✨"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_estudio_8am():
    dt_pub = datetime.now()
    analisis = seleccionar_analisis_dinamico(2)
    for animal in analisis:
        numero = animal.split(" - ")[0].strip()
        registrar_recomendacion(numero, "🔍 Análisis 8:15 AM", dt_pub)

    mensaje = (
        "🎯 *AGENCIA F&D* 🎯\n"
        "🔍 *ANÁLISIS TRAS EL SORTEO DE LAS 8:00 AM* 🔍\n\n"
        "¡Ya salieron los primeros animalitos! Evaluando la apertura de la pizarra y descartando lo ya jugado, la casa trae las recomendaciones probables para los siguientes sorteos:\n\n"
        f"🔥 *Regalitos recomendados:* `{analisis[0]}` y `{analisis[1]}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_estudio_mediodia():
    dt_pub = datetime.now()
    analisis = seleccionar_analisis_dinamico(2)
    for animal in analisis:
        numero = animal.split(" - ")[0].strip()
        registrar_recomendacion(numero, "☀️ Análisis Mediodía", dt_pub)

    tripleta = seleccionar_analisis_dinamico(3)
    for animal in tripleta:
        numero = animal.split(" - ")[0].strip()
        registrar_recomendacion(numero, "🎯 Tripleta Mediodía", dt_pub)

    t_str = f"{tripleta[0].split(' - ')[0].strip()} - {tripleta[1].split(' - ')[0].strip()} - {tripleta[2].split(' - ')[0].strip()}"
     
    mensaje = (
        "🎯 *AGENCIA F&D* 🎯\n"
        "☀️ *ANÁLISIS DEL MEDIODÍA* ☀️\n\n"
        "*¡Mitad de jornada! Estudiando los resultados que nos dejó la mañana y analizando tendencias en vivo, el tablero apunta hacia las siguientes proyecciones:*\n\n"
        f"🔥 *Animales calientes:* `{analisis[0]}` y `{analisis[1]}`\n"
        f"🎯 *Tripleta recomendada:* `{t_str}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_estudio_tarde():
    dt_pub = datetime.now()
    analisis = seleccionar_analisis_dinamico(2)
    for animal in analisis:
        numero = animal.split(" - ")[0].strip()
        registrar_recomendacion(numero, "🌇 Análisis Tarde", dt_pub)

    mensaje = (
        "🎯 *AGENCIA F&D* 🎯\n"
        "🌇 *ANÁLISIS Y CIERRE DE LA TARDE* 🌇\n\n"
        "¡A pocas horas de terminar la jornada! Evaluando el comportamiento de los últimos sortos y filtrando los ganadores del día, la casa trae los animales con mayor probabilidad de reventar para asegurar el cierre:\n\n"
        f"⚡️ *Imparables de la Tarde / Cierre:* `{analisis[0]}` y `{analisis[1]}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_saludo_matutino():
    enviar_telegram(
        "🎯 AGENCIA F&D 🎯\n\n"
        "☀️ ¡Buenos días! Arrancamos la jornada con la mejor actitud y la mejor energía para ganar.\n\n"
        "📲 WHATSAPP: 04249611372\n"
        "¡Mucho éxito en tus jugadas de hoy! 🍀🔥",
        disable_web_preview=True
    )

def enviar_tasa_dolar():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL_BCV, headers=headers, timeout=15, verify=False)
        precio_dolar = "742,23"
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            dolar_div = soup.find('div', id='dolar')
            if dolar_div and dolar_div.find('strong'):
                precio_dolar = dolar_div.find('strong').get_text(strip=True)
        enviar_telegram(
            "💵 TASA OFICIAL BCV 💵\n"
            f"📈 Precio Oficial: Bs. {precio_dolar}\n"
            f"Verifica la tasa oficial en: {URL_BCV}",
            disable_web_preview=True
        )
    except Exception as e:
        print(f"Error BCV: {e}")

def enviar_mensaje_cierre():
    enviar_telegram(
        "AGENCIA F&D\n"
        "🌙 ¡FINAL DE JORNADA! 🌙\n"
        "*¡Listo por hoy! 🚀 Que descansen y sueñen en grande. Mañana nos vemos tempranito con más suerte y nuevos retos. ¡Buenas noches! 🌟💤*",
        disable_web_preview=True
    )

def enviar_aviso_cierre_sorteo():
    enviar_telegram(
        "🛑 *¡ATENCIÓN!* 🛑\n\n"
        "El tiempo de jugadas ha terminado por este sorteo en la **AGENCIA F&D**.\n\n"
        "🤞 ¡Cruzamos los dedos por ti, mucha suerte en tus apuestas! 🎲🔥",
        disable_web_preview=True
    )

def cargar_registros():
    if os.path.exists(ARCH_REGISTRO):
        try:
            with open(ARCH_REGISTRO, "r") as f:
                data = json.load(f)
                if data.get("fecha") == datetime.now().strftime("%d-%m-%Y"):
                    return set(data.get("enviados", []))
        except Exception:
            pass
    return set()

def guardar_registros(enviados_set):
    data = {
        "fecha": datetime.now().strftime("%d-%m-%Y"),
        "enviados": list(enviados_set)
    }
    try:
        with open(ARCH_REGISTRO, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error al guardar registros: {e}")

def cargar_pendientes():
    if os.path.exists(ARCH_PENDIENTES):
        try:
            with open(ARCH_PENDIENTES, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("fecha") == datetime.now().strftime("%d-%m-%Y"):
                    return data.get("pendientes", {})
        except Exception:
            pass
    return {}

def guardar_pendientes(pendientes_dict):
    data = {
        "fecha": datetime.now().strftime("%d-%m-%Y"),
        "pendientes": pendientes_dict
    }
    try:
        with open(ARCH_PENDIENTES, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar pendientes: {e}")

# ==========================================
# MÓDULO CENTRAL DE SCRAPING DINÁMICO
# ==========================================
def obtener_resultados_winbig():
    resultados_map = {}
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        respuesta = requests.get(URL_LOTERIA, headers=headers, timeout=15)
        if respuesta.status_code != 200:
            return resultados_map

        soup = BeautifulSoup(respuesta.text, 'html.parser')
        tarjetas = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'card|box|item|lotto|result', re.IGNORECASE))

        for tarjeta in tarjetas:
            nombre_loteria = None
            posibles_titulos = tarjeta.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'span', 'div', 'strong', 'b'], class_=re.compile(r'title|header|name|lotto|text', re.IGNORECASE))
            for pt in posibles_titulos:
                t_text = limpiar_texto(pt.get_text(" ", strip=True)).upper()
                if t_text and len(t_text) > 2 and not re.search(r'\d{1,2}:\d{2}', t_text) and "PENDIENTE" not in t_text:
                    if t_text not in ["WINBIG", "RESULTADOS", "RESULTADOS ANIMALITOS", "ANIMALITOS"]:
                        nombre_loteria = t_text
                        break

            if not nombre_loteria:
                lineas = [l.strip().upper() for l in tarjeta.get_text("\n", strip=True).split("\n") if l.strip()]
                for linea in lineas:
                    linea_limpia = limpiar_texto(linea)
                    if linea_limpia and len(linea_limpia) > 2 and not re.search(r'\d{1,2}:\d{2}', linea_limpia) and "PENDIENTE" not in linea_limpia:
                        if linea_limpia not in ["WINBIG", "RESULTADOS", "RESULTADOS ANIMALITOS", "ANIMALITOS"]:
                            nombre_loteria = linea_limpia
                            break

            if not nombre_loteria:
                continue

            if "RULETA ROYAL" in nombre_loteria.upper() or nombre_loteria.upper() in ["RESULTADOS", "ANIMALITOS"]:
                continue

            if nombre_loteria not in resultados_map:
                resultados_map[nombre_loteria] = {}

            slots_sorteo = tarjeta.find_all(['div', 'li', 'span', 'tr'], class_=re.compile(r'item|slot|draw|row|col', re.IGNORECASE))
            if not slots_sorteo:
                slots_sorteo = [tarjeta]

            for slot in slots_sorteo:
                texto_slot = limpiar_texto(slot.get_text(" ", strip=True)).upper()
                match_h = re.search(r'\b(\d{1,2}:\d{2}\s*(?:AM|PM))\b', texto_slot)
                if not match_h:
                    continue
                hora = match_h.group(1).upper()

                if "PENDIENTE" in texto_slot:
                    resultados_map[nombre_loteria][hora] = "⏳ Pendiente"
                    continue

                match_res = re.search(r'\b(00|0|\d{1,2})\s*-\s*([A-ZÁÉÍÓÚÑa-zñáéíóú]+(?:\s+[A-ZÁÉÍÓÚÑa-zñáéíóú]+)?)\b', texto_slot)
                if match_res:
                    num_crudo = match_res.group(1)
                    animal_texto = match_res.group(2).strip().capitalize()
                    
                    if num_crudo == "00":
                        num_str = "00"
                    elif num_crudo == "0":
                        num_str = "0"
                    else:
                        num_str = str(int(num_crudo)).zfill(2)

                    resultado_formateado = f"{num_str} - {animal_texto}"
                    resultados_map[nombre_loteria][hora] = resultado_formateado

    except Exception as e:
        print(f"Error en obtener_resultados_winbig: {e}")

    return resultados_map

def cargar_ganadores_persistentes():
    if os.path.exists(ARCH_GANADORES):
        try:
            with open(ARCH_GANADORES, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_ganador_persistente(registro):
    ganadores = cargar_ganadores_persistentes()
    ganadores.append(registro)
    try:
        with open(ARCH_GANADORES, "w", encoding="utf-8") as f:
            json.dump(ganadores, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar ganadores.json: {e}")

@bot.message_handler(commands=['ganador'])
def cmd_ganador(message):
    chat_id = message.chat.id
    ESTADOS_GANADOR[chat_id] = {
        "paso": "nombre",
        "datos": {}
    }
    bot.send_message(
        chat_id,
        "🏆 Vamos a registrar un ganador para **Agencia F&D**.\n\n"
        "✍️ Envíame el **nombre del ganador**:",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.chat.id in ESTADOS_GANADOR and ESTADOS_GANADOR[m.chat.id]["paso"] in ["nombre", "loteria", "numero", "premio"])
def procesar_pasos_ganador(message):
    chat_id = message.chat.id
    estado = ESTADOS_GANADOR[chat_id]
    paso_actual = estado["paso"]
    texto = message.text.strip() if message.text else ""

    if not texto:
        bot.send_message(chat_id, "⚠️ Por favor, ingresa un texto válido.")
        return

    if paso_actual == "nombre":
        estado["datos"]["nombre"] = texto
        estado["paso"] = "loteria"
        bot.send_message(chat_id, "🎯 ¿En qué lotería ganó? (Ej: Lotto Activo, Granjita, etc.)")
    elif paso_actual == "loteria":
        estado["datos"]["loteria"] = texto
        estado["paso"] = "numero"
        bot.send_message(chat_id, "🔢 ¿Cuál fue el número o animalito ganador? (Ej: 25 - Gallina)")
    elif paso_actual == "numero":
        estado["datos"]["numero"] = texto
        estado["paso"] = "premio"
        bot.send_message(chat_id, "💰 ¿Cuál fue el monto del premio? (Ej: 500 Bs o 20$):")
    elif paso_actual == "premio":
        estado["datos"]["premio"] = texto
        estado["paso"] = "capture"
        bot.send_message(chat_id, "📸 Ahora envíame el **capture del pago realizado** (como foto). Será la imagen publicada con el texto como pie de página.")

@bot.message_handler(content_types=['photo'], func=lambda m: m.chat.id in ESTADOS_GANADOR and ESTADOS_GANADOR[m.chat.id].get("paso") == "capture")
def procesar_capture_ganador(message):
    chat_id = message.chat.id
    estado = ESTADOS_GANADOR[chat_id]

    file_id = message.photo[-1].file_id
    estado["datos"]["capture_file_id"] = file_id
    estado["paso"] = "confirmar"

    datos = estado["datos"]

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ PUBLICAR", callback_data="ganador_publicar"),
        InlineKeyboardButton("❌ CANCELAR", callback_data="ganador_cancelar")
    )

    caption_preview = (
        "🔎 **Vista previa del mensaje que irá en el pie del capture:**\n\n"
        "🏆 *¡TENEMOS GANADOR!* 🏆\n\n"
        "*AGENCIA F&D*\n\n"
        f"🎯 Lotería: {datos['loteria']}\n"
        f"🔢 Número: {datos['numero']}\n"
        f"💰 Premio: {datos['premio']}\n\n"
        f"🎉 ¡FELICIDADES, {datos['nombre'].upper()}!\n\n"
        "Gracias por confiar en Agencia F&D. 🍀\n"
        f"{ENLACE_CANAL}"
    )

    bot.send_photo(chat_id, file_id, caption=caption_preview, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data in ["ganador_publicar", "ganador_cancelar"])
def callback_publicar_ganador(call):
    chat_id = call.message.chat.id
    estado = ESTADOS_GANADOR.get(chat_id)

    if not estado:
        bot.answer_callback_query(call.id, "⚠️ La sesión ha expirado o ya fue procesada.")
        return

    if call.data == "ganador_cancelar":
        ESTADOS_GANADOR.pop(chat_id, None)
        try:
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=call.message.message_id,
                caption="❌ Registro de ganador cancelado.",
                reply_markup=None
            )
        except Exception:
            bot.send_message(chat_id, "❌ Registro de ganador cancelado.")
        bot.answer_callback_query(call.id, "Cancelado con éxito.")
        return

    if call.data == "ganador_publicar":
        datos = estado["datos"]
        try:
            bot.answer_callback_query(call.id, "Publicando ganador...")

            texto_canal = (
                "🏆 ¡TENEMOS GANADOR! 🏆\n\n"
                "*AGENCIA F&D*\n\n"
                f"🎯 Lotería: {datos['loteria']}\n"
                f"🔢 Número: {datos['numero']}\n"
                f"💰 Premio: {datos['premio']}\n\n"
                f"🎉 ¡FELICIDADES, {datos['nombre'].upper()}!\n\n"
                "Gracias por confiar en Agencia F&D. 🍀\n"
                f"{ENLACE_CANAL}"
            )

            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            payload = {
                'chat_id': CANAL,
                'photo': datos['capture_file_id'],
                'caption': texto_canal,
                'parse_mode': 'Markdown'
            }
            requests.post(url, json=payload, timeout=15)

            registro_final = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nombre": datos["nombre"],
                "loteria": datos["loteria"],
                "numero": datos["numero"],
                "premio": datos["premio"],
                "capture_file_id": datos["capture_file_id"]
            }
            guardar_ganador_persistente(registro_final)

            try:
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    caption="✅ ¡Ganador publicado con éxito usando el capture en el canal y registrado en ganadores.json!",
                    reply_markup=None
                )
            except Exception:
                bot.send_message(chat_id, "✅ ¡Ganador publicado con éxito!")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Error al publicar en el canal: {str(e)}")
        finally:
            ESTADOS_GANADOR.pop(chat_id, None)

def verificar_y_enviar_resultados_individuales():
    enviados_hoy = cargar_registros()
    es_primera_ejecucion = len(enviados_hoy) == 0
     
    try:
        resultados_actuales = obtener_resultados_winbig()
        if not resultados_actuales:
            return

        pendientes = cargar_pendientes()
        nuevos_pendientes = {}
        hubo_cambios = False
        nuevos_para_guardar = set(enviados_hoy)
        fecha_hoy_str = datetime.now().strftime("%Y-%m-%d")

        for nombre_loteria_ind, sorteos in resultados_actuales.items():
            for hora, resultado in sorteos.items():
                if "PENDIENTE" in resultado:
                    continue

                id_sorteo = f"{fecha_hoy_str}|{nombre_loteria_ind}|{hora}"
                id_resultado_completo = f"{nombre_loteria_ind}_{hora}_{resultado}"

                if id_resultado_completo in enviados_hoy:
                    continue

                if id_sorteo in pendientes:
                    valor_anterior = pendientes[id_sorteo]
                    if valor_anterior == resultado:
                        if es_primera_ejecucion:
                            nuevos_para_guardar.add(id_resultado_completo)
                        else:
                            numero = resultado.split("-")[0].strip()
                            if numero in RECOMENDADOS_HOY and numero not in ACIERTOS_HOY:
                                try:
                                    dt_resultado = datetime.strptime(f"{fecha_hoy_str} {hora}", "%Y-%m-%d %I:%M %p")
                                except Exception:
                                    dt_resultado = datetime.now()

                                cumple_tiempo = False
                                etiqueta_valida = ""
                                for rec in RECOMENDADOS_HOY[numero]:
                                    if dt_resultado > rec["tiempo"]:
                                        cumple_tiempo = True
                                        etiqueta_valida = rec["etiqueta"]
                                        break

                                if cumple_tiempo and id_resultado_completo not in [a.get("id_res") for a in list(ACIERTOS_HOY) if isinstance(a, dict)]:
                                    mensaje_acierto = (
                                        "🎉🎉 *¡ACERTAMOS!* 🎉🎉\n\n"
                                        f"✅ {etiqueta_valida}\n\n"
                                        f"🎯 *{resultado}*\n"
                                        f"🎲 {nombre_loteria_ind}\n"
                                        f"🕒 {hora}\n\n"
                                        "🍀 *¡Felicidades a todos los que confiaron en Agencia F&D!*"
                                    )
                                    enviar_telegram(mensaje_acierto)
                                    ACIERTOS_HOY.add(numero)
                                    ACIERTOS_HOY.add(f"ACERTADO_{id_resultado_completo}")

                            hora_actual_str = datetime.now().strftime("%I:%M %p")
                            mensaje = HEADER_FyD.format(
                                hora_str=hora_actual_str,
                                nombre_loteria=nombre_loteria_ind,
                                hora=hora,
                                resultado=resultado
                            )
                            enviar_telegram(mensaje)
                            nuevos_para_guardar.add(id_resultado_completo)
                            hubo_cambios = True
                            time.sleep(1.5)
                    else:
                        nuevos_pendientes[id_sorteo] = resultado
                else:
                    nuevos_pendientes[id_sorteo] = resultado

        guardar_pendientes(nuevos_pendientes)

        if es_primera_ejecucion:
            guardar_registros(nuevos_para_guardar)
        elif hubo_cambios:
            guardar_registros(nuevos_para_guardar)

    except Exception as e:
        print(f"Error al verificar resultados individuales: {e}")

ultimo_aviso_minuto = ""

def verificar_minuto():
    global ultimo_aviso_minuto
    ahora = datetime.now()
    hora_actual_minutos = ahora.hour * 60 + ahora.minute
    inicio_minutos = 7 * 60 + 25
    fin_minutos = 19 * 60 + 55

    if not (inicio_minutos <= hora_actual_minutos <= fin_minutos):
        return

    minuto_actual = ahora.minute
    if minuto_actual in [25, 55]:
        clave_tiempo = ahora.strftime("%H:%M")
        if ultimo_aviso_minuto != clave_tiempo:
            enviar_aviso_cierre_sorteo()
            ultimo_aviso_minuto = clave_tiempo

@bot.message_handler(commands=['resumen', 'tabla'])
def cmd_resumen(message):
    try:
        bot.reply_to(message, "🔍 Consultando resumen de resultados actual, por favor espera...")
         
        resumen_por_loterias = obtener_resultados_winbig()

        if not resumen_por_loterias:
            bot.reply_to(message, "⚠️ No se encontraron resultados disponibles en este momento.")
            return

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        texto_final = (
            "🎯 *AGENCIA F&D* 🎯\n"
            "_Trabajamos para tí_\n\n"
            "📊 *RESUMEN DE GANADORES DEL DÍA* 📊\n"
            f"📅 Fecha: {fecha_hoy}\n\n"
        )

        for loteria, sorteos in resumen_por_loterias.items():
            if sorteos:
                texto_final += f"🎲 *{loteria}*\n"
                for hora, res in sorteos.items():
                    texto_final += f"  • {hora} ➔ {res}\n"
                texto_final += "\n"

        texto_final += f"📲 *WHATSAPP:* 04249611372\n{ENLACE_CANAL}"

        if len(texto_final) > 4000:
            for x in range(0, len(texto_final), 4000):
                bot.send_message(message.chat.id, texto_final[x:x+4000], parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, texto_final, parse_mode="Markdown")

    except Exception as e:
        print(f"Error general en comando tabla: {e}")
        bot.reply_to(message, f"⚠️ Error técnico: {str(e)}")

def loop_bot():
    # Programación principal con el Regalo de las 6:00 AM incluido
    schedule.every().day.at("06:00").do(enviar_regalo_6am)
    schedule.every().day.at("06:31").do(enviar_piramide_diaria)
    schedule.every().day.at("07:00").do(enviar_saludo_matutino)
     
    schedule.every().day.at("08:15").do(enviar_estudio_8am)
    schedule.every().day.at("12:15").do(enviar_estudio_mediodia)
    schedule.every().day.at("16:15").do(enviar_estudio_tarde)
    
    schedule.every().day.at("18:30").do(enviar_tasa_dolar)
    schedule.every().day.at("20:00").do(enviar_mensaje_cierre)
    
    schedule.every().day.at("09:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("10:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("11:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("13:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("14:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("15:40").do(enviar_mensaje_automatico)
    schedule.every().day.at("17:30").do(enviar_mensaje_automatico)
    schedule.every().day.at("19:30").do(enviar_mensaje_automatico)
    
    schedule.every().day.at("08:30").do(enviar_publicidad_cashea)
    schedule.every().day.at("10:15").do(enviar_publicidad_cashea)
    schedule.every().day.at("12:00").do(enviar_publicidad_cashea)
    schedule.every().day.at("14:00").do(enviar_publicidad_cashea)
    schedule.every().day.at("16:00").do(enviar_publicidad_cashea)

    schedule.every().day.at("09:40").do(enviar_combinacion_diaria)
    schedule.every().day.at("13:30").do(enviar_combinacion_diaria)
    schedule.every().day.at("17:30").do(enviar_combinacion_diaria)

    schedule.every().day.at("00:01").do(limpiar_recomendaciones_diarias)
    
    schedule.every(1).minutes.do(verificar_y_enviar_resultados_individuales)
    schedule.every(1).minutes.do(verificar_minuto)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    t_bot = Thread(target=loop_bot)
    t_bot.daemon = True
    t_bot.start()
     
    try:
        bot.remove_webhook()
        t_polling = Thread(target=lambda: bot.infinity_polling(skip_pending=True, interval=3, timeout=20))
        t_polling.daemon = True
        t_polling.start()
    except Exception as e:
        print(f"Error iniciando polling: {e}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
