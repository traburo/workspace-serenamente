# Sistema de Contenido Serenamente — MVP

## Estado

Diseño operativo inicial. No publica contenido ni modifica documentos SER vigentes.

## Objetivo del MVP

Ayudar a Serenamente a crecer una comunidad de mujeres adultas que viven sobrecarga mediante contenido profesional, útil, humano y coherente, siempre sujeto a revisión humana.

El MVP convierte un brief semanal en una campaña revisable. No intenta automatizar desde el primer día toda la producción audiovisual ni la publicación en Instagram.

## Resultado semanal esperado

- Un calendario de siete días.
- Un carrusel educativo.
- Un reel práctico con guion y lista de tomas.
- Una publicación humana o reflexiva.
- Tres secuencias de historias interactivas.
- Textos, CTA, dirección visual y métricas propuestas para cada pieza.

## Flujo principal

1. **Brief:** una persona define tema, objetivo, público, restricciones y activos disponibles.
2. **Plan:** el sistema distribuye las piezas entre Comprender, Respirar, Avanzar y Conectar.
3. **Generación:** crea textos, guiones, estructuras de carrusel e instrucciones visuales.
4. **Control:** revisa tono, veracidad, promesas, estado de las fuentes, privacidad, derechos y accesibilidad.
5. **Revisión humana:** una persona edita, devuelve o aprueba cada pieza.
6. **Producción:** se graba a Helen, se diseña la pieza o se usa una herramienta audiovisual opcional.
7. **Publicación:** inicialmente se realiza manualmente en Meta Business Suite.
8. **Aprendizaje:** se registran alcance, seguidores, guardados, compartidos, comentarios y respuestas.

## Estados de una pieza

`BORRADOR` → `EN_CONTROL` → `PARA_REVISION` → `CAMBIOS_SOLICITADOS` → `APROBADA` → `PUBLICADA` → `MEDIDA`

Solo una persona autorizada puede mover una pieza a `APROBADA`. En el MVP no existe publicación automática.

## Agentes funcionales

No es necesario desplegar varios modelos separados. En el MVP son etapas especializadas dentro de un mismo servicio:

1. **Planificador:** transforma el brief en calendario y objetivos por pieza.
2. **Redactor:** genera carruseles, captions, historias y guiones.
3. **Director visual:** propone formato, encuadres, ritmo y activos; no presupone una estética obligatoria.
4. **Control Serenamente:** detecta afirmaciones clínicas, promesas absolutas, datos no confirmados, problemas de privacidad y decisiones pendientes.
5. **Analista:** compara las métricas con el objetivo y recomienda un ajuste para la semana siguiente.

## Pantallas del MVP

### 1. Inicio

- Campaña semanal activa.
- Piezas por estado.
- Pendientes de revisión.
- Resultado de la semana anterior.

### 2. Nuevo brief

- Objetivo.
- Público.
- Tema semanal.
- Mensaje principal.
- CTA.
- Activos autorizados.
- Restricciones y datos pendientes.

### 3. Calendario

- Vista semanal.
- Formato, pilar y objetivo de cada publicación.
- Estado de cada pieza.

### 4. Editor y revisión

- Contenido publicable separado de las notas internas.
- Fuentes utilizadas.
- Alertas del control Serenamente.
- Historial de cambios.
- Acciones: solicitar cambios o aprobar.

### 5. Métricas

- Seguidores nuevos.
- Alcance.
- Guardados.
- Compartidos.
- Comentarios y respuestas.
- Aprendizaje propuesto.

## Modelo de datos mínimo

### `content_campaigns`

- `id`, `title`, `objective`, `audience`, `theme`
- `starts_on`, `ends_on`, `status`
- `created_at`, `updated_at`

### `content_pieces`

- `id`, `campaign_id`, `pillar`, `format`, `status`
- `scheduled_for`, `objective`, `cta`
- `caption`, `script`, `visual_direction`
- `sources`, `assumptions`, `approval_pending`
- `created_at`, `updated_at`

### `content_reviews`

- `id`, `piece_id`, `reviewer`, `decision`, `comment`, `created_at`

### `content_metrics`

- `id`, `piece_id`, `followers_gained`, `reach`
- `saves`, `shares`, `comments`, `replies`
- `recorded_at`, `learning`

## Arquitectura recomendada

Para reducir complejidad, el sistema se implementará como un módulo nuevo del proyecto Flask/PostgreSQL de `CONOCEME_MVP`:

- Blueprints Flask para campañas, piezas, revisión y métricas.
- Repositorios PostgreSQL siguiendo el patrón ya existente.
- Plantillas web simples para el tablero interno.
- Servicio de generación desacoplado del proveedor de IA.
- Registro de entradas, salidas y fuentes sin almacenar secretos.
- Pruebas de estados, permisos, validación y generación simulada.

El proveedor de IA se conectará mediante una interfaz interna. Así se podrá comenzar con un proveedor y cambiarlo después sin rehacer el sistema.

## Integraciones por etapa

### MVP

- Modelo de IA para textos y guiones: pendiente de selección.
- Imágenes: generación asistida dentro del flujo de trabajo, cuando sea necesaria.
- Video: grabación humana; Higgsfield permanece opcional para planos de apoyo.
- Publicación: manual mediante Meta Business Suite.
- Métricas: carga manual semanal.

### Etapa posterior

- Higgsfield u otro estudio audiovisual mediante un adaptador.
- Envío de piezas aprobadas a Postiz o Meta mediante API.
- Importación automática de métricas.

## Referencias arquitectónicas evaluadas

- `microsoft/content-generation-solution-accelerator`: se adopta la separación entre brief, planificación, generación y control de marca. No se adopta su infraestructura Azure en el MVP.
- `gitroomhq/postiz-app`: se adoptan las ideas de calendario, estados, colaboración, programación y medición. No se incorpora su monorepo completo ni código AGPL dentro del proyecto.
- `Anil-matcha/Free-AI-Social-Media-Scheduler`: se estudió como alternativa simple, pero Instagram aún no está implementado según su documentación actual.

## Reglas obligatorias

- Los documentos SER vigentes prevalecen sobre documentos operativos.
- No presentar Serenamente como psicoterapia, tratamiento o diagnóstico.
- No inventar testimonios, evidencia, aprobaciones, precios, fechas ni resultados.
- No utilizar imágenes o datos personales sin autorización.
- No declarar una pieza lista para publicar sin revisión humana.
- La dirección creativa puede comenzar desde cero. `recursos visuales/` es una biblioteca opcional, de acuerdo con la decisión de gobernanza del 16 de julio de 2026.

## Criterios para considerar terminado el MVP

- Crear una campaña desde un brief.
- Generar un calendario semanal y sus piezas.
- Mostrar fuentes, supuestos, pendientes y alertas.
- Editar una pieza y conservar su historial.
- Impedir aprobación cuando existan errores críticos.
- Aprobar una pieza mediante una acción humana identificada.
- Registrar métricas y producir un aprendizaje semanal.
- Mantener pruebas automatizadas para permisos y transiciones de estado.

## Construcción incremental

1. **Tablero sin IA:** campañas, piezas, estados, revisión y métricas.
2. **Generación asistida:** calendario, textos y guiones desde el brief.
3. **Control Serenamente:** reglas automáticas y trazabilidad de fuentes.
4. **Producción e integración:** imágenes, video y envío opcional a una plataforma de publicación.

## Decisiones pendientes

- Proveedor inicial del modelo de IA.
- Persona o personas autorizadas para aprobar.
- Presupuesto mensual máximo para generación.
- Uso de infraestructura actual de Railway o un servicio separado.
- Momento en que se conectará una cuenta real de Instagram.

## Estado de implementación

- [x] Tablero de campañas y piezas.
- [x] Estados, revisión humana, historial y bloqueo de aprobación.
- [x] Generación inicial de seis borradores desde el brief semanal.
- [ ] Sustituir el generador inicial por un proveedor de IA seleccionado.
- [ ] Registro de métricas desde la interfaz.
- [ ] Producción audiovisual e integración de publicación.
- [x] Adaptador inicial para generar imágenes con Nano Banana desde una pieza.

El generador inicial es determinista: utiliza el tema y el público del brief para crear una campaña base segura. Está separado del resto del sistema para poder reemplazarlo por un modelo de IA sin modificar las rutas, la base de datos ni el flujo de aprobación.

La integración de imágenes utiliza `GEMINI_API_KEY` y, por defecto, `gemini-3.1-flash-lite-image`. El sistema compone un prompt editable, solicita una sola imagen vertical 4:5 y la guarda como activo pendiente de revisión. La clave nunca debe escribirse en el repositorio.

## Aplicación de migraciones PostgreSQL

Desde `CONOCEME_MVP`, con `DATABASE_URL` configurada, ejecutar:

`python -m app.commands.migrate`

El comando revisa los archivos numerados de `migrations/`, aplica únicamente los que no están registrados en `schema_migrations` y conserva el orden. Para este sistema, `003_content_system.sql` crea las tablas de campañas, piezas, revisiones y métricas. No elimina inscripciones ni reemplaza las tablas anteriores.
