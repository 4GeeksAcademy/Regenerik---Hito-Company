# Auditoria de rendimiento de Brasaland

Fecha: 2026-10-09. Rama: `perf/auditoria-lighthouse`.
Revision inicial: `41d9b18`; linea base funcional versionada: `b4fedef`.
Se trabaja sobre el monorepo de empresa existente,
sin reconstruir ni redisenar las aplicaciones.

## Superficies reales

La web corporativa es [index.html](index.html) y su segunda vista es el
formulario Brasa Points en [application.html](application.html).
[uis/web/index.html](uis/web/index.html) es otra consola protegida, no la
portada publica. No existen scripts Next.js `dev`, `build` o `start` por frontend.
La configuracion Docker existente redirige sus raices a consolas internas;
por eso no se uso para las mediciones de la web publica.

| Pagina | URL fija | Dispositivos |
| --- | --- | --- |
| Portada | http://127.0.0.1:8080/ | Movil y escritorio |
| Registro | http://127.0.0.1:8080/application.html | Movil y escritorio |
| Dashboard | http://127.0.0.1:8080/uis/backoffice/ | Movil y escritorio |

## Protocolo

- Ubuntu 24.04, Node 24.14.0, Lighthouse 12.8.2 y Playwright 1.56.1.
- Chromium 141.0.7390.37, headless, sin extensiones, mismo binario en ambas fases.
- Archivos estaticos con `python -m http.server 8080`; sin HMR ni compilador
  de desarrollo. El CSS final esta precompilado. No se compara dev con produccion.
- Movil: 412 x 823, DPR 1, RTT simulado 150 ms, 1638.4 Kbps y CPU x4.
- Escritorio: 1350 x 940, DPR 1, RTT simulado 40 ms, 10240 Kbps y CPU x1.
- Tres pasadas secuenciales por combinacion; se informa la mediana, no la mejor.
- Proceso Chrome nuevo por pasada. Se vacia la cache HTTP despues de la captura
  y antes de Lighthouse. `disableStorageReset` conserva solo la sesion necesaria;
  las aplicaciones no tienen service workers. Los informes contienen la configuracion completa.
- API FastAPI real en 8000, datos TinyDB aislados bajo `/tmp/brasaland-lighthouse-data`
  y `DATABASE_URL` SQLite temporal. No se utilizaron datos ni credenciales reales.
- Usuario temporal del mismo rol y con el mismo perfil en cada fase; 15 proveedores
  semilla, mismos filtros vacios. El dashboard se comprueba autenticado y con filas.
- Las capturas Playwright son de comprobacion visual, sin throttling; las metricas
  proceden de Lighthouse. Las trazas `sessionRequests` son diagnostico local,
  no una medicion de rendimiento de produccion.

## Excepcion de arranque anterior a la linea base

El dashboard original no ejecutaba `app.js`: las funciones globales de
[utils.js](uis/backoffice/utils.js) colisionaban con su desestructuracion
`const` en [app.js](uis/backoffice/app.js), provocando
`Identifier 'parseApiError' has already been declared`.

Antes de corregirlo se guardaron dos informes y dos capturas en
[audit/blocked/summary.json](audit/blocked/summary.json). Muestran la pantalla de
acceso sin un dashboard funcional; sus puntuaciones NO son una linea base valida.
Se encapsularon los auxiliares, conservando su contrato, y solo entonces se
midio el dashboard autenticado de `audit/before/`. La comparacion de rendimiento
del dashboard parte de esa reparacion minima, no del estado original roto.
Las pasadas exploratorias con cache caliente se descartaron y reemplazaron por
la serie fria documentada. No se presentan como evidencia comparable.

## Hallazgos y causas raiz

| Hallazgo | Evidencia inicial | Causa raiz | Correccion |
| --- | --- | --- | --- |
| Portada lenta | LCP movil 16.356 s; 3,098,448 bytes transferidos | PNG original de 2,964,476 bytes servido a todos los dispositivos, sin variantes responsivas | WebP del mismo recurso, `srcset`, `sizes`, dimensiones intrinsecas y prioridad alta |
| CSS bloqueante | Tailwind remoto: ahorro estimado 1.46 s en portada movil y 1.49 s en registro | Play CDN descarga y ejecuta el compilador en cada navegador | Tailwind 3.4.17 compilado localmente, CSS minimo con las clases existentes |
| Saltos de layout internos | CLS movil 0.307 y escritorio 0.256 | Se pintaba el login antes de autenticar, luego se sustituia por contenido y filas; fuentes externas tardias | Estado inicial `aria-busy` sin pintar contenido intermedio, fuentes locales y preload |
| Trabajo de red duplicado | `/auth/me` -> `/profiles/me` -> `/suppliers` | El perfil ya estaba en `me.profile`, pero se solicitaba otra vez en serie | Consumir el perfil incluido en `/auth/me`; dos peticiones en vez de tres |
| Desbordamiento movil | Captura y `horizontalOverflow: true` del dashboard | Minimo intrinseco de hijos de grid y tabla, y menu sin wrap | `min-width: 0` en contenedores; scroll dentro de la tabla; menu flexible |
| Formulario poco accesible | Accessibility 77; controles sin nombre y Best Practices 93 movil | Placeholders usados como etiquetas, selects/fecha sin nombre y falta de viewport | Nombres accesibles, autocomplete y viewport, sin alterar la validacion |
| Tarifas sin etiqueta | Accessibility 93 del dashboard | Inputs creados dinamicamente sin nombre accesible | Etiqueta contextual por proveedor, con prueba de regresion |
| Contraste y SEO publico | Accessibility 92 y SEO 91 en portada | Blanco sobre rojo con contraste 3.76 y falta de descripcion | Rojo de contraste suficiente y metadescripciones especificas |

## Dos casos de duplicacion

1. `addRetryButton` y `addHomeLink` en
   [uis/web/app.js](uis/web/app.js) y [uis/backoffice/app.js](uis/backoffice/app.js)
   repetian creacion, estilos y sustitucion de acciones DOM. Se extrajo el
   componente reutilizable [status-actions.js](uis/shared/status-actions.js).
   Ambos consumidores lo usan; mantiene un unico bloque por estado y permite
   botones con callback o enlaces. No se anadio React ni un Custom Hook artificial
   a aplicaciones que usan JavaScript estatico.
2. `renderSummary` en esos mismos archivos repite las tarjetas KPI, desglose de
   invalidos y tablas por categoria/estado. Se identifica pero se conserva:
   su extraccion no mejora el cuello de botella observado y ampliaria el cambio
   de renderizado del CSV. El requisito minimo de extraccion queda cubierto por
   el primer componente.

## Evidencia y limites

- [Antes](audit/before/summary.json): 18 informes HTML, 18 JSON y 6 PNG.
- [Despues](audit/after/summary.json): 18 informes HTML, 18 JSON y 6 PNG.
- Nombres: `<pagina>-<mobile|desktop>-<1|2|3>.html` y `.json`; capturas sin numero.
- LCP, CLS e INP son los Core Web Vitals actuales. FID fue sustituido por INP.
  Estos informes de carga aportan LCP, CLS, FCP, TBT y TTFB, NO un INP de campo.
  Las pruebas de clicks verifican funciones, no certifican INP. TBT no es INP.
- TTFB local no representa latencia de un despliegue real. El backend aislado no
  certifica PostgreSQL ni inventario. No se cambio codigo backend.
- `noindex, nofollow` del dashboard es intencionado: SEO interno baja a 50.
  No se fuerza la indexacion de un panel privado para obtener una puntuacion mayor.
- Quedan fuera: SEO de otras rutas, accesibilidad manual con lector de pantalla,
  INP real mediante RUM y comportamiento con miles de proveedores.
- `npm audit --omit=dev` informa cero vulnerabilidades de produccion. La instalacion
  detecto 54 avisos en herramientas de desarrollo (40 moderados, 14 altos);
  no se aplicaron upgrades forzados que cambiaran el motor de medicion a mitad de la comparacion.

Resultados y reproduccion: [REPORT.md](REPORT.md).