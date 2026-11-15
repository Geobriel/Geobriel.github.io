"""Genera el sitio estático de Gabriel Quezada Mata.

Uso:  python build.py
Todo el contenido vive en este archivo. Para cambiar de dominio, edita BASE.
Para sumar LinkedIn, Instagram u otro perfil, completa PERFILES (lo que quede en None no se publica).
El correo de contacto se lee de la variable de entorno CORREO_SITIO; si no existe, el sitio sale sin correo.
"""
import json, math, os
from datetime import date
from html import escape

RAIZ = os.path.dirname(os.path.abspath(__file__))
BASE = "https://geobriel.github.io"        # si compras un dominio (p. ej. gabrielquezada.cl), cámbialo aquí
HOY = date.today().isoformat()

NOMBRE = "Gabriel Quezada Mata"
CORREO = os.environ.get("CORREO_SITIO", "").strip() or None
ORCID = "0000-0003-1365-8584"
DOI = "10.30827/cuadgeo.v65i1.32676"

PERFILES = {                                # orden = orden en el pie y en "Contacto"
    "LinkedIn": None,                       # p. ej. "https://www.linkedin.com/in/gabriel-quezada-mata/"
    "ORCID": f"https://orcid.org/{ORCID}",
    "GitHub": "https://github.com/Geobriel",
    "Instagram": None,                      # p. ej. "https://www.instagram.com/usuario/"
    "YouTube": "https://www.youtube.com/@trapanautica",
    "Google Scholar": None,                 # cuando crees el perfil
    "Portafolio en Google Sites": "https://sites.google.com/view/gabrielquezada/p%C3%A1gina-principal",
}
FOTO = "img/gabriel-quezada-mata-geografo.jpg"
VERIFICACION_GOOGLE = None                  # código de Search Console (meta google-site-verification)

DESCRIPCION_CORTA = ("Geógrafo de la Universidad Austral de Chile, en Valdivia. Teledetección, clasificación de "
                     "cobertura de suelo con aprendizaje automático, análisis de accesibilidad, SIG y cartografía.")

# --------------------------------------------------------------------------------------------- utilidades
def e(t): return escape(t, quote=True)

def curvas_svg():
    """Curvas de nivel decorativas, deterministas (sin azar)."""
    caminos = []
    for cx, cy, n, r0, paso, fase in [(820, 160, 9, 26, 30, 0.0), (180, 520, 7, 30, 34, 1.7), (1180, 560, 6, 34, 36, 3.1)]:
        for k in range(n):
            r = r0 + k * paso
            pts = []
            for i in range(73):
                a = 2 * math.pi * i / 72
                d = r * (1 + 0.16 * math.sin(3 * a + fase + k * .35) + 0.08 * math.sin(5 * a - fase + k * .2))
                pts.append(f"{cx + d * math.cos(a) * 1.35:.1f},{cy + d * math.sin(a):.1f}")
            grosor = "1.6" if k % 4 == 3 else "0.8"
            caminos.append(f'<path d="M{" L".join(pts)}Z" stroke-width="{grosor}"/>')
    return ('<svg class="curvas" viewBox="0 0 1400 700" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'<g fill="none" stroke="currentColor">{"".join(caminos)}</g></svg>')

LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="15" fill="var(--acento)"/>'
        '<path d="M5 19c4-5 7-1 11-5s7-3 11 0M7 24c4-3 7 0 10-3s6-2 9 0M8 12c3-3 6-1 9-3s5-2 7 0" '
        'fill="none" stroke="var(--papel)" stroke-width="1.6" stroke-linecap="round"/></svg>')

NAV = [("/", "Inicio"), ("/proyectos/", "Proyectos"), ("/cartografia/", "Mapas"), ("/publicaciones/", "Publicaciones"),
       ("/cv/", "CV"), ("/#contacto", "Contacto"), ("/en/", "English")]

def persona(completa=True):
    p = {
        "@type": "Person", "@id": f"{BASE}/#persona",
        "name": NOMBRE, "givenName": "Gabriel", "familyName": "Quezada Mata",
        "alternateName": ["Gabriel Quezada", "Gabriel Quezada M.", "Geobriel"],
        "url": f"{BASE}/", "image": f"{BASE}/{FOTO}",
        "jobTitle": "Geógrafo",
        "sameAs": [u for u in PERFILES.values() if u],
    }
    if completa:
        p.update({
            "description": DESCRIPCION_CORTA,
            "address": {"@type": "PostalAddress", "addressLocality": "Valdivia",
                        "addressRegion": "Región de Los Ríos", "addressCountry": "CL"},
            "nationality": {"@type": "Country", "name": "Chile"},
            "alumniOf": {"@type": "CollegeOrUniversity", "name": "Universidad Austral de Chile",
                         "sameAs": "https://www.uach.cl/"},
            "hasCredential": {"@type": "EducationalOccupationalCredential", "credentialCategory": "degree",
                              "name": "Título profesional de Geógrafo",
                              "recognizedBy": {"@type": "CollegeOrUniversity", "name": "Universidad Austral de Chile"}},
            "hasOccupation": {"@type": "Occupation", "name": "Geógrafo",
                              "occupationLocation": {"@type": "City", "name": "Valdivia"},
                              "skills": "SIG, teledetección, Python, QGIS, ArcGIS, cartografía, análisis espacial"},
            "worksFor": {"@type": "CollegeOrUniversity", "name": "Universidad Austral de Chile"},
            "identifier": {"@type": "PropertyValue", "propertyID": "ORCID", "value": ORCID},
            "knowsLanguage": ["es", "en"],
            "knowsAbout": ["Geografía", "Sistemas de información geográfica", "Teledetección",
                           "Clasificación de cobertura y uso de suelo", "Aprendizaje automático", "Random Forest",
                           "U-Net", "Sentinel-2", "Landsat", "Análisis de accesibilidad", "Cartografía",
                           "Levantamiento GNSS", "Python", "QGIS", "Valdivia"],
        })
        if CORREO: p["email"] = "mailto:" + CORREO
    return p

MAPA = []

def pagina(ruta, titulo, descripcion, cuerpo, *, jsonld=None, imagen="img/og-gabriel-quezada-mata.jpg",
           extra_head="", hreflang=None, lang="es", tipo_og="website", prioridad="0.7"):
    url = BASE + ruta
    grafo = [persona(completa=(ruta in ("/", "/cv/", "/en/")))]
    grafo.append({"@type": "WebSite", "@id": f"{BASE}/#sitio", "url": f"{BASE}/", "name": NOMBRE,
                  "inLanguage": "es", "publisher": {"@id": f"{BASE}/#persona"}})
    if jsonld: grafo.extend(jsonld)
    ld = json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, indent=1)
    alt = "".join(f'<link rel="alternate" hreflang="{h}" href="{BASE}{r}">\n' for h, r in (hreflang or []))
    verif = f'<meta name="google-site-verification" content="{e(VERIFICACION_GOOGLE)}">\n' if VERIFICACION_GOOGLE else ""
    nav = "".join(f'<a href="{h}"{" aria-current=page" if h == ruta else ""}>{t}</a>' for h, t in NAV)
    pie_perfiles = " | ".join(f'<a href="{u}" rel="me">{n}</a>' for n, u in PERFILES.items() if u)
    html = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descripcion)}">
<meta name="author" content="{NOMBRE}">
<link rel="canonical" href="{url}">
{alt}{verif}<meta property="og:type" content="{tipo_og}">
<meta property="og:site_name" content="{NOMBRE}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descripcion)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/{imagen}">
<meta property="og:locale" content="{'es_CL' if lang == 'es' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#2e6a4e">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/estilo.css">
{extra_head}
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<a class="saltar" href="#contenido">Saltar al contenido</a>
<header class="cabecera"><div class="envoltura">
<a class="marca" href="/">{LOGO}<span>{NOMBRE}</span></a>
<nav class="nav" aria-label="Principal">{nav}</nav>
</div></header>
<main id="contenido">
{cuerpo}
</main>
<footer class="pie"><div class="envoltura">
<span>© {date.today().year} {NOMBRE}, geógrafo. Valdivia, Chile.</span>
<span>{pie_perfiles}</span>
</div></footer>
</body>
</html>
"""
    destino = os.path.join(RAIZ, ruta.strip("/"), "index.html") if ruta.endswith("/") else os.path.join(RAIZ, ruta.strip("/"))
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as f: f.write(html)
    if ruta != "/404.html": MAPA.append((url, prioridad))

def figura(img, alt, pie, ancho=None, alto=None, carga="lazy"):
    dims = f' width="{ancho}" height="{alto}"' if ancho else ""
    return (f'<figure><img src="/img/{img}" alt="{e(alt)}"{dims} loading="{carga}" decoding="async">'
            f'<figcaption>{pie}</figcaption></figure>')

def migas(*pares):
    partes = ['<a href="/">Inicio</a>'] + [f'<a href="{h}">{t}</a>' if h else e(t) for h, t in pares]
    return f'<nav class="migas envoltura" aria-label="Ruta">{" / ".join(partes)}</nav>'

def ld_migas(*pares):
    items = [("Inicio", "/")] + list(pares)
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + r} for i, (n, r) in enumerate(items)]}

# --------------------------------------------------------------------------------------------- contenido
ARTICULO = {
    "titulo": ("Integración de Teledetección Multisensor y Aprendizaje Automático para el Análisis de Dinámicas "
               "de Cambio en la Cobertura/uso de Suelo en Ciudades en Metropolización. El Caso de Valdivia, "
               "Chile (2016-2024)"),
    "titulo_en": ("Integration of Remote Sensing Multisensor and Machine Learning for the Analysis of Land "
                  "Cover/Land Use Change Dynamics in Metropolitan Cities: The Case of Valdivia, Chile (2016-2024)"),
    "autores": ["Quezada Mata, Gabriel", "Maturana Miranda, Francisco", "Morales Soto, Mauricio",
                "Iribarren Anacona, Pablo"],
    "revista": "Cuadernos Geográficos", "volumen": "65", "numero": "1", "paginas": ("26", "50"),
    "fecha": "2026-01-22", "issn": "2340-0129",
    "ruta": "/publicaciones/cambio-cobertura-suelo-valdivia-2016-2024/",
    "pdf": "/publicaciones/quezada-mata-2026-cuadernos-geograficos.pdf",
}
CITA = (f"Quezada Mata, G., Maturana Miranda, F., Morales Soto, M. e Iribarren Anacona, P. (2026). "
        f"{ARTICULO['titulo']}. <em>Cuadernos Geográficos</em>, 65(1), 26-50. "
        f'<a href="https://doi.org/{DOI}">https://doi.org/{DOI}</a>')

PROYECTOS = [
    {
        "slug": "sis-cosu", "img": "siscosu-unet-xgboost-detalle.webp", "dims": (1210, 1276),
        "titulo": "SIS-CoSu: cobertura y uso de suelo de Valdivia con U-Net",
        "corto": "Clasificación multitemporal de la comuna de Valdivia con Landsat, Sentinel-2 y aprendizaje profundo, y simulación de escenarios futuros.",
        "etiquetas": ["Teledetección", "U-Net", "XGBoost", "Landsat", "Sentinel-2", "Python"],
        "desc": "Proyecto FONDEF IDeA SIS-CoSu de la Universidad Austral de Chile: clasificación de cobertura de suelo de Valdivia con U-Net, Landsat y Sentinel-2, por el geógrafo Gabriel Quezada Mata.",
        "datos": [("Rol", "Analista de datos geoespaciales (profesional de análisis espacial)"),
                  ("Institución", "Universidad Austral de Chile, Facultad de Ciencias"),
                  ("Proyecto", "FONDEF IDeA ID26I10080, Sistema de Simulación Espacial de la Cobertura y Uso de Suelo (SIS-CoSu)"),
                  ("Período", "julio de 2026 a la fecha"),
                  ("Herramientas", "Python, PyTorch, XGBoost, rasterio, QGIS")],
        "cuerpo": """
<p>SIS-CoSu busca reconstruir cómo cambió la cobertura de suelo de la comuna de Valdivia desde los años 90 y simular cómo podría cambiar en el futuro. Mi trabajo en el proyecto es construir toda la cadena de datos: desde la descarga de las imágenes satelitales hasta los mapas finales.</p>
<h2>Qué hago</h2>
<ul>
<li><strong>Series de tiempo satelitales.</strong> Flujos automatizados en Python para descargar, enmascarar nubes y componer imágenes Landsat (1985 a 2026) y Sentinel-2 (2016 a 2026), integradas con OpenStreetMap, edificios con altura y fotografías aéreas históricas.</li>
<li><strong>Clasificación con aprendizaje automático y profundo.</strong> Un modelo XGBoost y una red neuronal convolucional U-Net clasifican cada verano de la serie; la exactitud se mide con una muestra de validación independiente.</li>
<li><strong>Reconstrucción y escenarios.</strong> Reconstrucción de la cobertura de los años 90 y modelación de escenarios de cambio de uso de suelo (cadenas de Markov con autómatas celulares y escenarios de población).</li>
<li><strong>Cartografía.</strong> Visualización de resultados y mapas en QGIS.</li>
</ul>""",
        "figs": [("valdivia-sentinel2-2026.webp", "Imagen satelital Sentinel-2 de la comuna de Valdivia en el verano de 2026",
                  "Compuesto Sentinel-2 de verano de la comuna de Valdivia, 2026.", (1080, 1080)),
                 ("siscosu-unet-xgboost-detalle.webp", "Comparación de Sentinel-2, XGBoost y U-Net en tres sectores de Valdivia, 2024",
                  "Tres sectores de Valdivia en 2024: imagen Sentinel-2 en color verdadero, clasificación XGBoost y clasificación U-Net.", (1210, 1276)),
                 ("siscosu-serie-unet.webp", "Serie de clasificaciones U-Net de la comuna de Valdivia de 2016 a 2026",
                  "Serie anual de cobertura de suelo de la comuna de Valdivia (2016 a 2026) clasificada con U-Net sobre Sentinel-2 a 10 m.", (1280, 1040))],
    },
    {
        "slug": "rutas-sin-cuestas", "img": "rutas-sin-cuestas-valdivia.webp", "dims": (1280, 860),
        "titulo": "Rutas sin cuestas: ruteo que evita las subidas en Valdivia",
        "corto": "App web instalable que calcula la ruta de ida y la de vuelta entre dos puntos de Valdivia evitando las calles empinadas.",
        "etiquetas": ["Análisis de redes", "OpenStreetMap", "FABDEM", "JavaScript", "Python"],
        "desc": "Rutas sin cuestas: app de ruteo en Valdivia que evita subidas empinadas con OpenStreetMap y el modelo de elevación FABDEM. Proyecto de Gabriel Quezada Mata, geógrafo.",
        "datos": [("Tipo", "Proyecto personal, código abierto"),
                  ("App", '<a href="https://geobriel.github.io/rutas-valdivia/">geobriel.github.io/rutas-valdivia</a>'),
                  ("Código", '<a href="https://github.com/Geobriel/rutas-valdivia">github.com/Geobriel/rutas-valdivia</a>'),
                  ("Datos", "OpenStreetMap (ODbL), FABDEM 30 m (CC BY-NC-SA 4.0)"),
                  ("Herramientas", "Python, NetworkX, JavaScript, Leaflet, aplicación web progresiva (PWA)")],
        "cuerpo": """
<p>Valdivia tiene cuestas que se notan a pie o en bicicleta. Rutas sin cuestas calcula, para dos puntos de la ciudad, la ruta de <strong>ida</strong> y la de <strong>vuelta</strong> que evitan las subidas empinadas. Como subir cuesta y bajar no, la ida y la vuelta pueden ir por calles distintas.</p>
<h2>Cómo funciona</h2>
<ul>
<li><strong>Red de calles.</strong> 995 km de vías de OpenStreetMap, con la topología revisada y corregida.</li>
<li><strong>Alturas.</strong> FABDEM, un modelo de terreno de 30 m sin edificios ni árboles.</li>
<li><strong>Costo asimétrico.</strong> Cada metro subido vale 8 metros planos (regla de Naismith) y las subidas sobre un umbral elegido por la persona usuaria (6 % por defecto) se castigan además en forma cuadrática. Bajar no se castiga.</li>
<li><strong>Tres versiones con resultados idénticos.</strong> Un script de Python que arma la red, una app web instalable que calcula en el teléfono sin servidor y sin conexión, y un programa para Windows.</li>
</ul>""",
        "figs": [("rutas-sin-cuestas-valdivia.webp", "Interfaz de la app Rutas sin cuestas sobre el mapa de Valdivia",
                  'La app en el navegador: mapa de Valdivia y controles de pendiente. <a href="https://geobriel.github.io/rutas-valdivia/">Abrir la app</a>.', (1280, 860))],
    },
    {
        "slug": "accesibilidad-territorial", "img": "accesibilidad-servicio-financiero-chile.webp", "dims": (1600, 1079),
        "titulo": "Indicadores de accesibilidad territorial para todas las comunas de Chile",
        "corto": "Tiempos de viaje por la red vial a bancos, liceos y centros de salud, y cobertura de caminos pavimentados, con hexágonos H3.",
        "etiquetas": ["Accesibilidad", "H3", "Análisis de redes", "Censo 2024", "Python"],
        "desc": "Indicadores comunales de accesibilidad a servicios financieros, educación y salud en Chile con hexágonos H3 y redes viales de OpenStreetMap. Trabajo de Gabriel Quezada Mata, geógrafo.",
        "datos": [("Rol", "Analista geoespacial y desarrollador del método"),
                  ("Instituciones", "Universidad Autónoma de Chile (proyecto IDI IT25I0105) y Laboratorio Transiciones Territoriales de la Zona Sur y Austral (LATSA), Universidad Austral de Chile"),
                  ("Período", "marzo a julio de 2026"),
                  ("Herramientas", "Python, H3, OSMnx, GeoPandas, QGIS")],
        "cuerpo": """
<p>¿Cuánto tarda una persona en llegar al banco, al liceo o al CESFAM más cercano desde donde vive? Para responderlo a escala comunal desarrollé un método reproducible en Python.</p>
<h2>Método</h2>
<ul>
<li>Se cubre la comuna con una malla de hexágonos H3.</li>
<li>Se descarga automáticamente la red vial de OpenStreetMap.</li>
<li>Para cada hexágono se calcula el tiempo mínimo de viaje por la red, desde su centroide hasta el servicio más cercano.</li>
<li>Los tiempos se resumen por comuna.</li>
</ul>
<h2>Indicadores calculados</h2>
<p>Para el proyecto «Plataforma de Gestión para el Desarrollo Territorial a partir del Índice de Desarrollo Intrarregional (IDI)» (IT25I0105) de la Universidad Autónoma de Chile diseñé y calculé indicadores de accesibilidad a sucursales bancarias y cajas vecinas, a establecimientos de enseñanza media públicos y particulares subvencionados, y a establecimientos de salud (CESFAM, CECOF y postas rurales), además de la cobertura de conexión a caminos pavimentados de las entidades urbanas y aldeas del Censo 2024. También redacté la propuesta metodológica y los informes técnicos.</p>""",
        "figs": [("accesibilidad-servicio-financiero-chile.webp", "Mapa de Chile con la mediana del tiempo mínimo de acceso a servicios financieros por comuna",
                  "Mediana del tiempo mínimo de viaje a un servicio financiero, por comuna (minutos).", (1600, 1079)),
                 ("pavimento-por-comuna-chile.webp", "Mapa de Chile con el porcentaje de conexión a caminos pavimentados por comuna",
                  "Porcentaje de conexión a caminos pavimentados, por comuna.", (1600, 1121)),
                 ("accesibilidad-araucania-montana-1.webp", "Mapas de tiempo de viaje a municipalidad, educación y salud en una comuna de montaña de La Araucanía",
                  "Tiempo de viaje a la municipalidad, a establecimientos educacionales y de salud en comunas de montaña de La Araucanía.", (1280, 1473)),
                 ("accesibilidad-panguipulli-continuo.webp", "Mapas y distribuciones del tiempo de viaje a servicios básicos en Panguipulli",
                  "Accesibilidad a educación, salud y municipalidad en Panguipulli: mapas por hexágono y distribución de tiempos.", (1280, 1114))],
    },
    {
        "slug": "jardin-botanico-uach", "img": "jardin-botanico-uach-carta-terreno.webp", "dims": (1600, 1120),
        "titulo": "Línea base geoespacial del Jardín Botánico de la Universidad Austral de Chile",
        "corto": "Levantamiento GNSS en terreno, digitalización de áreas verdes y dosel, zonificación y una carta de terreno para el trabajo botánico.",
        "etiquetas": ["GNSS", "Levantamiento en terreno", "Cartografía", "QGIS"],
        "desc": "Levantamiento GNSS y cartografía de terreno del Jardín Botánico de la Universidad Austral de Chile en Valdivia, por el geógrafo Gabriel Quezada Mata.",
        "datos": [("Rol", "Geógrafo y analista geoespacial"),
                  ("Mandante", "Dirección del Jardín Botánico, Universidad Austral de Chile"),
                  ("Período", "junio de 2026"),
                  ("Herramientas", "GPS GNSS, QGIS, Inkscape")],
        "cuerpo": """
<p>La dirección del Jardín Botánico de la Universidad Austral de Chile necesitaba una base espacial ordenada del jardín para levantar después la información botánica. Construí esa línea base desde cero.</p>
<ul>
<li><strong>Terreno:</strong> levantamiento con equipos GPS GNSS de senderos, bancas, basureros, hitos, señalética y canales.</li>
<li><strong>Gabinete:</strong> digitalización de los polígonos de áreas verdes y del dosel arbóreo, y zonificación de los espacios del jardín.</li>
<li><strong>Entrega:</strong> la base de datos espacial completa y una carta de terreno diseñada como instrumento de campo.</li>
</ul>""",
        "figs": [("jardin-botanico-uach-carta-terreno.webp", "Carta de terreno del Jardín Botánico de la Universidad Austral de Chile en Valdivia",
                  "Carta de terreno del Jardín Botánico de la Universidad Austral de Chile, isla Teja, Valdivia.", (1600, 1120))],
    },
    {
        "slug": "cartografia-ilustrada", "img": "epu-lafken-mapu-mapa-ilustrado.webp", "dims": (1600, 1129),
        "titulo": "Cartografía ilustrada y mapas de diseño",
        "corto": "Mapas pensados para colgarse en la pared o para guiar turistas: datos geográficos reales con diseño gráfico e ilustración.",
        "etiquetas": ["Cartografía", "Ilustración", "Diseño", "Illustrator", "Photoshop"],
        "desc": "Mapas ilustrados y pósters cartográficos del sur de Chile diseñados por Gabriel Quezada Mata, geógrafo y cartógrafo en Valdivia.",
        "datos": [("Herramientas", "QGIS, Illustrator, Photoshop, Inkscape, pinceles propios")],
        "cuerpo": """
<p>Además del análisis, me interesa que un mapa se entienda y se disfrute. Estos trabajos combinan información geográfica real con ilustración y diseño.</p>
<ul>
<li><strong>Epu Lafken Mapu, cuenca del Lago Ranco (50 × 65 cm).</strong> Cartografía ilustrada de estilo fantasía para un proyecto de toponimia ancestral, con relieve dibujado a mano y estética de mapa antiguo.</li>
<li><strong>«Archipiélago de los Parques», Fundación Alerce 3000 (2025, 70 × 50 cm).</strong> Póster del Chile sur y austral, terrestre y marítimo, con cada área protegida estatal y privada, simbología, toponimia, fotos de fauna, flora y paisajes, y datos cuantitativos del territorio.</li>
<li><strong>Parque Arboretum Puyumen, Panguipulli (2024, 84,1 × 118,9 cm).</strong> Levantamiento GNSS de senderos y puntos de interés, línea base de rodales y especies, y un mapa ilustrado para turistas con construcciones, especies emblemáticas, miradores y servicios.</li>
</ul>
<p>Más mapas técnicos en el <a href="/cartografia/">portafolio cartográfico</a>.</p>""",
        "figs": [("epu-lafken-mapu-mapa-ilustrado.webp", "Mapa ilustrado Epu Lafken Mapu de la cuenca del Lago Ranco con relieve dibujado a mano",
                  "Epu Lafken Mapu: cartografía ilustrada de la cuenca del Lago Ranco para un proyecto de toponimia ancestral.", (1600, 1129)),
                 ("parque-arboretum-puyumen-mapa-ilustrado.webp", "Mapa ilustrado para turistas del Parque Arboretum Puyumen en Panguipulli",
                  "Mapa ilustrado para turistas del Parque Arboretum Puyumen, Panguipulli.", (1280, 906)),
                 ("archipielago-de-los-parques-poster.webp", "Póster Archipiélago de los Parques con las áreas protegidas del sur de Chile",
                  "«Archipiélago de los Parques», póster para la Fundación Alerce 3000.", (1280, 1792))],
    },
]

EXPERIENCIA = [
    ("07/2026 a la fecha", "Analista de datos geoespaciales", "Universidad Austral de Chile, Facultad de Ciencias. Proyecto FONDEF IDeA ID26I10080 (SIS-CoSu)",
     "Flujos en Python para series de tiempo Landsat y Sentinel-2; clasificación multitemporal de cobertura de suelo de Valdivia con aprendizaje automático y una red U-Net; reconstrucción de la cobertura de los años 90 y escenarios futuros; cartografía en QGIS.", "/proyectos/sis-cosu/"),
    ("06/2026 a 07/2026", "Analista geoespacial", "Universidad Autónoma de Chile. Proyecto IDI IT25I0105",
     "Diseño y cálculo de indicadores comunales de accesibilidad a servicios financieros, educación media y salud, y de cobertura de caminos pavimentados según el Censo 2024; propuesta metodológica e informes técnicos.", "/proyectos/accesibilidad-territorial/"),
    ("06/2026", "Geógrafo y analista geoespacial", "Jardín Botánico, Universidad Austral de Chile",
     "Línea base geoespacial: levantamiento GNSS, digitalización de áreas verdes y dosel, zonificación y carta de terreno.", "/proyectos/jardin-botanico-uach/"),
    ("03/2026 a la fecha", "Desarrollador de código en Python", "Laboratorio Transiciones Territoriales de la Zona Sur y Austral (LATSA), Universidad Austral de Chile",
     "Script que cubre una comuna con hexágonos, descarga la red vial de OpenStreetMap y calcula el tiempo mínimo de viaje a servicios básicos.", "/proyectos/accesibilidad-territorial/"),
    ("09/2025 a 12/2025", "Capacitación de tesistas", "Universidad Austral de Chile",
     "Enseñé a tres tesistas el flujo completo de clasificación de cobertura de suelo con Random Forest: datos multiespectrales y de radar, procesamiento raster, Python y validación.", None),
    ("05/2025 a 07/2025", "Geógrafo y diseñador", "Fundación Alerce 3000",
     "Póster cartográfico «Archipiélago de parques» de las áreas protegidas del Chile sur y austral.", "/proyectos/cartografia-ilustrada/"),
    ("01/2024 a 02/2025", "Consultor y cartógrafo", "Parque Arboretum Puyumen, Panguipulli",
     "Levantamiento GNSS, base de datos espacial de rodales y especies, y mapa ilustrado para turistas.", "/proyectos/cartografia-ilustrada/"),
    ("07/2023 a 12/2024", "Tesista", "Universidad Austral de Chile. Proyecto FONDECYT 1230159, laboratorio LATSA",
     "Tesis de clasificación supervisada de la comuna de Valdivia con datos multiespectrales, radar y modelos de elevación; dio origen al artículo en Cuadernos Geográficos.", ARTICULO["ruta"]),
    ("08/2022 a 12/2023", "Ayudante SIG", "Universidad de Aysén. Proyectos FSEQ210010 y FIC40010333",
     "Georreferenciación de imágenes aéreas, de dron y satelitales; digitalización de cauces, barras y terrazas fluviales; medición del cambio geomorfológico en los ríos Simpson, Blanco y Huemules con extracción de áridos; informes y cartografía.", None),
    ("03/2023 a 06/2023", "Encargado de la Sala SIG", "Escuela de Geografía, Universidad Austral de Chile",
     "Atención de la sala de computación con QGIS y apoyo a estudiantes de geografía.", None),
]

GALERIA = [  # (título, ficha técnica, descripción, [(imagen, alt, ancho, alto)])
    ("Clasificación supervisada de la comuna de Valdivia, 2016 y 2024", "15,6 × 15,6 cm | Publicación científica",
     f'Zonas Climáticas Locales de Valdivia clasificadas con Random Forest sobre Sentinel-1, Sentinel-2 y ALOS PALSAR. <a href="{ARTICULO["ruta"]}">Ver el artículo</a>.',
     [("valdivia-zonas-climaticas-locales-2016.webp", "Mapa de Zonas Climáticas Locales de Valdivia en 2016", 1280, 1352),
      ("valdivia-zonas-climaticas-locales-2024-mapa.webp", "Mapa de Zonas Climáticas Locales de Valdivia en 2024", 1280, 1352)]),
    ("Estudio hídrico de la comuna de Calbuco", "14 × 15,6 cm | Publicación científica",
     "Lugares visitados en terreno, usos de suelo y derechos de agua, espacios costeros marinos de pueblos originarios (ECMPO), áreas de manejo (AMERB) y proyectos de pesca y acuicultura.",
     [("calbuco-lugares-visitados.webp", "Mapa de los lugares visitados en terreno en la comuna de Calbuco", 1280, 1149),
      ("calbuco-usos-de-suelo-derechos-de-agua.webp", "Mapa de usos de suelo y derechos de agua en Calbuco", 1280, 1149),
      ("calbuco-ecmpo-amerb.webp", "Mapa de zonas ECMPO y AMERB en Calbuco", 1280, 1149),
      ("calbuco-pesca-acuicultura.webp", "Mapa de proyectos de pesca y acuicultura en Calbuco", 1280, 1149)]),
    ("Accesibilidad a servicios básicos en comunas de montaña de La Araucanía", "14 × 15,6 cm | Publicación científica",
     "Tiempo de viaje por la red vial a la municipalidad, a establecimientos educacionales y a centros de salud, calculado sobre hexágonos.",
     [(f"accesibilidad-araucania-montana-{i}.webp", f"Mapas de tiempo de viaje a servicios básicos en una comuna de montaña de La Araucanía ({i})", 1280, 1473) for i in range(1, 5)]),
    ("Accesibilidad a servicios básicos en Panguipulli", "14 × 15,6 cm | Publicación científica",
     f'Tiempo de viaje a educación, salud y municipalidad por hexágono, en quintiles y en escala continua. <a href="/proyectos/accesibilidad-territorial/">Ver el método</a>.',
     [("accesibilidad-panguipulli-quintiles.webp", "Mapas de accesibilidad a servicios básicos en Panguipulli por quintiles", 1280, 1109),
      ("accesibilidad-panguipulli-continuo.webp", "Mapas de accesibilidad a servicios básicos en Panguipulli en escala continua", 1280, 1114)]),
    ("Isla Butachauques, comuna de Quemchi", "84,1 × 118,9 cm | Terreno integrado, Escuela de Geografía UACh",
     "Mapa base de la isla Butachauques, en el archipiélago de Chiloé, para el terreno integrado de la Escuela de Geografía.",
     [("isla-butachauques-quemchi.webp", "Mapa de la isla Butachauques en la comuna de Quemchi, Chiloé", 1280, 906)]),
    ("Parque Arboretum Puyumen, Panguipulli", "84,1 × 118,9 cm | Mapa para turistas y línea base",
     f'Mapa ilustrado para visitantes y línea base del parque con rodales, especies y senderos levantados con GNSS. <a href="/proyectos/cartografia-ilustrada/">Ver más</a>.',
     [("parque-arboretum-puyumen-mapa-ilustrado.webp", "Mapa ilustrado para turistas del Parque Arboretum Puyumen", 1280, 906),
      ("parque-arboretum-linea-base.webp", "Mapa de línea base del Parque Arboretum en Panguipulli", 1280, 906)]),
    ("Epu Lafken Mapu, cuenca del Lago Ranco", "50 × 65 cm | Proyecto de toponimia ancestral",
     "Cartografía ilustrada de estilo fantasía con relieve dibujado a mano.",
     [("epu-lafken-mapu-mapa-ilustrado.webp", "Mapa ilustrado Epu Lafken Mapu de la cuenca del Lago Ranco", 1600, 1129)]),
    ("Archipiélago de los Parques, Chile sur y austral", "70 × 50 cm | Póster para la Fundación Alerce 3000",
     "Áreas protegidas terrestres y marinas, estatales y privadas, del sur y la Patagonia de Chile.",
     [("archipielago-de-los-parques-poster.webp", "Póster Archipiélago de los Parques de la Fundación Alerce 3000", 1280, 1792)]),
    ("Ubicación, geología y turismo en el fundo El Plan, Chillán", "15,6 × 15,6 cm",
     "Mapa de relieve con red vial, refugios, miradores, volcanes y puntos turísticos en el sector de los Nevados de Chillán.",
     [("fundo-el-plan-chillan-turismo.webp", "Mapa de relieve y turismo del fundo El Plan en Chillán", 1280, 1363)]),
    ("Inversión en minería, pesca y acuicultura, Región de Magallanes, 1997 a 2021", "24 × 38,4 cm",
     "Círculos proporcionales a la inversión de los proyectos y su acumulación en el tiempo.",
     [("magallanes-inversion-mineria-acuicultura.webp", "Mapa de círculos proporcionales de inversión en minería y acuicultura en Magallanes", 1280, 905)]),
    ("Accesibilidad territorial en todas las comunas de Chile", "Proyecto IDI IT25I0105, Universidad Autónoma de Chile",
     f'Tiempo a servicios financieros y conexión a caminos pavimentados, por comuna. <a href="/proyectos/accesibilidad-territorial/">Ver el proyecto</a>.',
     [("accesibilidad-servicio-financiero-chile.webp", "Mapa de Chile del tiempo de acceso a servicios financieros por comuna", 1600, 1079),
      ("pavimento-por-comuna-chile.webp", "Mapa de Chile de conexión a caminos pavimentados por comuna", 1600, 1121)]),
    ("Jardín Botánico de la Universidad Austral de Chile", "Carta de terreno",
     f'Base para el levantamiento botánico, con senderos, mobiliario, canales y dosel. <a href="/proyectos/jardin-botanico-uach/">Ver el proyecto</a>.',
     [("jardin-botanico-uach-carta-terreno.webp", "Carta de terreno del Jardín Botánico de la Universidad Austral de Chile", 1600, 1120)]),
]

HABILIDADES = [("QGIS", "Avanzado"), ("ArcGIS", "Avanzado"), ("Python (GeoPandas, rasterio, PyTorch, scikit-learn, XGBoost)", "Intermedio a avanzado"),
               ("R", "Intermedio"), ("AutoCAD", "Intermedio"), ("Photoshop", "Avanzado"), ("Illustrator", "Intermedio"),
               ("Levantamiento GPS GNSS", "Avanzado"), ("Excel y Word", "Avanzado")]

# --------------------------------------------------------------------------------------------- páginas
def tarjeta(p):
    w, h = p["dims"]
    tags = "".join(f"<li>{e(t)}</li>" for t in p["etiquetas"][:4])
    return (f'<a class="tarjeta" href="/proyectos/{p["slug"]}/"><img src="/img/{p["img"]}" alt="" width="{w}" height="{h}" loading="lazy" decoding="async">'
            f'<div class="cuerpo"><h3>{e(p["titulo"])}</h3><p>{e(p["corto"])}</p><ul class="etiquetas">{tags}</ul></div></a>')

def tarjeta_articulo():
    return (f'<a class="tarjeta" href="{ARTICULO["ruta"]}"><img src="/img/valdivia-zonas-climaticas-locales-2024.webp" alt="" width="1600" height="1690" loading="lazy" decoding="async">'
            '<div class="cuerpo"><h3>Cambio de cobertura de suelo en Valdivia, 2016 a 2024</h3>'
            '<p>Artículo científico: Sentinel-1, Sentinel-2, ALOS PALSAR y Random Forest para mapear las Zonas Climáticas Locales de Valdivia, con exactitud global sobre 96 %.</p>'
            '<ul class="etiquetas"><li>Publicación</li><li>Random Forest</li><li>Sentinel</li><li>Zonas Climáticas Locales</li></ul></div></a>')

def contacto_html():
    items = [f'<li><a href="mailto:{CORREO}">Correo: {CORREO}</a></li>'] if CORREO else []
    items += [f'<li><a href="{u}" rel="me">{n}</a></li>' for n, u in PERFILES.items() if u]
    return f'<ul class="contacto">{"".join(items)}</ul>'

def inicio():
    cuerpo = f"""
<div class="portada">{curvas_svg()}<div class="envoltura">
<div>
<p class="antetitulo">Geógrafo | Valdivia, Chile</p>
<h1>{NOMBRE}</h1>
<p class="subtitulo">Soy geógrafo de la Universidad Austral de Chile. Trabajo con imágenes satelitales, aprendizaje automático y SIG para entender cómo cambia el territorio, y con cartografía para que esos resultados se entiendan.</p>
<div class="botones"><a class="boton lleno" href="/proyectos/">Ver proyectos</a><a class="boton" href="/cv/">Currículum</a><a class="boton" href="#contacto">Contacto</a></div>
</div>
<figure class="figura-portada retrato"><img src="/img/gabriel-quezada-mata-geografo.webp" alt="Gabriel Quezada Mata, geógrafo" width="554" height="689" fetchpriority="high"></figure>
</div></div>

<section><div class="envoltura">
<h2>Qué hago</h2>
<p class="intro-seccion">Geografía aplicada con código: desde la descarga de los datos hasta el mapa final.</p>
<ul class="areas">
<li><strong>Teledetección</strong><span>Series de tiempo Landsat, Sentinel-1 y Sentinel-2; clasificación de cobertura y uso de suelo con Random Forest, XGBoost y U-Net.</span></li>
<li><strong>Accesibilidad y redes</strong><span>Tiempos de viaje por la red vial con OpenStreetMap y hexágonos H3; indicadores comunales.</span></li>
<li><strong>Cartografía</strong><span>Mapas técnicos, cartas de terreno, pósters y mapas ilustrados.</span></li>
<li><strong>Terreno y datos</strong><span>Levantamientos GPS GNSS, bases de datos espaciales y automatización en Python.</span></li>
</ul>
</div></section>

<section id="proyectos"><div class="envoltura">
<h2>Proyectos</h2>
<p class="intro-seccion">Trabajos recientes en investigación, consultoría y proyectos propios. Más mapas en el <a href="/cartografia/">portafolio cartográfico</a>.</p>
<div class="rejilla">{tarjeta_articulo()}{"".join(tarjeta(p) for p in PROYECTOS)}</div>
</div></section>

<section><div class="envoltura">
<h2>Publicación</h2>
<div class="cita">{CITA}</div>
<p><a href="{ARTICULO['ruta']}">Resumen, mapas y PDF del artículo →</a></p>
</div></section>

<section id="contacto"><div class="envoltura">
<h2>Contacto</h2>
<p class="intro-seccion">¿Necesitas cartografía, análisis espacial o procesamiento de imágenes satelitales? Escríbeme.</p>
{contacto_html()}
</div></section>"""
    pagina("/", f"{NOMBRE} | Geógrafo en Valdivia: SIG, teledetección y cartografía",
           "Gabriel Quezada Mata, geógrafo de la Universidad Austral de Chile en Valdivia. Teledetección, clasificación de cobertura de suelo con aprendizaje automático, accesibilidad, SIG y cartografía.",
           cuerpo, hreflang=[("es", "/"), ("en", "/en/"), ("x-default", "/")], prioridad="1.0",
           jsonld=[{"@type": "ProfilePage", "@id": f"{BASE}/#pagina", "url": f"{BASE}/", "name": NOMBRE,
                    "mainEntity": {"@id": f"{BASE}/#persona"}, "dateModified": HOY, "inLanguage": "es"}])

def pagina_proyecto(p):
    ruta = f"/proyectos/{p['slug']}/"
    datos = "".join(f"<dt>{e(k)}</dt><dd>{v}</dd>" for k, v in p["datos"])
    figs = "".join(figura(f, a, c, *d) for f, a, c, d in p["figs"])
    cuerpo = f"""{migas(("/proyectos/", "Proyectos"), (None, p["titulo"]))}
<section><div class="envoltura ficha">
<p class="antetitulo">Proyecto de {NOMBRE}</p>
<h1>{e(p['titulo'])}</h1>
<p class="subtitulo">{e(p['corto'])}</p>
<dl class="datos">{datos}</dl>
{p['cuerpo']}
{figs}
<p><a href="/proyectos/">← Todos los proyectos</a> | <a href="/#contacto">Contacto</a></p>
</div></section>"""
    pagina(ruta, f"{p['titulo']} | {NOMBRE}, geógrafo", p["desc"], cuerpo, imagen=f"img/{p['img']}", tipo_og="article",
           jsonld=[ld_migas(("Proyectos", "/proyectos/"), (p["titulo"], ruta)),
                   {"@type": "CreativeWork", "name": p["titulo"], "description": p["desc"], "url": BASE + ruta,
                    "image": f"{BASE}/img/{p['img']}", "creator": {"@id": f"{BASE}/#persona"},
                    "keywords": ", ".join(p["etiquetas"]), "inLanguage": "es"}])

def indice_proyectos():
    cuerpo = f"""{migas((None, "Proyectos"))}
<section><div class="envoltura">
<h1>Proyectos</h1>
<p class="subtitulo">Teledetección, accesibilidad, levantamientos en terreno y cartografía de {NOMBRE}, geógrafo en Valdivia.</p>
<div class="rejilla">{tarjeta_articulo()}{"".join(tarjeta(p) for p in PROYECTOS)}</div>
</div></section>"""
    pagina("/proyectos/", f"Proyectos de {NOMBRE} | Geógrafo, SIG y teledetección",
           "Portafolio de Gabriel Quezada Mata: clasificación de cobertura de suelo con U-Net, indicadores de accesibilidad, levantamiento GNSS, ruteo y cartografía ilustrada.",
           cuerpo, prioridad="0.9", jsonld=[ld_migas(("Proyectos", "/proyectos/"))])

def cartografia():
    fichas = []
    for t, meta, txt, imgs in GALERIA:
        figs = "".join(f'<a href="/img/{f}"><img src="/img/{f}" alt="{e(a)}" width="{w}" height="{h}" loading="lazy" decoding="async"></a>'
                       for f, a, w, h in imgs)
        fichas.append(f'<article class="mapa-ficha"><h2>{e(t)}</h2><p class="meta">{e(meta)}</p><p>{txt}</p><div class="galeria">{figs}</div></article>')
    cuerpo = f"""{migas((None, "Portafolio cartográfico"))}
<section><div class="envoltura">
<h1>Portafolio cartográfico</h1>
<p class="subtitulo">Mapas de {NOMBRE}, geógrafo: cartografía para publicaciones científicas, terreno, fundaciones y proyectos culturales en el sur de Chile.</p>
{"".join(fichas)}
</div></section>"""
    imagenes = [{"@type": "ImageObject", "contentUrl": f"{BASE}/img/{f}", "name": t, "description": a,
                 "creator": {"@id": f"{BASE}/#persona"}, "creditText": NOMBRE, "copyrightNotice": NOMBRE}
                for t, _, _, imgs in GALERIA for f, a, _, _ in imgs]
    pagina("/cartografia/", f"Portafolio cartográfico de {NOMBRE} | Mapas y cartografía del sur de Chile",
           "Mapas de Gabriel Quezada Mata, geógrafo: Valdivia, Calbuco, Panguipulli, Lago Ranco, isla Butachauques, La Araucanía, Chillán y Magallanes. Cartografía científica, de terreno e ilustrada.",
           cuerpo, imagen="img/epu-lafken-mapu-mapa-ilustrado.webp", prioridad="0.9",
           jsonld=[ld_migas(("Portafolio cartográfico", "/cartografia/")),
                   {"@type": "ImageGallery", "name": f"Portafolio cartográfico de {NOMBRE}", "url": f"{BASE}/cartografia/",
                    "author": {"@id": f"{BASE}/#persona"}, "image": imagenes}])

def publicaciones():
    cuerpo = f"""{migas((None, "Publicaciones"))}
<section><div class="envoltura ficha">
<h1>Publicaciones</h1>
<p class="subtitulo">Artículos científicos de {NOMBRE}. Perfil ORCID: <a href="https://orcid.org/{ORCID}">{ORCID}</a>.</p>
<h2>2026</h2>
<div class="cita">{CITA}<br><a href="{ARTICULO['ruta']}">Resumen y mapas</a> | <a href="{ARTICULO['pdf']}">PDF</a></div>
</div></section>"""
    pagina("/publicaciones/", f"Publicaciones de {NOMBRE}, geógrafo",
           "Publicaciones científicas de Gabriel Quezada Mata sobre teledetección, aprendizaje automático y cambio de cobertura de suelo en Valdivia, Chile.",
           cuerpo, prioridad="0.8", jsonld=[ld_migas(("Publicaciones", "/publicaciones/"))])

def articulo():
    a = ARTICULO; ruta = a["ruta"]
    meta = [("citation_title", a["titulo"]),
            ("citation_author", a["autores"][0]), ("citation_author_institution", "Universidad Austral de Chile")]
    meta += [("citation_author", x) for x in a["autores"][1:]]
    meta += [("citation_publication_date", a["fecha"].replace("-", "/")), ("citation_journal_title", a["revista"]),
             ("citation_issn", a["issn"]), ("citation_volume", a["volumen"]), ("citation_issue", a["numero"]),
             ("citation_firstpage", a["paginas"][0]), ("citation_lastpage", a["paginas"][1]),
             ("citation_doi", DOI), ("citation_language", "es"), ("citation_pdf_url", BASE + a["pdf"])]
    extra = "\n".join(f'<meta name="{k}" content="{e(v)}">' for k, v in meta)
    cuerpo = f"""{migas(("/publicaciones/", "Publicaciones"), (None, "Valdivia 2016 a 2024"))}
<section><div class="envoltura ficha">
<p class="antetitulo">Artículo científico | Cuadernos Geográficos 65(1), 2026</p>
<h1>{e(a['titulo'])}</h1>
<p><strong>Gabriel Quezada Mata</strong>, Francisco Maturana Miranda, Mauricio Morales Soto y Pablo Iribarren Anacona. Universidad Austral de Chile.</p>
<div class="botones"><a class="boton lleno" href="{a['pdf']}">Descargar PDF</a><a class="boton" href="https://doi.org/{DOI}">DOI: {DOI}</a></div>
<h2>Resumen</h2>
<p>El avance de la urbanización y la presión sobre áreas de alto valor ecológico exige contar con estudios que puedan dar cuenta de tales procesos. Este trabajo analiza los cambios espaciotemporales según la clasificación de Zonas Climáticas Locales (ZCL) en la comuna de Valdivia, Chile, durante el período 2016-2024, mediante la integración de datos satelitales multisensor y técnicas de aprendizaje automático. La metodología combina datos de Sentinel-1, Sentinel-2 y ALOS PALSAR, adaptando el sistema ZCL para incluir categorías específicas de humedales y diferenciar entre bosque nativo y plantaciones forestales. Utilizando el algoritmo Random Forest, se alcanzó una precisión global superior al 96 % en la clasificación. Los resultados revelan una expansión urbana significativa del 47 % en las zonas construidas, con una tasa de crecimiento anual del 6 %, acompañada de una notable densificación en áreas periurbanas y rurales. Se identificó una reconfiguración del paisaje forestal, con un aumento de 40,28 km² en bosque nativo y una disminución de 25,14 km² en plantaciones forestales. La vegetación de los humedales experimentó un incremento del 8 % en su superficie. Este trabajo contribuye a la comprensión de las dinámicas en el cambio de la cobertura/uso de suelo de una ciudad en transición a la metropolización y ciudad humedal como Valdivia, demostrando el potencial de las técnicas de teledetección y aprendizaje automático para el monitoreo de tales cambios.</p>
<p><strong>Palabras clave:</strong> Sentinel; DEM; Random Forest; Sensores remotos; Zonas Climáticas Locales; LULC.</p>
<div class="galeria">{figura("valdivia-zonas-climaticas-locales-2016.webp", "Mapa de Zonas Climáticas Locales de la comuna de Valdivia en 2016", "Zonas Climáticas Locales de la comuna de Valdivia, 2016.", 1280, 1352)}{figura("valdivia-zonas-climaticas-locales-2024-mapa.webp", "Mapa de Zonas Climáticas Locales de la comuna de Valdivia en 2024", "Zonas Climáticas Locales de la comuna de Valdivia, 2024.", 1280, 1352)}</div>
<h2 lang="en">Abstract</h2>
<p lang="en"><em>{e(a['titulo_en'])}.</em> This study analyzes the spatiotemporal changes according to the Local Climate Zone (LCZ) classification in the commune of Valdivia, Chile, during 2016-2024, integrating multi-sensor satellite data (Sentinel-1, Sentinel-2 and ALOS PALSAR) and machine learning. Using Random Forest, overall accuracy exceeded 96 %. Built-up areas expanded by 47 %, native forest increased by 40.28 km², forest plantations decreased by 25.14 km² and wetland vegetation grew by 8 %.</p>
<h2>Cómo citar</h2>
<div class="cita">{CITA}</div>
<p style="font-size:.85rem;color:var(--tinta-2)">Publicado bajo licencia Creative Commons Reconocimiento-NoComercial 3.0. Recibido: 27-01-2025. Aceptado: 08-10-2025. Publicado: 22-01-2026.</p>
</div></section>"""
    pagina(ruta, f"Cambio de cobertura de suelo en Valdivia 2016-2024 | {NOMBRE} et al., Cuadernos Geográficos",
           "Artículo de Gabriel Quezada Mata y otros en Cuadernos Geográficos (2026): teledetección multisensor y Random Forest para analizar el cambio de cobertura de suelo en Valdivia, Chile, 2016-2024.",
           cuerpo, imagen="img/valdivia-zonas-climaticas-locales-2024.webp", extra_head=extra, tipo_og="article", prioridad="0.9",
           jsonld=[ld_migas(("Publicaciones", "/publicaciones/"), ("Valdivia 2016-2024", ruta)),
                   {"@type": "ScholarlyArticle", "headline": a["titulo"][:110], "name": a["titulo"],
                    "alternativeHeadline": a["titulo_en"], "datePublished": a["fecha"], "inLanguage": "es",
                    "author": [{"@id": f"{BASE}/#persona"}] + [{"@type": "Person", "name": n} for n in
                               ["Francisco Maturana Miranda", "Mauricio Morales Soto", "Pablo Iribarren Anacona"]],
                    "isPartOf": {"@type": "PublicationIssue", "issueNumber": "1",
                                 "isPartOf": {"@type": "PublicationVolume", "volumeNumber": "65",
                                              "isPartOf": {"@type": "Periodical", "name": a["revista"], "issn": a["issn"]}}},
                    "pageStart": "26", "pageEnd": "50", "sameAs": f"https://doi.org/{DOI}",
                    "identifier": {"@type": "PropertyValue", "propertyID": "DOI", "value": DOI},
                    "license": "https://creativecommons.org/licenses/by-nc/3.0/",
                    "image": f"{BASE}/img/valdivia-zonas-climaticas-locales-2024.webp",
                    "keywords": "Sentinel, DEM, Random Forest, sensores remotos, Zonas Climáticas Locales, LULC, Valdivia"}])

def cv():
    exp = "".join(
        f'<li><span class="fecha">{f}</span><h3>{e(c)}</h3><p class="lugar">{e(l)}</p><p>{e(d)}'
        + (f' <a href="{r}">Ver proyecto</a>' if r else "") + "</p></li>" for f, c, l, d, r in EXPERIENCIA)
    hab = "".join(f"<tr><td>{e(h)}</td><td>{n}</td></tr>" for h, n in HABILIDADES)
    cuerpo = f"""{migas((None, "Currículum"))}
<section><div class="envoltura ficha">
<p class="antetitulo">Currículum</p>
<h1>{NOMBRE}, geógrafo</h1>
<p class="subtitulo">Geógrafo con experiencia en análisis espacial y desarrollo de soluciones SIG aplicadas a problemas territoriales. Uso Python para procesamiento geoespacial, automatización y modelamiento, incluyendo clasificación de uso de suelo con Random Forest y U-Net y análisis de accesibilidad con redes viales. Trabajo con datos multiespectrales, radar y modelos de elevación para generar cartografía y productos técnicos para la planificación y la toma de decisiones.</p>
<h2>Formación</h2>
<ul class="tiempo"><li><span class="fecha">Titulado el 22 de mayo de 2025</span><h3>Geógrafo</h3><p class="lugar">Universidad Austral de Chile, Valdivia. Área: medio ambiente.</p></li></ul>
<h2>Experiencia</h2>
<ul class="tiempo">{exp}</ul>
<h2>Publicaciones</h2>
<div class="cita">{CITA}</div>
<h2>Competencias técnicas</h2>
<table><thead><tr><th>Programa o lenguaje</th><th>Nivel</th></tr></thead><tbody>{hab}</tbody></table>
<h2>Idiomas</h2>
<p>Español nativo. Inglés de nivel laboral y cotidiano (cinco meses de experiencia en California, Estados Unidos).</p>
<h2>Contacto</h2>
{contacto_html()}
</div></section>"""
    pagina("/cv/", f"Currículum de {NOMBRE} | Geógrafo, Universidad Austral de Chile",
           "CV de Gabriel Quezada Mata, geógrafo titulado en la Universidad Austral de Chile: experiencia en teledetección, SIG, accesibilidad, levantamiento GNSS y cartografía en Valdivia y el sur de Chile.",
           cuerpo, prioridad="0.9", tipo_og="profile",
           jsonld=[ld_migas(("Currículum", "/cv/")),
                   {"@type": "ProfilePage", "url": f"{BASE}/cv/", "mainEntity": {"@id": f"{BASE}/#persona"},
                    "dateModified": HOY, "inLanguage": "es"}])

def ingles():
    cuerpo = f"""
<div class="portada">{curvas_svg()}<div class="envoltura">
<div>
<p class="antetitulo">Geographer | Valdivia, Chile</p>
<h1>{NOMBRE}</h1>
<p class="subtitulo">I am a geographer from Universidad Austral de Chile. I use satellite imagery, machine learning and GIS to understand how land changes, and cartography to make those results clear.</p>
<div class="botones"><a class="boton lleno" href="/proyectos/">Projects (Spanish)</a><a class="boton" href="#contact">Contact</a></div>
</div>
<figure class="figura-portada retrato"><img src="/img/gabriel-quezada-mata-geografo.webp" alt="Gabriel Quezada Mata, geographer" width="554" height="689"></figure>
</div></div>
<section><div class="envoltura ficha">
<h2>What I do</h2>
<ul>
<li><strong>Remote sensing:</strong> Landsat, Sentinel-1 and Sentinel-2 time series; land use and land cover (LULC) classification with Random Forest, XGBoost and U-Net.</li>
<li><strong>Accessibility analysis:</strong> travel times over OpenStreetMap road networks on H3 hexagons; municipal indicators for all of Chile.</li>
<li><strong>Cartography:</strong> technical maps, field maps, posters and illustrated maps.</li>
<li><strong>Fieldwork and data:</strong> GNSS surveys, spatial databases and Python automation.</li>
</ul>
<h2>Current work</h2>
<p>Geospatial data analyst at Universidad Austral de Chile for the FONDEF IDeA project SIS-CoSu (ID26I10080): multitemporal land cover classification of Valdivia with a U-Net, reconstruction of 1990s land cover and simulation of future scenarios.</p>
<h2>Publication</h2>
<div class="cita">Quezada Mata, G., Maturana Miranda, F., Morales Soto, M., &amp; Iribarren Anacona, P. (2026). <em>{e(ARTICULO['titulo_en'])}</em> [in Spanish]. Cuadernos Geográficos, 65(1), 26-50. <a href="https://doi.org/{DOI}">https://doi.org/{DOI}</a></div>
<h2 id="contact">Contact</h2>
{contacto_html()}
</div></section>"""
    pagina("/en/", f"{NOMBRE} | Geographer in Valdivia, Chile: GIS, remote sensing and cartography",
           "Gabriel Quezada Mata is a geographer from Universidad Austral de Chile in Valdivia: remote sensing, land cover classification with machine learning, accessibility analysis, GIS and cartography.",
           cuerpo, lang="en", hreflang=[("es", "/"), ("en", "/en/"), ("x-default", "/")], prioridad="0.8")

def error404():
    cuerpo = """<section><div class="envoltura ficha"><h1>Esta página no está en el mapa</h1>
<p>La dirección no existe o cambió. <a href="/">Volver al inicio</a> o ver los <a href="/proyectos/">proyectos</a>.</p></div></section>"""
    pagina("/404.html", f"Página no encontrada | {NOMBRE}", "Página no encontrada.", cuerpo,
           extra_head='<meta name="robots" content="noindex">')

def extras():
    with open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url, pr in MAPA:
            f.write(f"  <url><loc>{url}</loc><lastmod>{HOY}</lastmod><priority>{pr}</priority></url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    with open(os.path.join(RAIZ, "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"')
                .replace("var(--acento)", "#2e6a4e").replace("var(--papel)", "#f5f2ea"))
    open(os.path.join(RAIZ, ".nojekyll"), "w").close()
    dominio = BASE.split("//")[1]
    cname = os.path.join(RAIZ, "CNAME")
    if not dominio.endswith("github.io"):
        with open(cname, "w") as f: f.write(dominio + "\n")
    elif os.path.exists(cname): os.remove(cname)

if __name__ == "__main__":
    inicio(); indice_proyectos(); cartografia()
    for p in PROYECTOS: pagina_proyecto(p)
    publicaciones(); articulo(); cv(); ingles(); error404(); extras()
    print(f"{len(MAPA)} páginas generadas para {BASE}" + ("" if CORREO else " (sin correo: define CORREO_SITIO)"))
