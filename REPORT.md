# Resultados de la auditoria Brasaland

Fecha de la serie comparable: 2026-10-09, 23:06-23:17 UTC.
Se conservan las mismas tres URLs y los mismos perfiles de dispositivo.
Resultados: medianas de tres pasadas. Protocolo y excepcion de arranque:
[AUDIT.md](AUDIT.md).

## Puntuaciones Lighthouse

Cada celda expresa `antes -> despues`.

| Pagina | Dispositivo | Performance | Accessibility | Best Practices | SEO |
| --- | --- | --- | --- | --- | --- |
| Portada | Movil | 72 -> 100 | 92 -> 100 | 100 -> 100 | 91 -> 100 |
| Portada | Escritorio | 85 -> 100 | 92 -> 100 | 100 -> 100 | 91 -> 100 |
| Registro | Movil | 96 -> 100 | 77 -> 100 | 93 -> 100 | 90 -> 100 |
| Registro | Escritorio | 100 -> 100 | 77 -> 100 | 96 -> 100 | 90 -> 100 |
| Dashboard | Movil | 79 -> 99 | 93 -> 100 | 100 -> 100 | 90 -> 50 |
| Dashboard | Escritorio | 86 -> 100 | 93 -> 100 | 100 -> 100 | 90 -> 50 |

El descenso SEO interno corresponde a `noindex`; no es una regresion de SEO
publico. Una puntuacion 100 de laboratorio no garantiza velocidad ni accesibilidad
perfectas en todos los dispositivos reales.

## Metricas de carga

| Pagina / dispositivo | LCP (s) | CLS | FCP (s) | TBT (ms) | TTFB (ms) | Bytes transferidos |
| --- | --- | --- | --- | --- | --- | --- |
| Portada movil | 16.356 -> 1.204 | 0 -> 0 | 2.198 -> 0.754 | 0 -> 0 | 1.66 -> 1.33 | 3,098,448 -> 73,616 |
| Portada escritorio | 2.724 -> 0.365 | 0 -> 0 | 0.528 -> 0.207 | 0 -> 0 | 0.49 -> 0.85 | 3,098,459 -> 138,257 |
| Registro movil | 2.177 -> 0.996 | 0 -> 0 | 2.177 -> 0.754 | 0 -> 0 | 0.72 -> 1.38 | 134,626 -> 18,003 |
| Registro escritorio | 0.516 -> 0.274 | 0 -> 0 | 0.516 -> 0.204 | 0 -> 0 | 1.86 -> 1.76 | 134,624 -> 18,003 |
| Dashboard movil | 2.457 -> 1.861 | 0.307 -> 0.011 | 2.306 -> 1.061 | 0 -> 17 | 0.81 -> 0.90 | 83,522 -> 87,819 |
| Dashboard escritorio | 0.676 -> 0.458 | 0.256 -> 0.012 | 0.676 -> 0.290 | 0 -> 0 | 1.63 -> 0.92 | 83,522 -> 87,819 |

La portada movil reduce el LCP un 92.6% y la transferencia un 97.6%.
Las seis medianas finales cumplen LCP <= 2.5 s y CLS <= 0.1.
No hay afirmacion sobre INP: no fue medido. TBT movil interno sube a 17 ms y los
bytes internos aumentan un 5.1%; se informa ese coste, aunque LCP y CLS mejoran.
La mejora interna viene de la ruta critica y la estabilidad, no de menos bytes.
TTFB es local y pequenas variaciones no se atribuyen a los cambios frontend.
Las muestras individuales y su variabilidad quedan en los JSON; por ejemplo,
Performance inicial del dashboard movil fue 79, 72 y 79.

## Cambios entregados

- CSS Tailwind compilado localmente para las dos paginas publicas, sin compilador
  CDN en runtime y manteniendo clases y estructura.
- Misma imagen de Brasaland en WebP de 480, 768 y 1152 px; `srcset`, `sizes`,
  dimensiones 1536 x 1024 y prioridad de descarga. Se conserva el PNG original.
- Fuentes Space Grotesk e IBM Plex Mono locales, con licencias OFL junto a los
  archivos; scripts `defer` y precarga de la fuente principal del dashboard.
- Correccion minima del bloqueo global de auxiliares, con prueba especifica.
- Perfil reutilizado desde `/auth/me`: 3 -> 2 llamadas de inicializacion.
- Estado `aria-busy` evita pintar y sustituir la pantalla de acceso durante la
  carga; se libera tambien en el manejo de error. No se modifica la autenticacion.
- Menu que envuelve y tabla que se desplaza dentro de su contenedor movil.
- Nombres accesibles para controles de registro y tarifas, contraste suficiente
  y metadescripciones publicas; exclusividad `noindex` de la vista interna.
- Componente DOM compartido `BrasalandStatusActions`, consumido en ambas consolas
  y copiado por el Dockerfile. Segundo caso de duplicacion documentado sin refactor
  innecesario del analisis CSV.

## Verificacion

- `npm test -- --runInBand`: 12 pruebas en tres suites; umbral existente de
  cobertura de auxiliares satisfecho. La cobertura global no equivale a la de las rutas UI.
- `npm run check:frontends`: Chrome 412 y 1350 px; formulario dependiente y errores,
  login/logout real, 15 filas, filtros, tarifa editada y restaurada, CSV real,
  cuatro KPI, descarga CSV, perfil actualizado/restaurado y componente compartido
  cargado en ambas consolas. No hubo errores JavaScript sin capturar.
- Imagen renderizada y ausencia de desbordamiento de documento comprobadas;
  capturas finales revisadas. La tabla conserva su scroll horizontal propio.
- `docker build -t brasaland-perf-interfaces uis`: correcto, incluye `uis/shared`.
- Las auditorias finales verifican dashboard autenticado y URL sin redireccion
  a login; cada fase conserva seis capturas completas.

## Reproduccion en Linux / Codespaces

Desde la raiz, instalar dependencias fijadas y generar recursos:

```bash
npm ci
npx playwright install chromium
npm run build:frontends
```

Terminal A, servidor estatico (solo para pruebas locales):

```bash
python -m http.server 8080 --bind 0.0.0.0
```

Terminal B, usando el entorno Python existente que contiene requirements de API:

```bash
BRASALAND_DATA_DIR=/tmp/brasaland-lighthouse-data \
DATABASE_URL=sqlite:////tmp/brasaland-lighthouse.sqlite \
AUTH_SECRET_KEY="$(openssl rand -hex 32)" \
ACCESS_TOKEN_EXPIRE_MINUTES=480 \
./.venv-1/bin/uvicorn main:app --app-dir services/api --host 127.0.0.1 --port 8000
```

Terminal C:

```bash
npm test -- --runInBand
npm run check:frontends
npm run audit:frontends -- after
```

Los scripts crean usuarios temporales con claves aleatorias y los eliminan al
terminar. Deben ejecutarse contra la API de prueba, nunca contra produccion.
Si se reutiliza el directorio temporal, conservar exactamente los 15 proveedores
semilla. La prueba modifica una tarifa y la restaura; no debe interrumpirse.
Los JWT se redactan antes de guardar los informes; no se versionan datos de API.

`AUDIT_ORIGIN`, `AUDIT_API` y `AUDIT_RUNS` permiten configurar el escenario.
`AUDIT_PAGES=backoffice-dashboard` permite retomar solo esa pagina cuando ya
existe el resumen de la fase. El valor por defecto son tres pasadas.
Para recrear un verdadero `before`, usar la revision de linea base con la
reparacion minima (`b4fedef`), no ejecutar `before` sobre el codigo optimizado.
En esa revision el ejecutor se invoca directamente con herramientas externas:

```bash
npm install --prefix /tmp/brasaland-perf-tools lighthouse@12.8.2 playwright@1.56.1
/tmp/brasaland-perf-tools/node_modules/.bin/playwright install chromium
AUDIT_TOOLS=/tmp/brasaland-perf-tools node scripts/audit-frontends.mjs before
```

Cada fase
sobrescribe sus nombres de archivos, por lo que conviene preservar la evidencia
entregada antes de repetirla. No mezclar puertos, perfiles ni servidores.

## Entrega y evidencia

Los HTML pueden abrirse desde el servidor, por ejemplo:
[portada antes](audit/before/website-home-mobile-1.html),
[portada despues](audit/after/website-home-mobile-1.html),
[dashboard antes](audit/before/backoffice-dashboard-mobile-1.html) y
[dashboard despues](audit/after/backoffice-dashboard-mobile-1.html).
Resumenes completos: [before](audit/before/summary.json) y
[after](audit/after/summary.json). Estado original roto:
[blocked](audit/blocked/summary.json).

La entrega se versiona en `perf/auditoria-lighthouse`, en el mismo repositorio
de empresa; no se crea un repositorio nuevo. El remoto de empresa configurado es
`origin` (`4GeeksAcademy/Regenerik---Hito-Company`); `fork` es una copia personal
distinta y no se sustituye por ella para cumplir la entrega.