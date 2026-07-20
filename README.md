# Repositorio Serenamente — Guía de estructura

*Última actualización: 13 de julio de 2026.*

## Principio de organización

La ubicación física de un archivo facilita el trabajo, pero no modifica su Estado documental. Un documento solo cambia de Propuesto a Vigente cuando se completa el procedimiento de gobernanza correspondiente.

## Estructura vigente del repositorio

### `01_Oficial_Vigente`

Contiene los ocho documentos Serenamente registrados como Vigentes:

- SER-NM-01 — Núcleo Maestro Serenamente.
- SER-MM-01 — Manual del Método Serenamente.
- SER-PIC-01 — Protocolo de Investigación Científica.
- SER-BIB-V01 — Biblioteca Metodológica, volumen 1.
- SER-MAPA-01 — Mapa Maestro del Ecosistema.
- SER-GF-01 — Guion de Facilitación.
- SER-FAP-01 — Ficha de Apoyo al Participante.
- SER-POE-01 — Pauta de Observación Post-Experiencia.

### `02_Propuestos`

Contiene documentos con Estado documental Propuesto o En revisión. Las distintas versiones se conservan juntas para mantener trazabilidad:

- SER-DD-00 — Constitución del Lenguaje Oficial.
- SER-BRUJULA-01 — Brújula del Ecosistema.
- SER-MAPA-01 — Mapa Maestro del Ecosistema, versión 1.1 propuesta (la versión 1.0 vigente permanece en `01_Oficial_Vigente`).
- SER-IAOS-01 — Sistema Operativo para Inteligencias Artificiales, versiones 1.0 y 1.1 propuesta.
- SER-CLAUDE-01 — Protocolo Operacional de Claude, versiones 1.0 y 1.1 propuesta.
- SER-BITACORA-01 — Bitácora de Gobernanza.

### `03_IAOS_Madre`

Contiene el paquete fundacional del IAOS como sistema independiente y reutilizable para distintos proyectos. Incluye su propio `README.md` como índice interno.

### `04_IAOS_Aplicado_a_Serenamente`

Contiene fichas, mapas, arquitectura técnica, arquitectura de servicios y documentos operativos derivados de la aplicación del IAOS al proyecto Serenamente.

### `05_Auditoria_Arquitectonica`

Contiene el expediente de auditoría arquitectónica. Es material de análisis y trazabilidad; su ubicación no lo convierte en documento normativo del ecosistema.

### `recursos visuales`

Es la fuente visual principal para diseñar nuevas piezas de Serenamente. Cada encargo debe seleccionar las imágenes de referencia más pertinentes según su propósito, público y formato. La carpeta orienta la dirección estética; no impone una paleta, tipografía o composición fija para todas las piezas.

### `99_Obsoletos`

Conserva documentos retirados y antecedentes históricos. `SER-BCS-01` fue retirado como autoridad visual el 13 de julio de 2026 por confirmación explícita de la Fundadora. Sus reglas no deben aplicarse a piezas nuevas.

## Regla para mover documentos

Mover un documento a `01_Oficial_Vigente` requiere previamente:

1. Confirmación de contenido por la Fundadora del Método.
2. Validación de coherencia arquitectónica cuando corresponda.
3. Asignación de una Resolución dentro de SER-REF-01.
4. Actualización de SER-MAPA-01.

Hasta completar esos pasos, el documento permanece en `02_Propuestos`.

## Alcance de esta guía

Este archivo describe la organización física del repositorio. No reemplaza SER-MAPA-01, SER-IAOS-01, SER-CLAUDE-01 ni las tablas de Control documental incluidas en cada documento.
