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
import traceback

# Desactivar advertencias de certificados SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CONFIGURACIÓN DE CREDENCIALES Y ENLACES (FyD)
# ==========================================
TOKEN = '7691909067:AAG4EdkF0-_lpefI9ewFpo6AMhqawBZztAM'
CANAL = '@agenciafyd'
ENLACE_CANAL = 'https://t.me/+x4A5d5Jpu44yNzc5'

bot = telebot.TeleBot(TOKEN)

URL_LOTERIA = 'https://lotery.winbigvzla.com/resultados'
URL_BCV = 'https://www.bcv.org.ve/'

# Archivo local para control de registros persistentes y evitar duplicados
ARCH_REGISTRO = "resultados_enviados.json"
ARCH_TABLAS_REGISTRO = "tablas_enviadas.json"

# Memoria en ejecución para construir las tablas a partir de los resultados individuales
MEMORIA_TABLAS = {}

# Pool completo de animalitos para los análisis automáticos
ANIMALES_POOL = [
    "00 - Delfín", "01 - Carnero", "02 - Toro", "03 - Ciempiés", "04 - Alacrán", 
    "05 - León", "06 - Rana", "07 - Perico", "08 - Ratón", "09 - Águila", 
    "10 - Tigre", "11 - Gato", "12 - Caballo", "13 - Mono", "14 - Paloma", 
    "15 - Zorro", "16 - Oso", "17 - Pavo", "18 - Burro", "19 - Chivo", 
    "20 - Cochino", "21 - Gallo", "22 - Camello", "23 - Cebra", "24 - Iguana", 
    "25 - Gallina", "26 - Vaca", "27 - Perro", "28 - Zamuro", "29 - Elefante", 
    "30 - Caimán", "31 - Lapa", "32 - Ardilla", "33 - Pescado", "34 - Venado", 
    "35 - Jirafa", "36 - Culebra"
]

# Diccionario de abreviaturas oficiales solicitadas para resultados individuales
TRADUCCION_LOTERIAS = {
    "L.A": "LOTTO ACTIVO",
    "GRJ": "GRANJITA",
    "S.P": "SELVA PLUS",
    "L.RE": "LOTTO REAL",
    "GHO": "GUACHARO",
    "L.CH": "LOTTO CHAIMA",
    "MJ.M": "MONJE MILLONARIO"
}

HEADER_FyD = (
    "Resultado: *AGENCIA FyD*\n"
    "Hora: {hora_str}\n"
    "JUEGA AQUI\n"
    "RESULTADOS ANIMALITOS\n\n"
    "🎲 *{nombre_loteria}* 🎲\n"
    "Hora: {hora}\n"
    "Animalito: *{resultado}*\n\n"
    f"{ENLACE_CANAL}"
)

app = Flask('')

@app.route('/')
def home():
    return (
        f"¡El bot de resultados individuales y tablas de la <b>Agencia FyD</b> está activo en el canal {CANAL}!<br><br>"
        "<b>Enlaces de prueba rápida (Test):</b><br>"
        "👉 <a href='/test/madrugada'>Probar Saludo de Madrugada</a><br>"
        "👉 <a href='/test/piramide'>Probar Pirámide Numérica</a><br>"
        "👉 <a href='/test/regalos'>Probar Regalos del Día</a><br>"
        "👉 <a href='/test/saludo'>Probar Saludo Matutino</a><br>"
        "👉 <a href='/test/estudio_manana'>Probar Análisis de las 8 AM</a><br>"
        "👉 <a href='/test/estudio_mediodia'>Probar Análisis del Mediodía</a><br>"
        "👉 <a href='/test/estudio_tarde'>Probar Análisis de la Tarde</a><br>"
        "👉 <a href='/test/bcv'>Probar Tasa Oficial BCV</a><br>"
        "👉 <a href='/test/sorteo'>Probar Cierre de Sorteo (Min 25/55)</a><br>"
        "👉 <a href='/test/cierre'>Probar Cierre de Jornada (8:00 PM)</a><br>"
        "👉 <a href='/test/tabla1_fake'>Probar Tabla 1 Fake (Orden de Prioridad)</a>"
    )

# --- RUTAS DE PRUEBA MANUAL (TESTS) ---
@app.route('/test/madrugada')
def test_madrugada():
    enviar_saludo_madrugada()
    return "Prueba de Saludo de Madrugada ejecutada."

@app.route('/test/piramide')
def test_piramide():
    enviar_piramide_diaria()
    return "Prueba de Pirámide Numérica ejecutada."

@app.route('/test/regalos')
def test_regalos():
    enviar_regalos_diarios()
    return "Prueba de Regalos del Día ejecutada."

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

@app.route('/test/forzar')
def test_forzar():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CANAL,
        "text": "🚨 PRUEBA DIRECTA: Si lees esto, el bot tiene acceso total y perfecto al canal.",
        "parse_mode": "Markdown"
    }
    r = requests.post(url, json=payload)
    return f"Respuesta de Telegram: {r.status_code} - {r.text}"

@app.route('/test/tabla1_fake')
def test_tabla1_fake():
    MEMORIA_TABLAS.clear()

    if os.path.exists(ARCH_TABLAS_REGISTRO):
        try:
            os.remove(ARCH_TABLAS_REGISTRO)
        except Exception:
            pass

    MEMORIA_TABLAS["08:00 AM"] = {
        "LOTTO REAL": "05 - LEÓN",
        "OTRA LOTERIA": "12 - CABALLO",
        "SELVA PLUS": "20 - COCHINO",
        "GUACHARO ACTIVO": "10 - TIGRE",
        "LOTTO ACTIVO": "15 - ZORRO",
        "LA GRANJITA": "36 - CULEBRA"
    }

    enviar_tabla_tanda(1)

    return "¡Tabla 1 enviada a Telegram con éxito!"

def limpiar_texto(texto):
    return " ".join(texto.split())

def enviar_telegram(mensaje, disable_web_preview=True):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CANAL, 
        "text": mensaje, 
        "parse_mode": "Markdown", 
        "disable_web_page_preview": disable_web_preview
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Error al enviar al canal: {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción de conexión con Telegram: {e}")

def enviar_saludo_madrugada():
    enviar_telegram(
        "🎯 AGENCIA FyD 🎯\n\n"
        "_Trabajamos para tí_\n\n"
        "🌅 ¡Despertando con la mejor energía y listos para ganar! 🌅\n"
        "WHATSAPP: 04249611372",
        disable_web_preview=True
    )

def generar_piramide():
    ahora = datetime.now()
    fecha_str = ahora.strftime("%d/%m/%Y")
    digitos = [int(c) for c in fecha_str if c.isdigit()]
    filas = [digitos]
    while len(filas[-1]) > 1:
        actual = filas[-1]
        siguiente = [(actual[i] + actual[i+1]) % 10 for i in range(len(actual) - 1)]
        filas.append(siguiente)
     
    lineas_formateadas = []
    for i, f in enumerate(filas):
        nums_str = "  ".join(str(d) for d in f)
        dots_count = 3 + (i * 2)
        lineas_formateadas.append(f"{'.' * dots_count}  {nums_str}  {'.' * dots_count}")
     
    cuerpo_piramide = "\n".join(lineas_formateadas)
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
     
    return (
        "AGENCIA FyD\n"
        "_Trabajamos para tí_\n"
        "📢 REPORTE TÁCTICO - LA PIRÁMIDE 📢\n\n"
        f"📅 Fecha: {fecha_str}\n\n"
        f"{cuerpo_piramide}\n\n"
        "🔥 DATOS CLAVES PARA HOY:\n"
        f"📌 {d1}\n"
        f"📌 {d2}\n\n"
        "WHATSAPP: 04249611372"
    )

def enviar_piramide_diaria():
    enviar_telegram(generar_piramide(), disable_web_preview=True)

def enviar_regalos_diarios():
    ahora = datetime.now()
    fecha_str = ahora.strftime("%d/%m/%Y")
    seed_val = int(ahora.strftime("%Y%m%d")) + 99
    rnd = random.Random(seed_val)
    regalos_seleccionados = rnd.sample(ANIMALES_POOL, 3)
     
    mensaje_regalos = (
        "🎁 *LOS REGALOS DE LA AGENCIA FyD* 🎁\n"
        "_Trabajamos para tí_\n\n"
        f"📅 Fecha: {fecha_str}\n\n"
        "¡Los fijos recomendados para reventar la banca hoy:\n\n"
        f"🌟 *1er Regalo:* {regalos_seleccionados[0]}\n"
        f"🌟 *2do Regalo:* {regalos_seleccionados[1]}\n"
        f"🌟 *3er Regalo:* {regalos_seleccionados[2]}\n\n"
        "📲 WHATSAPP: 04249611372\n"
        f"{ENLACE_CANAL}\n\n"
        "¡Mucha suerte en tus jugadas! 🍀✨"
    )
    enviar_telegram(mensaje_regalos, disable_web_preview=True)

def obtener_animales_salidos_actuales():
    salidos = set()
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        respuesta = requests.get(URL_LOTERIA, headers=headers, timeout=10)
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            texto_total = soup.get_text(" ", strip=True)
            matches = re.findall(r'(\d{1,2})\s*-\s*([A-ZÁÉÍÓÚÑa-zñáéíóú]+)', texto_total)
            for m in matches:
                num_str = f"{int(m[0]):02d}" if m[0].isdigit() else m[0]
                salidos.add(num_str)
    except Exception as e:
        print(f"Error obteniendo salidos para análisis: {e}")
    return salidos

def seleccionar_analisis_dinamico(cantidad):
    salidos = obtener_animales_salidos_actuales()
    disponibles = [a for a in ANIMALES_POOL if a.split(" - ")[0].zfill(2) not in salidos]
     
    if len(disponibles) < cantidad:
        disponibles = ANIMALES_POOL

    seed_val = int(datetime.now().strftime("%Y%m%d%H%M"))
    rnd = random.Random(seed_val)
    return rnd.sample(disponibles, cantidad)

def enviar_estudio_8am():
    analisis = seleccionar_analisis_dinamico(2)
    mensaje = (
        "🎯 *AGENCIA FyD* 🎯\n"
        "_Trabajamos para tí_\n\n"
        "🔍 *ANÁLISIS TRAS EL SORTEO DE LAS 8:00 AM* 🔍\n\n"
        "¡Ya salieron los primeros animalitos! Evaluando la apertura de la pizarra y descartando lo ya jugado, la casa trae las recomendaciones probables para los siguientes sorteos:\n\n"
        f"🔥 *Regalitos recomendados:* `{analisis[0]}` y `{analisis[1]}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_estudio_mediodia():
    analisis = seleccionar_analisis_dinamico(2)
    tripleta = seleccionar_analisis_dinamico(3)
    t_str = f"{tripleta[0].split(' - ')[0]} - {tripleta[1].split(' - ')[0]} - {tripleta[2].split(' - ')[0]}"
     
    mensaje = (
        "🎯 *AGENCIA FyD* 🎯\n"
        "_Trabajamos para tí_\n\n"
        "☀️ *ANÁLISIS DEL MEDIODÍA* ☀️\n\n"
        "¡Mitad de jornada! Estudiando los resultados que nos dejó la mañana y analizando tendencias en vivo, el tablero apunta hacia las siguientes proyecciones:\n\n"
        f"🔥 *Animales calientes:* `{analisis[0]}` y `{analisis[1]}`\n"
        f"🎯 *Tripleta recomendada:* `{t_str}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_estudio_tarde():
    analisis = seleccionar_analisis_dinamico(2)
    mensaje = (
        "🎯 *AGENCIA FyD* 🎯\n"
        "_Trabajamos para tí_\n\n"
        "🌇 *ANÁLISIS Y CIERRE DE LA TARDE* 🌇\n\n"
        "¡A pocas horas de terminar la jornada! Evaluando el comportamiento de los últimos sortos y filtrando los ganadores del día, la casa trae los animales con mayor probabilidad de reventar para asegurar el cierre:\n\n"
        f"⚡️ *Imparables de la Tarde / Cierre:* `{analisis[0]}` y `{analisis[1]}`\n\n"
        "📲 *WHATSAPP:* 04249611372\n"
        f"{ENLACE_CANAL}"
    )
    enviar_telegram(mensaje, disable_web_preview=True)

def enviar_saludo_matutino():
    enviar_telegram(
        "🎯 AGENCIA FyD 🎯\n"
        "_Trabajamos para tí_\n\n"
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
        "AGENCIA FyD\n"
        "_Trabajamos para tí_\n\n"
        "🌙 ¡FINAL DE JORNADA! 🌙\n"
        "Cerramos nuestras puertas por el día de hoy. ¡Gracias por jugar con nosotros! Los esperamos mañana con más energía y suerte. 🍀✨",
        disable_web_preview=True
    )

def enviar_aviso_cierre_sorteo():
    enviar_telegram(
        "🛑 *¡ATENCIÓN!* 🛑\n\n"
        "El tiempo de jugadas ha terminado por este sorteo en la **AGENCIA FyD**.\n\n"
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

def cargar_tablas_registros():
    if os.path.exists(ARCH_TABLAS_REGISTRO):
        try:
            with open(ARCH_TABLAS_REGISTRO, "r") as f:
                data = json.load(f)
                if data.get("fecha") == datetime.now().strftime("%d-%m-%Y"):
                    return set(data.get("enviados", []))
        except Exception:
            pass
    return set()

def guardar_tablas_registros(enviados_set):
    data = {
        "fecha": datetime.now().strftime("%d-%m-%Y"),
        "enviados": list(enviados_set)
    }
    try:
        with open(ARCH_TABLAS_REGISTRO, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error al guardar registros de tablas: {e}")

# ==========================================
# NUEVO SISTEMA DE TABLAS DINÁMICAS POR TANDAS
# ==========================================
MAPA_ABREVIATURAS = {
    "LA GRANJITA": "GRAJ",
    "LOTTO ACTIVO": "L.ACT",
    "SELVA PLUS": "SELV",
    "GUACHARO ACTIVO": "G.ARO",
    "LOTTO CHAIMA": "CHAIM",
    "MONJE MILLONARIO": "MONJE",
    "LOTO ANIMAL": "L.ANIM",
    "LOTTO PANTHER": "L.PANT",
    "LOTTO REAL": "L.REAL",
    "LOTTO RD": "L.RD",
    "CENTENA ANIMAL": "CEN.A",
    "MEGA ANIMAL": "MEGA",
    "RULETA PERÚ": "R.PER",
    "RULETA COLOMBIA": "R.COL",
    "RULETA VENEZUELA": "R.VEN",
    "CÓNDOR": "COND",
    "FRUTICA": "FRUI",
    "TRÓPICA": "TROP",
    "GRANJA MILLONARIA": "G.MIL",
    "ZOOLÓGICO": "ZOOL",
    "LOTTO MAX": "L.MAX"
}

EMOJIS_ANIMALES_FIJOS = {
    "00": "🐋", "0": "🐋",
    "01": "🐏", "1": "🐏",
    "02": "🐂", "2": "🐂",
    "03": "🐛", "3": "🐛",
    "04": "🦂", "4": "🦂",
    "05": "🦁", "5": "🦁",
    "06": "🐸", "6": "🐸",
    "07": "🦜", "7": "🦜",
    "08": "🐭", "8": "🐭",
    "09": "🦅", "9": "🦅",
    "10": "🐯",
    "11": "🐱",
    "12": "🐴",
    "13": "🐵",
    "14": "🕊️",
    "15": "🦊",
    "16": "🐻",
    "17": "🦃",
    "18": "🫏",
    "19": "🐐",
    "20": "🐖",
    "21": "🐓",
    "22": "🐪",
    "23": "🦓",
    "24": "🦎",
    "25": "🐔",
    "26": "🐮",
    "27": "🐶",
    "28": "🦅",
    "29": "🐘",
    "30": "🐊",
    "31": "🐾",
    "32": "🐿️",
    "33": "🐟",
    "34": "🦌",
    "35": "🦒",
    "36": "🐍"
}

ORDEN_TABLA_1 = [
    "LOTTO ACTIVO",
    "LA GRANJITA",
    "SELVA PLUS",
    "GUACHARO ACTIVO",
    "LOTTO REAL"
]

def obtener_abreviatura_dinamica(nombre_loteria):
    nombre_upper = limpiar_texto(nombre_loteria.upper())
    if nombre_upper in MAPA_ABREVIATURAS:
        return MAPA_ABREVIATURAS[nombre_upper]
     
    palabras = [p for p in nombre_upper.split() if p not in ["DE", "DEL", "LA", "EL", "LOS", "LAS"]]
    if not palabras:
        return nombre_upper[:4]
    if len(palabras) == 1:
        return palabras[0][:4]
    else:
        sigla = "".join([w[0] for w in palabras])
        if len(sigla) >= 3:
            return sigla[:4]
        return palabras[0][:3] + "." + palabras[1][0]

def formatear_celda_tabla(res_str):
    res_str = limpiar_texto(res_str.upper())
    if res_str == "FALSE" or "FALSE" in res_str:
        return "....🚫"
    if "PENDIENTE" in res_str or not res_str:
        return "....🚫"
     
    match = re.search(r'(\d{1,2})\s*-\s*([A-ZÁÉÍÓÚÑ]+)', res_str)
    if match:
        num_raw = match.group(1)
        num_fmt = f"{int(num_raw):02d}" if num_raw.isdigit() else num_raw
        emoji = EMOJIS_ANIMALES_FIJOS.get(num_fmt, "🐾")
        return f"{num_fmt}{emoji}"
     
    match_num = re.search(r'(\d{1,2})', res_str)
    if match_num:
        num_raw = match_num.group(1)
        num_fmt = f"{int(num_raw):02d}" if num_raw.isdigit() else num_raw
        emoji = EMOJIS_ANIMALES_FIJOS.get(num_fmt, "🐾")
        return f"{num_fmt}{emoji}"
         
    return "....🚫"

def enviar_tabla_tanda(tipo_tanda):
    try:
        if not MEMORIA_TABLAS:
            return

        horas_filtradas = []
        for h in MEMORIA_TABLAS.keys():
            try:
                minuto_str = h.split(":")[1][:2]
                minuto_val = int(minuto_str)
                if tipo_tanda == 1 and 0 <= minuto_val <= 10:
                    horas_filtradas.append(h)
                elif tipo_tanda == 2 and 11 <= minuto_val <= 20:
                    horas_filtradas.append(h)
                elif tipo_tanda == 3 and 30 <= minuto_val <= 40:
                    horas_filtradas.append(h)
            except Exception:
                continue

        if not horas_filtradas:
            return

        def ordenar_hora(h_str):
            try:
                return datetime.strptime(h_str.replace(" ", ""), "%I:%M%p")
            except Exception:
                return datetime.min

        horas_filtradas.sort(key=ordenar_hora)

        loterias_en_tanda = []
        for h in horas_filtradas:
            for lot, res in MEMORIA_TABLAS.get(h, {}).items():
                if lot not in loterias_en_tanda and "PENDIENTE" not in res.upper() and "....🚫" not in formatear_celda_tabla(res):
                    loterias_en_tanda.append(lot)

        if not loterias_en_tanda:
            for h in horas_filtradas:
                for lot in MEMORIA_TABLAS.get(h, {}).keys():
                    if lot not in loterias_en_tanda:
                        loterias_en_tanda.append(lot)

        if not loterias_en_tanda:
            return

        if tipo_tanda == 1:
            prioridad = []
            for lot in ORDEN_TABLA_1:
                for encontrada in loterias_en_tanda:
                    if lot in encontrada.upper():
                        prioridad.append(encontrada)
                        break
            for lot in loterias_en_tanda:
                if lot not in prioridad:
                    prioridad.append(lot)
            loterias_en_tanda = prioridad

        enviadas_hoy = cargar_tablas_registros()
        
        TAMANO_BLOQUE = 4
        bloques_loterias = [loterias_en_tanda[i:i + TAMANO_BLOQUE] for i in range(0, len(loterias_en_tanda), TAMANO_BLOQUE)]

        texto_final = "📰 <b>RESULTADOS ANIMALITOS</b> 📰\n"

        for idx, bloque in enumerate(bloques_loterias):
            texto_final += f"\n📋 <b>Bloque {idx + 1}</b>:\n"
            cabecera = "<code>HO_RA"
            for lot in bloque:
                abrev = obtener_abreviatura_dinamica(lot)
                cabecera += f"  🎰{abrev}"
            cabecera += "</code>\n"
            texto_final += cabecera

            for h in horas_filtradas:
                hora_corta = h[:5]
                fila = f"<code>⏰{hora_corta}"
                for lot in bloque:
                    res = MEMORIA_TABLAS.get(h, {}).get(lot, "....🚫")
                    celda = formatear_celda_tabla(res)
                    fila += f"  {celda}"
                fila += "</code>\n"
                texto_final += fila

        texto_final += f"\n📲 <b>WHATSAPP:</b> 04249611372\n{ENLACE_CANAL}"

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CANAL, 
            "text": texto_final.strip(), 
            "parse_mode": "HTML", 
            "disable_web_page_preview": True
        }
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Respuesta Telegram Tabla: {resp.status_code} - {resp.text}")

    except Exception as e:
        print(f"Error al enviar tabla tanda {tipo_tanda}: {e}")

def verificar_y_enviar_resultados_individuales():
    enviados_hoy = cargar_registros()
    es_primera_ejecucion = len(enviados_hoy) == 0
     
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        respuesta = requests.get(URL_LOTERIA, headers=headers, timeout=15)
        if respuesta.status_code != 200:
            return

        soup = BeautifulSoup(respuesta.text, 'html.parser')
        tarjetas = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'card|box|item|lotto|result', re.IGNORECASE))

        hubo_cambios = False
        nuevos_para_guardar = set(enviados_hoy)

        for tarjeta in tarjetas:
            nombre_loteria = ""
            posibles_titulos = tarjeta.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'span', 'div', 'strong', 'b'], class_=re.compile(r'title|header|name|lotto|text', re.IGNORECASE))
            for pt in posibles_titulos:
                t_text = pt.get_text(" ", strip=True).upper()
                if t_text and len(t_text) > 2 and not re.search(r'\d{1,2}:\d{2}', t_text) and "PENDIENTE" not in t_text:
                    if t_text not in ["WINBIG", "RESULTADOS", "RESULTADOS ANIMALITOS", "ANIMALITOS"]:
                        nombre_loteria = t_text
                        break

            if not nombre_loteria:
                lineas = [l.strip().upper() for l in tarjeta.get_text("\n", strip=True).split("\n") if l.strip()]
                for linea in lineas:
                    if len(linea) > 2 and not re.search(r'\d{1,2}:\d{2}', linea) and "PENDIENTE" not in linea and "-" not in linea:
                        if linea not in ["RESULTADOS ANIMALITOS", "ANIMALITOS", "RESULTADOS"]:
                            nombre_loteria = linea
                            break

            if not nombre_loteria or len(nombre_loteria) > 40:
                continue

            nombre_loteria_limpio = limpiar_texto(nombre_loteria)
            loteria_key = nombre_loteria_limpio

            nombre_loteria_ind = nombre_loteria_limpio
            for sigla, nombre_largo in TRADUCCION_LOTERIAS.items():
                if sigla in nombre_loteria_limpio.upper() or nombre_loteria_limpio.upper() == sigla:
                    nombre_loteria_ind = nombre_largo
                    break

            if "RULETA ROYAL" in nombre_loteria_limpio.upper() or "RESULTADOS" in nombre_loteria_limpio.upper():
                continue

            slots_sorteo = tarjeta.find_all(['div', 'li', 'span', 'tr'], class_=re.compile(r'item|slot|draw|row|col', re.IGNORECASE))
            if not slots_sorteo:
                slots_sorteo = [tarjeta]

            for slot in slots_sorteo:
                texto_slot = slot.get_text(" ", strip=True).upper()
                if "PENDIENTE" in texto_slot:
                    continue

                match_h = re.search(r'\b(\d{1,2}:\d{2}\s*(?:AM|PM))\b', texto_slot)
                if not match_h:
                    continue
                hora = match_h.group(1).upper()

                match_res = re.search(r'(\d{1,2}\s-\s[A-ZÁÉÍÓÚÑa-zñáéíóú]+(?:\s+[A-ZÁÉÍÓÚÑa-zñáéíóú]+)?)', texto_slot)
                if not match_res:
                    continue

                resultado = limpiar_texto(match_res.group(1)).upper()
                 
                if hora not in MEMORIA_TABLAS:
                    MEMORIA_TABLAS[hora] = {}
                MEMORIA_TABLAS[hora][loteria_key] = resultado

                id_resultado = f"{nombre_loteria_ind}_{hora}_{resultado}"

                if es_primera_ejecucion:
                    nuevos_para_guardar.add(id_resultado)
                    continue

                if id_resultado not in enviados_hoy:
                    hora_actual_str = datetime.now().strftime("%I:%M %p")
                    mensaje = HEADER_FyD.format(
                        hora_str=hora_actual_str,
                        nombre_loteria=nombre_loteria_ind,
                        hora=hora,
                        resultado=resultado
                    )
                    enviar_telegram(mensaje)
                    nuevos_para_guardar.add(id_resultado)
                    hubo_cambios = True
                    time.sleep(1.5)

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
     
    if ahora.hour > 19 or (ahora.hour == 19 and ahora.minute > 55):
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
         
        headers = {'User-Agent': 'Mozilla/5.0'}
        respuesta = requests.get(URL_LOTERIA, headers=headers, timeout=15)
        if respuesta.status_code != 200:
            bot.reply_to(message, "⚠️ No se pudo conectar con la página de resultados en este momento.")
            return

        soup = BeautifulSoup(respuesta.text, 'html.parser')
        tarjetas = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'card|box|item|lotto|result', re.IGNORECASE))

        resumen_por_loterias = {}

        for tarjeta in tarjetas:
            try:
                nombre_loteria = ""
                posibles_titulos = tarjeta.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'span', 'div', 'strong', 'b'], class_=re.compile(r'title|header|name|lotto|text', re.IGNORECASE))
                for pt in posibles_titulos:
                    t_text = pt.get_text(" ", strip=True).upper()
                    if t_text and len(t_text) > 2 and not re.search(r'\d{1,2}:\d{2}', t_text) and "PENDIENTE" not in t_text:
                        if t_text not in ["WINBIG", "RESULTADOS", "RESULTADOS ANIMALITOS", "ANIMALITOS"]:
                            nombre_loteria = t_text
                            break

                if not nombre_loteria:
                    lineas = [l.strip().upper() for l in tarjeta.get_text("\n", strip=True).split("\n") if l.strip()]
                    for linea in lineas:
                        if len(linea) > 2 and not re.search(r'\d{1,2}:\d{2}', linea) and "PENDIENTE" not in linea and "-" not in linea:
                            if linea not in ["RESULTADOS ANIMALITOS", "ANIMALITOS", "RESULTADOS"]:
                                nombre_loteria = linea
                                break

                if not nombre_loteria or len(nombre_loteria) > 40:
                    continue

                nombre_loteria = limpiar_texto(nombre_loteria)
                 
                for sigla, nombre_largo in TRADUCCION_LOTERIAS.items():
                    if sigla in nombre_loteria.upper() or nombre_loteria.upper() == sigla:
                        nombre_loteria = nombre_largo
                        break

                if "RULETA ROYAL" in nombre_loteria.upper() or "RESULTADOS" in nombre_loteria.upper():
                    continue

                if nombre_loteria not in resumen_por_loterias:
                    resumen_por_loterias[nombre_loteria] = []

                slots_sorteo = tarjeta.find_all(['div', 'li', 'span', 'tr'], class_=re.compile(r'item|slot|draw|row|col', re.IGNORECASE))
                if not slots_sorteo:
                    slots_sorteo = [tarjeta]

                for slot in slots_sorteo:
                    try:
                        texto_slot = slot.get_text(" ", strip=True).upper()
                         
                        match_h = re.search(r'\b(\d{1,2}:\d{2}\s*(?:AM|PM))\b', texto_slot)
                        if not match_h:
                            continue
                        hora = match_h.group(1).upper()

                        if "PENDIENTE" in texto_slot:
                            resumen_por_loterias[nombre_loteria].append(f"• {hora} ➔ ⏳ Pendiente")
                        else:
                            match_res = re.search(r'(\d{1,2}\s-\s[A-ZÁÉÍÓÚÑa-zñáéíóú]+(?:\s+[A-ZÁÉÍÓÚÑa-zñáéíóú]+)?)', texto_slot)
                            if match_res:
                                resultado = limpiar_texto(match_res.group(1)).upper()
                                resumen_por_loterias[nombre_loteria].append(f"• {hora} ➔ {resultado}")
                    except Exception:
                        continue
            except Exception:
                continue

        if not resumen_por_loterias:
            bot.reply_to(message, "⚠️ No se encontraron resultados disponibles en este momento.")
            return

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        texto_final = (
            "🎯 *AGENCIA FyD* 🎯\n"
            "_Trabajamos para tí_\n\n"
            "📊 *RESUMEN DE GANADORES DEL DÍA* 📊\n"
            f"📅 Fecha: {fecha_hoy}\n\n"
        )

        for loteria, items in resumen_por_loterias.items():
            if items:
                texto_final += f"🎲 *{loteria}*\n"
                for item in items:
                    texto_final += f"  {item}\n"
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

@bot.message_handler(commands=['diaria', 'todo'])
def cmd_tabla_diaria(message):
    try:
        if not MEMORIA_TABLAS:
            bot.reply_to(message, "⚠️ Todavía no hay resultados en memoria para armar la tabla del día.")
            return

        horas_filtradas = list(MEMORIA_TABLAS.keys())
        def ordenar_hora(h_str):
            try:
                return datetime.strptime(h_str.replace(" ", ""), "%I:%M%p")
            except Exception:
                return datetime.min
        horas_filtradas.sort(key=ordenar_hora)

        loterias_en_dia = []
        for h in horas_filtradas:
            for lot in MEMORIA_TABLAS.get(h, {}).keys():
                if lot not in loterias_en_dia:
                    loterias_en_dia.append(lot)

        if not loterias_en_dia:
            bot.reply_to(message, "⚠️ No hay loterías registradas todavía.")
            return

        prioridad = []
        for lot in ORDEN_TABLA_1:
            for encontrada in loterias_en_dia:
                if lot in encontrada.upper():
                    prioridad.append(encontrada)
                    break
        for lot in loterias_en_dia:
            if lot not in prioridad:
                prioridad.append(lot)
        loterias_en_dia = prioridad

        TAMANO_BLOQUE = 4
        bloques_loterias = [loterias_en_dia[i:i + TAMANO_BLOQUE] for i in range(0, len(loterias_en_dia), TAMANO_BLOQUE)]

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        texto_final = f"📰 <b>RESUMEN TOTAL DEL DÍA ({fecha_hoy})</b> 📰\n"

        for idx, bloque in enumerate(bloques_loterias):
            texto_final += f"\n📋 <b>Bloque {idx + 1}</b>:\n"
            cabecera = "<code>HO_RA"
            for lot in bloque:
                abrev = obtener_abreviatura_dinamica(lot)
                cabecera += f"  🎰{abrev}"
            cabecera += "</code>\n"
            texto_final += cabecera

            for h in horas_filtradas:
                hora_corta = h[:5]
                fila = f"<code>⏰{hora_corta}"
                for lot in bloque:
                    res = MEMORIA_TABLAS.get(h, {}).get(lot, "....🚫")
                    celda = formatear_celda_tabla(res)
                    fila += f"  {celda}"
                fila += "</code>\n"
                texto_final += fila

        texto_final += f"\n📲 <b>WHATSAPP:</b> 04249611372\n{ENLACE_CANAL}"

        if len(texto_final) > 4000:
            for x in range(0, len(texto_final), 4000):
                bot.send_message(message.chat.id, texto_final[x:x+4000], parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, texto_final, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        print(f"Error en comando diaria: {e}")
        bot.reply_to(message, f"⚠️ Error técnico al generar la tabla del día: {e}")

def loop_bot():
    schedule.every().day.at("06:30").do(enviar_saludo_madrugada)
    schedule.every().day.at("06:31").do(enviar_piramide_diaria)
    schedule.every().day.at("06:45").do(enviar_regalos_diarios)
    schedule.every().day.at("07:00").do(enviar_saludo_matutino)
     
    schedule.every().day.at("08:15").do(enviar_estudio_8am)
    schedule.every().day.at("12:15").do(enviar_estudio_mediodia)
    schedule.every().day.at("16:15").do(enviar_estudio_tarde)

    schedule.every().day.at("06:30").do(enviar_tasa_dolar)
    schedule.every().day.at("18:30").do(enviar_tasa_dolar)
    schedule.every().day.at("20:00").do(enviar_mensaje_cierre)
     
    schedule.every().hour.at(":10").do(lambda: enviar_tabla_tanda(1))
    schedule.every().hour.at(":20").do(lambda: enviar_tabla_tanda(2))
    schedule.every().hour.at(":40").do(lambda: enviar_tabla_tanda(3))
    
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
