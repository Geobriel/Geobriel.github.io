/* Visor de capas de la portada. Requiere maplibre-gl y h3-js.
   Los colores de las capas se cambian en el bloque CONFIGURACIÓN de abajo (formato #rrggbb). */
(function () {
  /* ================================================================= CONFIGURACIÓN */
  const COLOR_PUNTOS = "#222222";          // lugares de trabajo
  const COLOR_CONTORNO = "#222222";        // contorno de las comunas de estudio
  // tiempos de viaje: de cerca (azul) a lejos (rojo), 6 clases
  const RAMPA_TIEMPO = ["#2b83ba", "#abdda4", "#ffffbf", "#fdae61", "#f46d43", "#d7191c"];
  // conexión a caminos pavimentados: de poca (rojo) a total (azul), 5 clases
  const RAMPA_PAV = ["#d7191c", "#fdae61", "#ffffbf", "#abdda4", "#2b83ba"];
  // límites de cada clase (minutos o %)
  const CORTES = {
    comuna: { salud: [8, 12, 16, 22, 35], educ: [6, 8, 11, 16, 30], finan: [15, 25, 35, 50, 80] },
    hex: { salud: [5, 10, 20, 30, 45], educ: [5, 10, 15, 25, 40], finan: [20, 35, 50, 70, 100] },
  };
  const CORTES_PAV = [20, 40, 60, 80];
  const COLOR_JARDIN = { Dosel: "#4f7a3a", Pasto: "#b8dc8c", Humedal: "#8a7a5c", Sendero: "#ffffff", otro: "#9a9a9a" };
  const COLOR_PERIMETRO = "#222222";
  /* ================================================================================ */
  const CENTRO_SUR = [[-75.5, -44.5], [-68.5, -32.5]];
  const SUR = [[-74.6, -46.2], [-70.4, -36.2]];
  const ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/";
  const base = {
    claro: { tiles: [ESRI + "Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"], ref: ESRI + "Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
             attribution: "Mapa base © Esri, HERE, Garmin, OpenStreetMap" },
    oscuro: { tiles: [ESRI + "Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"], ref: ESRI + "Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
              attribution: "Mapa base © Esri, HERE, Garmin, OpenStreetMap" },
    satelite: { tiles: [ESRI + "World_Imagery/MapServer/tile/{z}/{y}/{x}"], attribution: "Imágenes © Esri, Maxar, Earthstar Geographics" },
  };

  const mapa = new maplibregl.Map({
    container: "mapa",
    style: {
      version: 8,
      sources: {
        claro: { type: "raster", tiles: base.claro.tiles, tileSize: 256, attribution: base.claro.attribution, maxzoom: 16 },
        "claro-nombres": { type: "raster", tiles: [base.claro.ref], tileSize: 256, maxzoom: 16 },
        oscuro: { type: "raster", tiles: base.oscuro.tiles, tileSize: 256, attribution: base.oscuro.attribution, maxzoom: 16 },
        "oscuro-nombres": { type: "raster", tiles: [base.oscuro.ref], tileSize: 256, maxzoom: 16 },
        satelite: { type: "raster", tiles: base.satelite.tiles, tileSize: 256, attribution: base.satelite.attribution, maxzoom: 19 },
      },
      layers: [
        { id: "claro", type: "raster", source: "claro" },
        { id: "oscuro", type: "raster", source: "oscuro", layout: { visibility: "none" } },
        { id: "satelite", type: "raster", source: "satelite", layout: { visibility: "none" } },
        { id: "oscuro-nombres", type: "raster", source: "oscuro-nombres", layout: { visibility: "none" } },
        { id: "nombres", type: "raster", source: "claro-nombres" },
      ],
    },
    bounds: SUR, fitBoundsOptions: { padding: 20 },
    cooperativeGestures: true, attributionControl: { compact: true },
    locale: { "CooperativeGesturesHandler.WindowsHelpText": "Usa Ctrl + rueda para hacer zoom",
              "CooperativeGesturesHandler.MacHelpText": "Usa ⌘ + rueda para hacer zoom",
              "CooperativeGesturesHandler.MobileHelpText": "Usa dos dedos para mover el mapa" },
  });
  mapa.on("error", (e) => console.error("mapa:", e.error && e.error.message));
  window.__mapa = mapa;
  mapa.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-left");
  mapa.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");

  const cache = {};
  const cargar = async (archivo) => (cache[archivo] ??= fetch(`/mapa/${archivo}`).then(r => r.json()));
  const paso = (prop, rampa, cortes) => ["step", ["get", prop], rampa[0], ...cortes.flatMap((c, i) => [c, rampa[i + 1]])];
  const popup = (lngLat, html) => new maplibregl.Popup({ maxWidth: "280px" }).setLngLat(lngLat).setHTML(html).addTo(mapa);
  const esc = (t) => String(t ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const visible = (ids, si) => ids.forEach(id => mapa.getLayer(id) && mapa.setLayoutProperty(id, "visibility", si ? "visible" : "none"));
  const antesDe = () => "nombres";

  /* ---------------------------------------------------------------- capas */
  const capas = {
    async lugares(si) {
      if (!mapa.getSource("lugares")) {
        mapa.addSource("lugares", { type: "geojson", data: await cargar("lugares.json") });
        mapa.addLayer({ id: "lugares", type: "circle", source: "lugares",
          paint: { "circle-radius": 6, "circle-color": COLOR_PUNTOS, "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
        mapa.on("click", "lugares", e => {
          const p = e.features[0].properties, items = JSON.parse(p.items);
          popup(e.lngLat, `<strong>${esc(p.lugar)}</strong><ul>${items.map(([t, u]) =>
            `<li>${u ? `<a href="${u}">${esc(t)}</a>` : esc(t)}</li>`).join("")}</ul>`);
        });
        puntero("lugares");
      }
      visible(["lugares"], si);
    },
    async estudio(si) {
      if (!mapa.getSource("estudio")) {
        mapa.addSource("estudio", { type: "geojson", data: await cargar("comunas_estudio.json") });
        mapa.addLayer({ id: "estudio-linea", type: "line", source: "estudio",
          paint: { "line-color": COLOR_CONTORNO, "line-width": 1.5, "line-dasharray": [3, 2] } }, mapa.getLayer("lugares") ? "lugares" : undefined);
      }
      visible(["estudio-linea"], si);
    },
    async cobertura2016(si) { await cobertura(2016, si); },
    async cobertura2024(si) { await cobertura(2024, si); },
    async jardin(si) {
      if (!mapa.getSource("jardin")) {
        mapa.addSource("jardin", { type: "geojson", data: await cargar("jardin_botanico.json") });
        mapa.addLayer({ id: "jardin", type: "fill", source: "jardin", filter: ["!=", ["get", "uso"], "Perímetro"],
          paint: { "fill-color": ["match", ["get", "uso"], "Dosel", COLOR_JARDIN.Dosel, "Pasto", COLOR_JARDIN.Pasto, "Humedal", COLOR_JARDIN.Humedal,
                                  "Sendero", COLOR_JARDIN.Sendero, COLOR_JARDIN.otro], "fill-opacity": 0.9 } }, antesDe());
        mapa.addLayer({ id: "jardin-borde", type: "line", source: "jardin", filter: ["==", ["get", "uso"], "Perímetro"],
          paint: { "line-color": COLOR_PERIMETRO, "line-width": 2 } }, antesDe());
        mapa.on("click", "jardin", e => {
          const p = e.features[0].properties;
          popup(e.lngLat, `<strong>${esc(p.uso)}</strong>${p.zona ? `<br>${esc(p.zona)}` : ""}`);
        });
        puntero("jardin");
      }
      visible(["jardin", "jardin-borde"], si);
      if (si) mapa.fitBounds(caja(await cargar("jardin_botanico.json")), { padding: 30 });
    },
  };

  async function cobertura(anio, si) {
    const id = `cobertura-${anio}`;
    if (!mapa.getSource(id)) {
      const meta = await cargar("capas.json");
      mapa.addSource(id, { type: "image", url: `/mapa/cobertura_${anio}.png`, coordinates: meta.cobertura[anio] });
      mapa.addLayer({ id, type: "raster", source: id, paint: { "raster-opacity": 0.9, "raster-resampling": "nearest" } }, antesDe());
    }
    visible([id], si);
    if (si) mapa.fitBounds([[-73.45, -40.0], [-72.95, -39.6]], { padding: 20 });
  }

  /* indicadores por comuna (uno a la vez) */
  const INDICADOR = {
    salud: ["Tiempo a salud (min)", "salud"], educ: ["Tiempo a educación media (min)", "educ"],
    finan: ["Tiempo a servicios financieros (min)", "finan"], pav: ["Conexión a caminos pavimentados (%)", "pav"],
  };
  async function indicador(clave) {
    if (!mapa.getSource("comunas")) {
      mapa.addSource("comunas", { type: "geojson", data: await cargar("comunas.json") });
      mapa.addLayer({ id: "comunas", type: "fill", source: "comunas", layout: { visibility: "none" },
        paint: { "fill-opacity": 0.85 } }, antesDe());
      mapa.addLayer({ id: "comunas-borde", type: "line", source: "comunas", layout: { visibility: "none" },
        paint: { "line-color": "#ffffff", "line-width": 0.3 } }, antesDe());
      mapa.on("click", "comunas", e => {
        const p = e.features[0].properties, c = mapa.__indicador;
        if (!c) return;
        const v = p[c], unidad = c === "pav" ? " %" : " min";
        popup(e.lngLat, `<strong>${esc(p.n)}</strong><br>${INDICADOR[c][0].replace(/ \(.*\)/, "")}: ${v == null ? "sin dato" : v + unidad}`);
      });
      puntero("comunas");
    }
    mapa.__indicador = clave || null;
    if (clave) {
      const color = clave === "pav" ? paso("pav", RAMPA_PAV, CORTES_PAV) : paso(clave, RAMPA_TIEMPO, CORTES.comuna[clave]);
      mapa.setPaintProperty("comunas", "fill-color", ["case", ["==", ["get", clave], null], "#bdbdbd", color]);
      mapa.fitBounds(CENTRO_SUR, { padding: 10 });
    }
    visible(["comunas", "comunas-borde"], !!clave);
  }

  /* hexágonos H3 */
  let hexListo = false;
  async function hexagonos(clave) {
    if (!hexListo && clave) {
      const datos = await cargar("hexagonos.json");
      const feats = [];
      for (const [comuna, filas] of Object.entries(datos)) {
        for (const [h, salud, educ, finan] of filas) {
          const idx = h.length === 9 ? `89${h}ffff` : h;
          feats.push({ type: "Feature", properties: { c: comuna, salud, educ: educ < 0 ? null : educ, finan: finan < 0 ? null : finan },
                       geometry: { type: "Polygon", coordinates: [h3.cellToBoundary(idx, true)] } });
        }
      }
      mapa.addSource("hex", { type: "geojson", data: { type: "FeatureCollection", features: feats }, tolerance: 0.2 });
      mapa.addLayer({ id: "hex", type: "fill", source: "hex", paint: { "fill-opacity": 0.85 } }, antesDe());
      mapa.on("click", "hex", e => {
        const p = e.features[0].properties, c = mapa.__hex, v = p[c];
        popup(e.lngLat, `<strong>${esc(p.c)}</strong><br>${HEX[c]}: ${v == null || v === "null" ? "sin dato" : v + " min"}`);
      });
      puntero("hex");
      hexListo = true;
    }
    mapa.__hex = clave || null;
    if (clave) {
      mapa.setPaintProperty("hex", "fill-color", ["case", ["==", ["get", clave], null], "#bdbdbd", paso(clave, RAMPA_TIEMPO, CORTES.hex[clave])]);
      mapa.fitBounds([[-73.45, -40.0], [-72.95, -39.6]], { padding: 20 });
    }
    visible(["hex"], !!clave);
    avisoZoom();
  }
  function avisoZoom() {
    const aviso = document.getElementById("aviso-zoom");
    if (aviso) aviso.hidden = !(mapa.__hex && mapa.getZoom() < 8.5);
  }
  mapa.on("zoomend", avisoZoom);
  const HEX = { salud: "Tiempo a salud", educ: "Tiempo a educación", finan: "Tiempo a servicios financieros" };

  function caja(gj) {
    let o = 180, s = 90, e = -180, n = -90;
    const rec = (c) => (typeof c[0] === "number" ? (o = Math.min(o, c[0]), e = Math.max(e, c[0]), s = Math.min(s, c[1]), n = Math.max(n, c[1])) : c.forEach(rec));
    gj.features.forEach(f => rec(f.geometry.coordinates));
    return [[o, s], [e, n]];
  }

  function puntero(id) {
    mapa.on("mouseenter", id, () => (mapa.getCanvas().style.cursor = "pointer"));
    mapa.on("mouseleave", id, () => (mapa.getCanvas().style.cursor = ""));
  }

  /* ---------------------------------------------------------------- leyendas */
  const filas = (rampa, cortes, unidad) => rampa.map((c, i) => {
    const t = i === 0 ? `menos de ${cortes[0]}` : i === rampa.length - 1 ? `${cortes[i - 1]} o más` : `${cortes[i - 1]} a ${cortes[i]}`;
    return `<li><i style="background:${c}"></i>${t} ${unidad}</li>`;
  }).join("");
  async function leyendas() {
    const f = document.getElementById("capas"), cont = document.getElementById("leyenda");
    const partes = [];
    if (f.cobertura2016.checked || f.cobertura2024.checked) {
      const meta = await cargar("capas.json");
      partes.push(`<p>Cobertura de suelo</p><ul>${meta.leyenda_cobertura.map(([n, c]) => `<li><i style="background:${c}"></i>${n}</li>`).join("")}</ul>`);
    }
    if (f.indicador.value) partes.push(`<p>${INDICADOR[f.indicador.value][0]}</p><ul>${f.indicador.value === "pav"
      ? filas(RAMPA_PAV, CORTES_PAV, "%") : filas(RAMPA_TIEMPO, CORTES.comuna[f.indicador.value], "min")}</ul>`);
    if (f.hex.value) partes.push(`<p>${HEX[f.hex.value]} por hexágono</p><ul>${filas(RAMPA_TIEMPO, CORTES.hex[f.hex.value], "min")}</ul>`);
    if (f.jardin.checked) partes.push(`<p>Jardín Botánico</p><ul><li><i style="background:${COLOR_JARDIN.Dosel}"></i>Dosel</li><li><i style="background:${COLOR_JARDIN.Pasto}"></i>Pasto</li><li><i style="background:${COLOR_JARDIN.Humedal}"></i>Humedal</li><li><i style="background:${COLOR_JARDIN.Sendero};outline:1px solid #888"></i>Senderos</li></ul>`);
    cont.innerHTML = partes.join("");
  }

  /* ---------------------------------------------------------------- controles */
  let iniciado = false;
  const iniciar = async () => {
    if (iniciado) return; iniciado = true;
    const f = document.getElementById("capas");
    await capas.lugares(true);
    await capas.estudio(true);
    f.addEventListener("change", async (ev) => {
      const el = ev.target;
      try {
        if (el.name === "base") {
          visible(["claro", "nombres"], el.value === "claro"); visible(["oscuro", "oscuro-nombres"], el.value === "oscuro");
          visible(["satelite"], el.value === "satelite");
        }
        else if (el.name === "indicador") { if (el.value && f.hex.value) { f.hex.value = ""; await hexagonos(""); } await indicador(el.value); }
        else if (el.name === "hex") { if (el.value && f.indicador.value) { f.indicador.value = ""; await indicador(""); } await hexagonos(el.value); }
        else if (capas[el.name]) await capas[el.name](el.checked);
        await leyendas();
      } catch (err) { console.error(err); }
    });
  };
  if (mapa.isStyleLoaded()) iniciar(); else mapa.once("style.load", iniciar);
})();
