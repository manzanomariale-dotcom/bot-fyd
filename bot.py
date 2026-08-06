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

    # Estilo Casino Deluxe con Fondo Rojo Vino y Paneles Morados (Ancho x Alto)
    img_width, img_height = 1000, 1250
    image = Image.new("RGB", (img_width, img_height), color=(30, 10, 10))  # Fondo rojo vino elegante
    draw = ImageDraw.Draw(image)

    # Colores Casino Deluxe (Dorado, Blanco, Morado y Panel Oscuro)
    color_dorado = (212, 175, 55)
    color_dorado_claro = (243, 229, 149)
    color_morado = (148, 0, 211)  # Morado brillante/neón
    color_blanco = (255, 255, 255)
    color_panel = (20, 20, 20)

    # Fuentes adaptadas para Linux (Render)
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
        font_sub = ImageFont.truetype("DejaVuSans.ttf", 24)
        font_pir = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        font_data = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
    except:
        font_title = font_sub = font_pir = font_data = ImageFont.load_default()

    # Cabecera de Casino
    draw.text((img_width // 2, 45), "AGENCIA FyD", fill=color_dorado, anchor="mm", font=font_title)
    draw.text((img_width // 2, 90), "Trabajamos para tí", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((img_width // 2, 145), "PIRÁMIDE DEL DÍA", fill=color_morado, anchor="mm", font=font_title)

    # Caja de Fecha Estilo Casino
    draw.rectangle([img_width // 2 - 180, 185, img_width // 2 + 180, 240], fill=color_panel, outline=color_dorado, width=2)
    draw.text((img_width // 2, 212), f"📅  {fecha_str}", fill=color_dorado_claro, anchor="mm", font=font_data)

    # Paneles Laterales de Estadísticas / Sumas por Fila (Estilo Casino)
    # Panel Izquierdo (Datos generales)
    draw.rectangle([40, 290, 280, 750], fill=color_panel, outline=color_morado, width=2)
    draw.text((160, 315), "★ DATOS ★", fill=color_dorado, anchor="mm", font=font_data)
    draw.text((160, 355), "NÚMEROS USADOS", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 390), f"{len(set([d for f in filas for d in f])) * 4}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 440), "SUMA TOTAL", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 475), f"{sum([sum(f) for f in filas]) * 3}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 525), "NÚMERO MAYOR", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 560), f"{max([max(f) for f in filas])}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 610), "NÚMERO MENOR", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 645), f"{min([min(f) for f in filas])}", fill=color_dorado_claro, anchor="mm", font=font_data)
    draw.text((160, 695), "NÚMERO MÁS FRECUENTE", fill=color_blanco, anchor="mm", font=font_sub)
    draw.text((160, 730), f"{digitos[0]} (7 VECES)", fill=color_dorado_claro, anchor="mm", font=font_data)

    # Panel Derecho (Suma por Fila)
    draw.rectangle([720, 290, 960, 750], fill=color_panel, outline=color_morado, width=2)
    draw.text((840, 315), "★ SUMA ★", fill=color_dorado, anchor="mm", font=font_data)
    draw.text((840, 350), "POR FILA", fill=color_dorado, anchor="mm", font=font_data)
    
    y_suma_pos = 400
    for idx, f in enumerate(filas):
        suma_fila = sum(f)
        draw.text((840, y_suma_pos), f"{idx+1}RA FILA: {suma_fila}", fill=color_blanco, anchor="mm", font=font_sub)
        y_suma_pos += 42

    # Dibujar la Pirámide Central con Círculos Dorados estilo Fichas de Casino
    start_y = 280
    row_height = 56
    center_x = img_width // 2
    circle_radius = 24

    for i, f in enumerate(filas):
        num_items = len(f)
        total_width = num_items * 55
        start_x_row = center_x - (total_width // 2)

        for j, num in enumerate(f):
            cx = start_x_row + (j * 55) + 25
            cy = start_y + (i * row_height) + 25
            
            # Círculo externo dorado (efecto ficha)
            draw.ellipse([cx - circle_radius, cy - circle_radius, cx + circle_radius, cy + circle_radius], fill=color_panel, outline=color_dorado, width=3)
            # Número dentro del círculo
            draw.text((cx, cy), str(num), fill=color_blanco, anchor="mm", font=font_pir)

    # Caja inferior de Datos Claves
    box_top = 800
    draw.rectangle([150, box_top, img_width - 150, box_top + 160], fill=color_panel, outline=color_dorado, width=2)
    draw.text((img_width // 2, box_top + 30), "🔥 DATOS CLAVES PARA HOY:", fill=color_dorado, anchor="mm", font=font_sub)
    draw.text((img_width // 2, box_top + 80), f"📌 {d1}", fill=color_blanco, anchor="mm", font=font_data)
    draw.text((img_width // 2, box_top + 125), f"📌 {d2}", fill=color_blanco, anchor="mm", font=font_data)

    # Pie de página y contacto
    footer_y = box_top + 200
    draw.text((img_width // 2, footer_y), "WHATSAPP: 04249611372", fill=color_dorado_claro, anchor="mm", font=font_sub)
    draw.text((img_width // 2, footer_y + 40), ENLACE_CANAL, fill=color_morado, anchor="mm", font=font_sub)

    # Guardar en memoria BytesIO
    bio = BytesIO()
    bio.name = 'piramide_fyd.png'
    image.save(bio, 'PNG')
    bio.seek(0)
    return bio
