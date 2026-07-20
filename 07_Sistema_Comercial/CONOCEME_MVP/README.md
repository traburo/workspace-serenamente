# CONÓCEME MVP — sistema comercial Serenamente

Estado: entorno técnico de prueba desplegado en Railway. El evento permanece sin
habilitación comercial y su marca requiere validación humana antes de una
publicación real.

## Alcance implementado

- Aplicación Flask compatible con `gunicorn main:app`.
- Landing adaptable a teléfonos y formulario con minimización de datos.
- CSRF, honeypot, validación en servidor, normalización y encabezados de seguridad.
- Persistencia PostgreSQL mediante SQL parametrizado y registro idempotente por evento + email.
- Consentimiento operativo obligatorio y marketing opcional, almacenados por separado.
- Cola inicial de email y capa Resend simulable.
- Migración inicial con el evento cargado como borrador.
- Pruebas de registro, validación, duplicados, consentimientos, email simulado y secretos.
- Panel protegido por usuario y hash de contraseña.
- Filtros, detalle, transiciones de estado y trazabilidad administrativa.
- Control transaccional de un máximo de 20 duplas confirmadas.
- Exportación CSV limitada a datos operativos.
- Recordatorios de 24 y 2 horas, cola con bloqueo y reintentos limitados.
- Agradecimiento una hora después y seguimiento para asistentes a las 48 horas.
- Mensaje para no asistentes implementado pero desactivado hasta aprobación.
- Comando independiente e idempotente para Railway cron.

## Ejecución local

1. Crear un entorno virtual de Python 3.12 o superior.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Crear una base PostgreSQL y copiar `.env.example` a `.env`.
4. Aplicar, en orden, `migrations/001_initial.sql` y `migrations/002_operations.sql` con `psql`.
5. Mantener el evento en borrador hasta la validación humana. Para una prueba local controlada, cambiarlo manualmente a `published` y `validated` en la base de prueba.
6. Generar el hash de la contraseña administrativa con Werkzeug y guardarlo en `ADMIN_PASSWORD_HASH`. No guardar la contraseña en el repositorio.
7. Cargar las variables de entorno y ejecutar `flask --app main run`.

El panel queda disponible en `/admin/login`. La página pública usa los datos confirmados: 1 de octubre de 2026, 12:00 a 15:00, Sede Pedro Fontova, $30.000 por dupla y máximo 20 duplas.

## Mensajes y recordatorios

Para una prueba sin correos reales, configurar `EMAIL_SIMULATION=1` y ejecutar:

`python -m app.commands.process_messages`

El comando crea una sola intención por inscripción, evento y tipo de mensaje; reclama filas con bloqueo, registra intentos y evita duplicados al repetirse. En producción se ejecutará como tarea programada independiente, no como hilo dentro de Flask.

## Pruebas

Ejecutar `pytest -q`. Las pruebas usan un repositorio en memoria: no requieren una base real ni envían correos.

La prueba integral PostgreSQL se activa con `TEST_DATABASE_URL`. En este equipo se verificó con `postgresql://postgres@127.0.0.1:55432/serenamente_test`: inscripción, panel, pago, CSV, recordatorios, asistencia, agradecimiento, seguimiento, idempotencia, auditoría y cambio final de estado.

## PostgreSQL local de prueba

PostgreSQL 17 está extraído dentro de `.local/`, fuera del control de versiones, y escucha solo en `127.0.0.1:55432`.

- Iniciar: `powershell -ExecutionPolicy Bypass -File scripts/start_local_database.ps1`
- Detener: `powershell -ExecutionPolicy Bypass -File scripts/stop_local_database.ps1`
- Base: `serenamente_test`

Se comprobó además un ciclo completo de respaldo y restauración con `pg_dump` y `pg_restore`. Esta configuración con autenticación local de confianza es solo para desarrollo y nunca debe copiarse a Railway.

## Guías operativas

- `MANUAL_OPERATIVO.md`: instrucciones para una persona no técnica.
- `CORREOS_PARA_APROBACION.md`: textos completos sujetos a revisión humana.

## Railway (entorno de prueba activo)

El proyecto privado `Serenamente CONOCEME Pruebas` está configurado con:

- `conoceme-web`: aplicación Flask, panel interno y dominio temporal de Railway.
- `Postgres`: base persistente con migraciones automáticas previas al despliegue.
- `conoceme-recordatorios`: proceso independiente ejecutado cada hora mediante `railway.cron.json`.

La página de prueba está disponible en
`https://diligent-surprise-production-6eb0.up.railway.app/` y mantiene
`STAGING_MODE=1`. El programador conserva `EMAIL_SIMULATION=1` y
`ENABLE_NO_SHOW_FOLLOWUP=0`, por lo que procesa la lógica sin enviar mensajes
reales. El 16 de julio de 2026 se verificó una ejecución manual con tres mensajes
simulados y cero fallos.

Resend tiene una clave exclusiva de envío. Se comprobó un único correo técnico
entregado a la dirección autorizada de la cuenta. No se debe activar el envío
general hasta revisar los mensajes pendientes, verificar un dominio remitente y
obtener aprobación humana explícita. `awmc18@gmail.com` continúa siendo el buzón
para comprobantes, no un remitente validado de Resend.

## Decisiones humanas pendientes

- Validar publicación, imagen/marca y política provisional de devolución.
- Aprobar texto de privacidad y consentimientos con revisión jurídica local.
- Definir instrucciones, plazo, devoluciones y responsable de verificación del pago.
- Completar el número de cuenta y aprobar los textos finales de correo, especialmente el seguimiento de no asistentes.
- Confirmar responsables, cuentas propietarias, dominio y política de respaldo/retención.
- Cambiar la contraseña administrativa provisional antes de abrir inscripciones reales.

## Dirección visual aplicada

Se usó `recursos visuales/IMG-20260706-WA0050.jpg` como referencia de calidez editorial y `CONOCEME_Propuesta_03` como antecedente de jerarquía informativa. No se reutilizaron fotografías, QR ni composiciones. Los acentos turquesa y rosa dialogan con el logotipo confirmado para el encargo, sin declararlos sistema visual oficial. La validación final de marca sigue pendiente.
