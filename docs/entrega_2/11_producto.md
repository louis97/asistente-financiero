# Producto de datos (punto 11)

Las demás secciones de este documento las completa la documentación del producto.

## Despliegue

Esta guía conecta el repositorio con las cuentas gratuitas que usa el producto: Supabase (base de datos), Render (API), Streamlit Community Cloud (dashboard) y GitHub Actions (tarea diaria). Ningún valor secreto se escribe en el repositorio: se pegan solo en los paneles que se indican.

### 1. Antes de empezar

1. El repositorio debe estar en GitHub y ser público.
2. El despliegue se hace desde la rama `entrega-2` (la rama `main` conserva la entrega 1 y no se fusiona). Render y Streamlit se configuran con esa rama.
3. El archivo `requirements.txt` de la raíz (lo usa Render) ya está exportado. Si cambian las dependencias, se regenera con `uv export --no-hashes --no-dev --no-emit-project --group app -o requirements.txt` (sin `--no-emit-project` traería la línea `-e .` y `pip install` fallaría). Comprobar que `grep -c "^-e" requirements.txt` da `0`.
4. El dashboard usa su propio `app/dashboard/requirements.txt` (cuatro paquetes con versión fija), que tiene precedencia sobre el de la raíz en Streamlit Community Cloud.
5. Secretos que se van a cargar (nombre, dónde y para qué; los valores nunca van en archivos):

| Dónde | Nombre | Para qué |
|---|---|---|
| Render | `SUPABASE_URL` | Dirección del proyecto de Supabase |
| Render | `SUPABASE_KEY` | Clave de servicio (`service_role`) de Supabase |
| Render | `CODIGOS_HASH` | JSON alias → huella (sha256) del código de acceso |
| Render | `SEC_USER_AGENT` | Tu nombre y correo, como pide la SEC, para consultar EDGAR a demanda |
| Render | `DATA_DIR` | Carpeta de datos; ya viene en `render.yaml` (`data/produccion`) |
| Streamlit Cloud | `API_URL` | Dirección pública de la API en Render |
| GitHub Actions | `SEC_USER_AGENT` | Lo mismo que en Render, para la tarea diaria |
| GitHub Actions | `API_URL` | Dirección de la API, para el keep-alive |

### 2. Supabase

1. Entra a supabase.com con tu cuenta de GitHub y pulsa "New project". Plan gratuito, la región más cercana. Anota la contraseña de la base de datos en un lugar privado (no se usa en el producto).
2. Abre "SQL Editor" → "New query", pega **todo** el contenido de `app/api/supabase.sql` y pulsa "Run". Crea tres tablas (`decisiones`, `niveles_usuario` y `salud`) y da a la clave de servicio los permisos mínimos sobre ellas. Se puede volver a ejecutar completo sin riesgo ni pérdida de datos.
3. En "Table Editor" comprueba que las tres tablas muestran RLS activado.
4. En "Project Settings" → "API" copia "Project URL" (será `SUPABASE_URL`; exactamente `https://<ref>.supabase.co`, sin `/` final ni `/rest/v1`, que la API agrega sola) y la clave de servicio: "service_role" o, en el panel nuevo, "Secret key" (empieza por `sb_secret_`); será `SUPABASE_KEY`. **No** uses la clave "anon" ni la "Publishable" (`sb_publishable_`): con ella la API no puede leer ni escribir y `/estado` dirá `supabase_ok: false`. Esa clave solo se pega en Render: nunca en el dashboard, en GitHub ni en archivos.
5. `SEC_USER_AGENT` es tu nombre y correo (por ejemplo, "Nombre Apellido correo@dominio.com"); la SEC lo exige para identificar quién consulta.

### 3. Códigos de acceso

1. Por cada usuario elige un alias y un código de 12 o más caracteres.
2. Ejecuta `uv run python scripts/generar_hash_codigo.py <alias>`. Pide el código sin mostrarlo (así no queda en el historial de la terminal) e imprime una línea `"alias": "huella"`.
3. Junta las líneas en un JSON, por ejemplo `{"alias1": "huella1", "alias2": "huella2"}`; ese texto es `CODIGOS_HASH`.
4. El código en claro se entrega a cada usuario por un canal privado y no se guarda en el repositorio.

### 4. Render (API)

1. Entra a render.com con tu cuenta de GitHub. Pulsa "New" → "Blueprint" y elige el repositorio; en la rama escribe `entrega-2`.
2. Render lee `render.yaml`. Pega los cuatro valores marcados como secretos (`SUPABASE_URL`, `SUPABASE_KEY`, `CODIGOS_HASH`, `SEC_USER_AGENT`) y pulsa "Apply".
3. Espera al primer despliegue ("Live") y copia la dirección `https://<servicio>.onrender.com`; es `API_URL`.
4. Aviso: el plan gratuito duerme el servicio tras unos 15 minutos sin tráfico y la primera petición tarda cerca de 1 minuto en despertarlo.
5. No definas `ACCESO_ABIERTO` en Render: desactivaría el acceso por código.

### 5. Streamlit Community Cloud (dashboard)

1. Entra a share.streamlit.io con tu cuenta de GitHub y pulsa "Create app".
2. Elige el repositorio, la rama `entrega-2` y el archivo principal `app/dashboard/app.py`.
3. En "Advanced settings" elige Python 3.12 y en "Secrets" escribe `API_URL = "https://<servicio>.onrender.com"`.
4. Pulsa "Deploy" y copia la dirección pública del dashboard.
5. Tras el primer despliegue, abre "Manage app" y confirma en el registro de instalación que instaló desde `app/dashboard/requirements.txt` y sin errores.

### 6. GitHub Actions (tarea diaria)

1. En el repositorio: Settings → Secrets and variables → Actions → "New repository secret". Crea `SEC_USER_AGENT` (tu nombre y correo) y `API_URL` (la dirección de Render).
2. Settings → Actions → General → "Workflow permissions": marca "Read and write permissions" y "Save".
3. GitHub solo ejecuta el cron diario (`schedule`) desde la rama por defecto del repositorio. Por eso, hasta el cierre de la entrega 2, la rama por defecto es `entrega-2`: Settings → General → "Default branch" → cambiar a `entrega-2` → "Update". La rama `main` no se modifica y conserva la entrega 1. El workflow hace commit y push a la misma rama en la que corre.
4. La primera ejecución de la tarea diaria solo siembra `data/produccion/` desde la instantánea (la siembra ya viene hecha y versionada en el repositorio); desde la siguiente descarga, precios (con y sin ajuste por dividendos), splits, ratios y la latencia de los reportes nuevos se actualizan solos; así los múltiplos y percentiles (historia, industria y P/E normalizado) quedan al día. Si la carpeta es anterior a este cambio y solo faltan `precios_semanales_sd` y `splits`, la tarea no siembra nada (no pisa los precios actuales con los de la instantánea): los descarga y los escribe en esa misma ejecución. Casi todos los días habrá un commit de datos: el ajuste por dividendos reescribe el histórico de precios y la barra semanal en curso cambia; es lo esperado.
5. Segunda ejecución con descarga real (la hace Actions o tú en la terminal): `SEC_USER_AGENT="<tu nombre y correo>" uv run python scripts/actualizar_datos.py; echo "codigo=$?"; wc -l data/produccion/latencia.csv`. Esperado: `codigo=0` y `latencia.csv` sin filas con `filed` anterior a la fecha de `primera_ejecucion` (1 línea si no hubo reportes nuevos).

### 7. Comprobar que todo funciona

1. Tarea diaria: `gh workflow run actualizar.yml --ref entrega-2 && sleep 20 && gh run list --workflow=actualizar.yml --limit 1` y luego `gh run watch`. Esperado: `completed success`; si no había datos nuevos, el paso "Commit" no crea commit.
2. API: `curl -s --max-time 120 "$API_URL/estado"`. Esperado: JSON con `ultimo_dato`, `ultimo_recalculo` y `supabase_ok: true` (la primera llamada puede tardar cerca de 1 minuto).
3. Dashboard: `curl -sL -c /tmp/cookies -b /tmp/cookies -o /dev/null -w "%{http_code}\n" --max-time 60 "$URL_DASHBOARD"`. Esperado: `200`. Sin `-L` y las cookies se ve `303`: es la redirección normal con la que Streamlit pone su cookie, no un error.
4. Lecturas públicas: `curl -s -X POST "$API_URL/lecturas" -H 'Content-Type: application/json' -d '{"ticker":"KO","entradas":[],"salidas":[]}' | head -c 300`. Esperado: una respuesta de la API (un 422 por niveles vacíos es aceptable); nunca 500 ni 401.
5. Supabase en vivo (con la clave real; las variables se exportan en la terminal, no en archivos):
   1. En "Table Editor" las tres tablas (`decisiones`, `niveles_usuario`, `salud`) con RLS activado.
   2. `export SUPABASE_URL=... SUPABASE_KEY=... CODIGOS_HASH='{"ana":"<huella1>","beto":"<huella2>"}'` y `uv run uvicorn app.api.main:app --port 8000`. Si el cliente rechazara una clave `sb_secret_`, usa la clave `service_role` clásica.
   3. `curl -s localhost:8000/estado` debe dar `supabase_ok: true`. Sin encabezados `X-Alias` y `X-Codigo`, `/decisiones` y `/niveles/KO` dan 401; con alias o código errado, el mismo 401 sin más detalle (por diseño).
   4. Con el código correcto de cada alias: un POST a `/decisiones` de `ana` deja una fila con `alias = 'ana'` y ninguna de `beto`; un PUT a `/niveles/KO` de cada uno con valores distintos deja una fila por `(alias, 'KO')` y cada uno lee solo la suya.
   5. Dos PUT seguidos del mismo alias y ticker dejan una sola fila con `actualizado` distinto (el upsert actualiza y no duplica).
   6. Con una clave sin permisos (la pública anon o `sb_publishable_`) `/estado` debe dar `supabase_ok: false` y `/decisiones` 503. Con `SUPABASE_URL` inválida, `/estado` responde 200 en menos de 5 s con `false` y el arranque no falla.
6. EDGAR a demanda (con `SEC_USER_AGENT` en Render): una lectura de un ticker fuera de la piloto con un nivel en unidad `pe` debe calcular el P/E implícito.
7. Memoria en Render: tras unas 5 llamadas a `POST /lecturas` (tickers distintos, uno fuera de la piloto), abre el servicio → "Metrics" → "Memory" y registra aquí el pico. Esperado: menos de 512 MB (el límite del plan gratuito; esta cifra no pudo confirmarse en la documentación de Render: contrástala con el tipo de instancia que muestra tu panel). Pico registrado: _pendiente_.
8. Falla controlada (en un fork o rama de prueba): corre el workflow con `SEC_USER_AGENT` vacío. Esperado: "Descargar y recalcular" falla, "Commit" se omite, "Keep-alive" corre y `git log -1 -- data/produccion/estado.json` no cambia.

### 8. Si algo falla

| Síntoma | Causa | Qué hacer |
|---|---|---|
| El workflow queda en rojo en "Descargar y recalcular" | Falló yfinance o EDGAR, o falta `SEC_USER_AGENT` | Nada, si es una caída pasajera: no se escribe nada y el dashboard muestra la fecha del último dato bueno. Si falta el secreto, créalo (sección 6) |
| El cron no se ejecuta | El workflow no está en la rama por defecto, o el repositorio estuvo 60 días sin actividad | Ver sección 6, paso 3 |
| 401 en la API | Alias o código mal escrito | Revisa ambos; por diseño no se da más detalle |
| El dashboard tarda cerca de 1 minuto | Arranque en frío de Render | Esperar; el keep-alive solo mantiene Supabase, no la API |
| "Keep-alive" en rojo | `API_URL` mal escrito o API caída | Revisa el secreto `API_URL` |
| `supabase_ok: false` | Clave sin permisos, URL mal escrita o proyecto pausado | Revisa `SUPABASE_URL` y `SUPABASE_KEY` en Render |

### Arranque en frío y memoria

- Render gratuito duerme el servicio tras unos 15 minutos sin tráfico; el despertar toma cerca de 1 minuto.
- En local la API arranca en unos 2 s y usa unos 250 MB (cota inferior); la cifra de Render se registra en la sección 7, paso 7.
