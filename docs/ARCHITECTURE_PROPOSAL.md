# ARCHITECTURE_PROPOSAL - Backend Brasaland

## 1. Objetivo
Definir una propuesta arquitectonica para el backend de Brasaland antes de escribir codigo, con decisiones tecnicas justificadas por la realidad del negocio y no por preferencias genericas.

## 2. Contexto de negocio que guia la arquitectura
Brasaland es una cadena de restaurantes a la brasa con operacion en Colombia y Florida (EE. UU.), con 14 ubicaciones activas y un programa de fidelizacion digital (Brasa Points).

A partir del sitio y del flujo de registro actual:
- Se registran clientes con nombre, email, telefono, pais, ciudad, ubicacion, fecha de nacimiento, fuente de adquisicion y consentimiento de terminos.
- Existen reglas de puntos segun moneda/pais (COP y USD).
- La experiencia omnicanal sera progresiva (hoy no hay pedidos online, pero se anticipa).

Impacto tecnico:
- Se necesita consistencia fuerte en reglas de puntos.
- Debe existir trazabilidad de movimientos para auditoria.
- Se requiere diseno multi-pais desde el inicio.

## 3. Patron arquitectonico propuesto y justificacion
### Propuesta principal
Monolito modular orientado a dominios, con capas internas por modulo (domain, application, infrastructure, interfaces).

### Por que este patron es el mas adecuado para Brasaland
1. El negocio comparte reglas transaccionales entre clientes, ubicaciones y puntos; dividir en microservicios desde el inicio aumentaria complejidad sin beneficio inmediato.
2. El equipo necesita velocidad de entrega para el siguiente sprint y claridad de ownership por dominio.
3. La base de clientes y las reglas de fidelizacion exigen consistencia transaccional alta; un monolito modular lo simplifica.
4. Permite evolucionar a microservicios por extraccion futura cuando haya evidencia de cuellos de botella reales.

### Alternativas evaluadas
1. Microservicios desde el dia uno:
- Pro: aislamiento fuerte por dominio.
- Contra: complejidad operativa (observabilidad distribuida, contratos, latencia, resiliencia interservicio).
- Decision: descartado en esta etapa.

2. Monolito clasico por capas tecnicas globales:
- Pro: arranque rapido.
- Contra: acoplamiento entre dominios y deterioro de mantenibilidad.
- Decision: descartado por riesgo de deuda estructural.

## 4. Estructura de carpetas y modulos backend
Ubicacion propuesta en el monorepo: services/admin-api.

```text
services/
  admin-api/
    app/
      main.py
      api/
        v1/
          router.py
          dependencies.py
          endpoints/
            health.py
            auth.py
            customers.py
            loyalty.py
            locations.py
            catalog.py
            campaigns.py
      core/
        config.py
        logging.py
        security.py
        errors.py
      modules/
        customers/
          domain/
          application/
          infrastructure/
          interfaces/
        loyalty/
          domain/
          application/
          infrastructure/
          interfaces/
        locations/
          domain/
          application/
          infrastructure/
          interfaces/
        catalog/
          domain/
          application/
          infrastructure/
          interfaces/
        campaigns/
          domain/
          application/
          infrastructure/
          interfaces/
      db/
        session.py
        base.py
        migrations/
      tests/
        unit/
        integration/
    pyproject.toml
    README.md
```

Criterio de separacion:
- Por dominio de negocio primero (customers, loyalty, locations, catalog, campaigns).
- Por responsabilidad tecnica dentro de cada dominio (regla de negocio, casos de uso, adaptadores, interfaces).

## 5. Dominios funcionales y responsabilidades
1. Customers:
- Registro, perfil y estado del cliente.
- Gestion de consentimientos y version legal aceptada.
- Preferencias de ubicacion y datos de contacto.

2. Loyalty:
- Cuenta de puntos por cliente.
- Ledger de movimientos (earn, burn, adjustment, expiration).
- Reglas por pais y moneda con auditoria.

3. Locations:
- Paises, ciudades, restaurantes, horarios, disponibilidad.
- Validaciones de relacion cliente-ubicacion.

4. Catalog:
- Productos/menu para reglas de beneficios.
- Elegibilidad por ubicacion.

5. Campaigns:
- Promociones, segmentacion, reglas y vigencias.

## 6. Endpoints y routers de FastAPI por dominio
Prefijo global propuesto: /api/v1.

Agrupacion por router:
1. health_router:
- GET /api/v1/health

2. auth_router:
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout

3. customers_router:
- POST /api/v1/customers
- GET /api/v1/customers/{customer_id}
- PATCH /api/v1/customers/{customer_id}
- POST /api/v1/customers/{customer_id}/consents

4. loyalty_router:
- GET /api/v1/loyalty/accounts/{customer_id}
- GET /api/v1/loyalty/accounts/{customer_id}/transactions
- POST /api/v1/loyalty/accounts/{customer_id}/earn
- POST /api/v1/loyalty/accounts/{customer_id}/burn

5. locations_router:
- GET /api/v1/locations/countries
- GET /api/v1/locations/cities
- GET /api/v1/locations/restaurants

6. catalog_router:
- GET /api/v1/catalog/menu-items
- GET /api/v1/catalog/menu-items/{item_id}

7. campaigns_router:
- GET /api/v1/campaigns
- POST /api/v1/campaigns
- PATCH /api/v1/campaigns/{campaign_id}

Criterio de diseno:
- Rutas orientadas a recursos.
- Acciones sensibles del dominio (earn/burn) como subrutas explicitas para evitar ambiguedad semantica.
- Versionado por URI para gestionar breaking changes.

## 7. Convenciones habituales en proyectos FastAPI y como influyen en esta propuesta
Practicas comunes observadas en FastAPI:
1. Separar transporte HTTP de logica de negocio (routers vs services/use-cases).
2. Centralizar configuracion y dependencias en core y api/dependencies.
3. Versionar API desde el inicio (por ejemplo, api/v1).
4. Gestionar modelos de entrada/salida de forma explicita y validada.
5. Mantener migraciones en un directorio dedicado para control de esquema.

Origen explicito de estas convenciones:
1. Documentacion oficial de FastAPI (estructura con APIRouter, dependencias, validacion con modelos y documentacion OpenAPI).
2. Practica estandar de proyectos backend Python con separacion de configuracion, acceso a datos y capa HTTP.
3. Recomendaciones recurrentes en plantillas educativas de FastAPI usadas en formacion backend (rutas por dominio y versionado desde el arranque).

Como impactan nuestras decisiones:
- Adoptamos carpeta api/v1/endpoints para routers por dominio.
- Definimos core/config.py para entorno y settings.
- Separamos modules por dominio para evitar mezclar negocio con infraestructura.
- Definimos db/migrations para evolucion de datos controlada.
- Priorizamos test unitario en reglas de loyalty por su criticidad.

## 8. Aplicacion con frontend y backend separados
Modelo recomendado en este proyecto:
- Monorepo con sistemas separados por carpeta (uis para frontend, services para backend).
- Comunicacion exclusivamente por API HTTP/JSON.

Consideraciones clave:
1. Contrato API:
- OpenAPI como fuente unica de verdad para alineacion frontend/backend.

2. Configuracion por entorno:
- Variables separadas por dev/staging/prod para URLs de API, llaves y toggles.

3. CORS:
- Lista blanca por entorno para permitir solo origins esperados.

4. Desacoplamiento de despliegue:
- Frontend y backend deben poder desplegarse de manera independiente, con versionado coordinado por contrato.

5. Manejo de errores consistente:
- Formato uniforme (code, message, details, request_id) para simplificar UX y debugging.

## 9. Decisiones tecnicas iniciales
1. API framework: FastAPI.
2. Validacion: Pydantic v2.
3. Base de datos principal: PostgreSQL.
4. Acceso a datos: SQLAlchemy 2.x + Alembic.
5. Seguridad: JWT (access/refresh) y RBAC basico.
6. Observabilidad: logs estructurados y metricas de negocio.
7. Calidad: pruebas unitarias de dominio, integracion de endpoints y validacion de contrato API en CI.

Nota de alcance del curso:
- Esta propuesta se mantiene en un stack backend estandar de FastAPI y evita depender de herramientas avanzadas no necesarias para cumplir el hito.
- Componentes opcionales de optimizacion (por ejemplo cache dedicada) pueden incorporarse despues del MVP si hay evidencia de necesidad.

## 10. Riesgos y puntos de atencion
1. Riesgo de inconsistencia en reglas de puntos por pais:
- Posible falla: dos equipos aplican formulas distintas de acumulacion/canje.
- Mitigacion: especificacion unica versionada con ejemplos numericos oficiales.

2. Riesgo de identidad duplicada de clientes:
- Posible falla: cuentas paralelas por email/telefono y saldos fragmentados.
- Mitigacion: politica de unicidad y flujo controlado de merge.

3. Riesgo legal en consentimientos:
- Posible falla: no registrar version de terminos ni timestamp auditable.
- Mitigacion: ledger de consentimiento con version, fecha, canal y actor.

4. Riesgo de sobrecargar el MVP:
- Posible falla: intentar cubrir pedidos online y fidelizacion completa en un solo sprint.
- Mitigacion: recorte de alcance al nucleo (customers + locations + loyalty ledger).

## 11. Criterios de exito
- El equipo entiende donde implementar cada cambio sin ambiguedad.
- Las reglas de fidelizacion estan concentradas en el dominio loyalty y no en los controladores HTTP.
- Frontend y backend avanzan en paralelo con contrato estable.
- La arquitectura permite crecer a nuevas capacidades sin reescritura total.

## 12. Cierre
La propuesta prioriza claridad estructural, consistencia de negocio y velocidad de ejecucion para el hito backend. El patron seleccionado responde al contexto real de Brasaland y crea una base solida para iterar hacia escenarios mas complejos sin introducir complejidad operativa prematura.
