# SER-IAOS-ATM-01 - Arquitectura Técnica Mínima Serenamente

Estado: Propuesta técnica operativa IAOS aplicada  
Fecha: 2026-07-10  
Responsable operativo: Alex  
Proyecto: Serenamente  
Condición: Diseño técnico mínimo; no representa software implementado ni decisiones comerciales aprobadas  
Fuentes directas: SER-IAOS-TRANSFER-01, SER-IAOS-SCO-01, SER-IAOS-OMI-01  
Oferta de prueba: `Volver a mí: pausa, respiración y claridad para sostenerte mejor`, pendiente de validación de Helen

## 1. Propósito

Definir la arquitectura técnica mínima para probar el flujo comercial operativo de una experiencia Serenamente sin construir prematuramente una plataforma completa.

El sistema debe permitir:

`Atención -> Interés -> Registro -> Pago o reserva -> Confirmación -> Recordatorio -> Asistencia -> Seguimiento -> Continuidad`

La arquitectura debe conservar trazabilidad, reducir trabajo manual y producir datos suficientes para que IAOS evalúe el flujo. No congela la identidad, el nombre de la oferta, el modelo de pago ni decisiones que requieren validación humana.

## 2. Alcance del MVP

### 2.1 Incluido

- Una landing o página pública para una experiencia activa.
- Catálogo técnico mínimo de eventos, aunque el MVP publique inicialmente uno.
- Formulario propio de registro.
- Persistencia en base de datos PostgreSQL.
- Prevención de duplicados por evento y email.
- Reserva gratuita, transferencia o derivación a un link de pago externo.
- Confirmación de registro y de cupo mediante email transaccional.
- Recordatorios programados por email.
- Registro manual de pago, reserva y asistencia.
- Seguimiento posterior por email.
- Panel interno básico protegido.
- Exportación CSV.
- Registro de fuente de llegada y métricas operativas mínimas.
- Historial básico de envíos y cambios críticos de estado.

### 2.2 Fuera de alcance inicial

- Pasarela propia o manejo de datos de tarjetas.
- Integración automática con Flow, Mercado Pago o Transbank.
- Automatización por WhatsApp API.
- CRM general de Serenamente.
- Gestión completa de programas, membresías o venta institucional.
- Facturación, contabilidad o conciliación bancaria automática.
- Sistema clínico, ficha terapéutica o datos sensibles de salud.
- Portal de participantes, cuentas de usuario o recuperación de contraseña pública.
- Orquestación de subagentes.
- Analítica avanzada, personalización o campañas masivas.

## 3. Principios técnicos

1. Construir para validar un flujo, no una plataforma completa.
2. Mantener el pago desacoplado: Serenamente no almacena datos financieros sensibles.
3. Automatizar mensajes repetibles y mantener manuales las decisiones que requieren revisión.
4. No confirmar un cupo pagado hasta verificar el pago cuando el método sea transferencia.
5. Minimizar datos personales y separar consentimiento operativo de consentimiento comercial.
6. Hacer idempotentes el registro, los webhooks futuros y los envíos programados.
7. Mantener estados explícitos; no inferir pago, asistencia o consentimiento.
8. Registrar fechas en UTC y mostrar horario local de Chile según el evento.

## 4. Flujo funcional completo

### 4.1 Captación y visita

1. La persona llega desde Instagram, QR, referido, WhatsApp, anuncio o enlace directo.
2. La URL conserva parámetros `utm_source`, `utm_medium`, `utm_campaign` y `ref` cuando existan.
3. La landing consulta el evento publicado y muestra nombre, descripción, modalidad, fecha, hora, duración, cupos, condición de pago/reserva y una llamada a la acción.

### 4.2 Registro

4. La persona completa el formulario y acepta el contacto estrictamente necesario para gestionar su inscripción.
5. El sistema valida campos, cupos y duplicidad.
6. Se crea o actualiza la persona y se crea un registro asociado al evento.
7. El registro entra en uno de estos estados:
   - `pending_reservation`, si requiere revisión o confirmación manual;
   - `pending_payment`, si requiere transferencia o pago externo;
   - `confirmed`, si la reserva gratuita se confirma automáticamente y hay cupo.
8. El sistema devuelve una página de resultado sin exponer identificadores internos predecibles.

### 4.3 Pago o reserva

9. Para transferencia, la persona recibe instrucciones y un código de referencia.
10. Para link externo, el sistema registra la derivación; el resultado puede confirmarse manualmente en el MVP.
11. Alex o Helen verifican la reserva o el pago en el panel y actualizan su estado.
12. La confirmación de cupo ocurre solo después de cumplir la regla configurada para el evento.

### 4.4 Comunicación previa

13. El sistema encola el email apropiado: registro recibido, instrucciones de pago o cupo confirmado.
14. Una tarea programada selecciona registros confirmados y encola recordatorios 24 horas y 2 horas antes.
15. Cada tipo de email se envía una sola vez por registro y evento, salvo reenvío manual explícito.

### 4.5 Ejecución y continuidad

16. El equipo marca asistencia o ausencia desde el panel.
17. Después del evento, el sistema envía agradecimiento y práctica a quienes asistieron.
18. A quienes no asistieron se les puede enviar un mensaje distinto, pendiente de validación de contenido.
19. El panel presenta registros, confirmaciones, pagos, asistencia, fuentes y continuidad declarada.
20. IAOS puede trabajar posteriormente con datos agregados o exportados, no con exposición innecesaria de datos personales.

## 5. Stack recomendado inicial

### 5.1 Opción recomendada: aplicación web semi-automatizada

- Aplicación web y API: una sola aplicación full-stack en TypeScript.
- Framework sugerido: Next.js estable al momento de implementar, con rutas públicas, acciones/API y panel interno en el mismo proyecto.
- Base de datos: PostgreSQL administrado.
- ORM y migraciones: Prisma o equivalente, a confirmar durante implementación.
- Hosting inicial: Railway para aplicación y PostgreSQL, sujeto a revisión de costos y operación.
- Email transaccional: Resend.
- Tareas programadas: cron de Railway o programador equivalente que invoque un endpoint interno protegido.
- Archivos: no almacenar comprobantes en el MVP; registrar referencia y nota de verificación. Si luego son necesarios, usar almacenamiento privado con URLs firmadas y política de eliminación.
- Analítica: métricas propias derivadas de la base; analítica web externa es opcional y debe respetar la política de privacidad.

### 5.2 Razón del diseño

Una sola aplicación reduce despliegues, autenticación duplicada y coordinación entre frontend y backend. PostgreSQL conserva integridad y trazabilidad. Resend separa la entrega de correo. El pago externo evita complejidad y riesgo antes de validar demanda.

### 5.3 Alternativas permitidas

- Supabase puede reemplazar PostgreSQL/administración si se decide usar su autenticación y panel.
- Un proveedor distinto de hosting puede reemplazar Railway.
- Una vista segura de base de datos puede servir temporalmente como panel, pero no debe exponer credenciales ni datos al público.

Estas alternativas son decisiones de implementación; no cambian el modelo funcional.

## 6. Modelo de datos

### 6.1 `events`

Representa una edición concreta de una experiencia.

Campos mínimos:

- `id`: UUID.
- `slug`: texto único para URL pública.
- `name`: texto.
- `short_description`: texto.
- `status`: `draft | published | closed | completed | cancelled`.
- `validation_status`: `pending_human_validation | validated`.
- `modality`: `online | in_person | hybrid | pending`.
- `starts_at`: fecha/hora nullable mientras sea borrador.
- `ends_at`: fecha/hora nullable.
- `timezone`: texto, por defecto sugerido `America/Santiago`.
- `location_name`: texto nullable.
- `location_details`: texto nullable; visible solo a confirmados si corresponde.
- `meeting_url`: texto nullable; visible solo a confirmados.
- `capacity`: entero nullable.
- `access_type`: `free_reservation | bank_transfer | external_payment_link | pending`.
- `price_amount`: entero nullable, en la unidad menor de moneda.
- `currency`: texto nullable, sugerido `CLP`.
- `external_payment_url`: URL nullable.
- `registration_opens_at`: fecha/hora nullable.
- `registration_closes_at`: fecha/hora nullable.
- `contact_email`: texto nullable.
- `contact_phone`: texto nullable.
- `created_at`, `updated_at`: fecha/hora.

Regla: un evento no puede pasar a `published` si mantiene fecha, modalidad, cupos o acceso obligatorios sin definir, o si `validation_status` no es `validated`.

### 6.2 `people`

Representa datos de contacto mínimos de una persona.

Campos mínimos:

- `id`: UUID.
- `full_name`: texto.
- `email`: texto normalizado.
- `whatsapp`: texto nullable en formato normalizado.
- `city_or_commune`: texto nullable.
- `created_at`, `updated_at`: fecha/hora.

No incluir diagnósticos, antecedentes clínicos ni categorías sensibles en este MVP.

### 6.3 `registrations`

Relaciona una persona con un evento y conserva el estado del flujo.

Campos mínimos:

- `id`: UUID.
- `public_reference`: texto único no secuencial.
- `event_id`: UUID, clave foránea.
- `person_id`: UUID, clave foránea.
- `status`: estado operativo del registro.
- `attendance_mode`: `online | in_person | pending`, si aplica.
- `source`: texto controlado, por ejemplo `instagram`, `qr`, `referral`, `whatsapp`, `direct`, `institutional`, `other`.
- `utm_source`, `utm_medium`, `utm_campaign`, `referrer`: texto nullable.
- `motivation`: texto corto nullable; evitar relato clínico abierto.
- `follow_up_interest`: texto nullable.
- `operational_consent`: booleano.
- `operational_consent_at`: fecha/hora.
- `marketing_consent`: booleano independiente.
- `marketing_consent_at`: fecha/hora nullable.
- `internal_notes`: texto nullable, solo panel.
- `registered_at`, `confirmed_at`, `cancelled_at`: fecha/hora nullable.
- `created_at`, `updated_at`: fecha/hora.

Restricción: combinación única `event_id + person_id`. Un reintento devuelve el registro existente de forma segura en vez de duplicarlo.

### 6.4 `payments`

Registra la situación de pago o reserva sin almacenar datos de tarjeta.

Campos mínimos:

- `id`: UUID.
- `registration_id`: UUID, clave foránea.
- `method`: `not_required | bank_transfer | external_link | cash | other`.
- `status`: `not_required | pending | reported | verified | rejected | refunded | waived`.
- `amount`: entero nullable.
- `currency`: texto nullable.
- `external_reference`: texto nullable.
- `reported_at`, `verified_at`, `refunded_at`: fecha/hora nullable.
- `verified_by`: identificador de administrador nullable.
- `internal_note`: texto nullable.
- `created_at`, `updated_at`: fecha/hora.

En el MVP, la confirmación de transferencia es una acción humana auditada.

### 6.5 `attendance`

Campos mínimos:

- `id`: UUID.
- `registration_id`: UUID único.
- `status`: `pending | attended | absent | excused`.
- `checked_in_at`: fecha/hora nullable.
- `marked_by`: identificador de administrador nullable.
- `note`: texto nullable.
- `updated_at`: fecha/hora.

### 6.6 `email_messages`

Registra intención, envío y resultado de cada email transaccional.

Campos mínimos:

- `id`: UUID.
- `registration_id`: UUID.
- `event_id`: UUID.
- `type`: tipo de mensaje.
- `recipient_email`: texto.
- `scheduled_for`: fecha/hora.
- `status`: `queued | sending | sent | delivered | failed | cancelled`.
- `provider_message_id`: texto nullable.
- `attempt_count`: entero.
- `last_error`: texto acotado nullable, sin secretos.
- `sent_at`, `delivered_at`: fecha/hora nullable.
- `created_at`, `updated_at`: fecha/hora.

Restricción recomendada: índice único `registration_id + type + event_id` para envíos automáticos ordinarios.

### 6.7 `admin_audit_log`

Campos mínimos:

- `id`: UUID.
- `actor_id`: identificador del administrador.
- `action`: texto controlado.
- `entity_type`: texto.
- `entity_id`: UUID.
- `before_state`: JSON nullable.
- `after_state`: JSON nullable.
- `created_at`: fecha/hora.

Debe cubrir como mínimo verificación/rechazo de pagos, cambio de cupo confirmado, cancelación y asistencia.

## 7. Estados del registro

Estados propuestos:

- `started`: opcional; formulario iniciado, no necesario en la primera implementación.
- `pending_reservation`: registro recibido y pendiente de revisión/reserva.
- `pending_payment`: requiere pago o verificación.
- `payment_reported`: la persona informó pago; pendiente de verificación humana.
- `confirmed`: cupo confirmado.
- `waitlisted`: sin cupo disponible; no recibe link de acceso ni recordatorio de asistencia.
- `cancelled`: cancelado por la persona o administración.
- `attended`: asistió.
- `no_show`: estaba confirmado y no asistió.
- `completed_follow_up`: se ejecutó el seguimiento aplicable.

Transiciones permitidas principales:

- `pending_reservation -> confirmed | waitlisted | cancelled`
- `pending_payment -> payment_reported | cancelled`
- `payment_reported -> confirmed | pending_payment | cancelled`
- `confirmed -> attended | no_show | cancelled`
- `attended -> completed_follow_up`
- `no_show -> completed_follow_up`, solo si se aprueba un seguimiento específico

Las transiciones deben validarse en servidor. No se debe usar un único campo de estado para reemplazar los estados detallados de pago, asistencia y email; el estado de registro funciona como resumen operativo.

## 8. Emails transaccionales

### 8.1 Tipos mínimos

1. `registration_received`: confirma recepción; no afirma cupo ni pago cuando están pendientes.
2. `payment_instructions`: instrucciones de transferencia o botón hacia pago externo.
3. `registration_confirmed`: confirma el cupo e incluye logística.
4. `reminder_24h`: recordatorio 24 horas antes.
5. `reminder_2h`: recordatorio 2 horas antes.
6. `event_changed`: envío manual/dirigido ante cambio relevante.
7. `event_cancelled`: aviso de cancelación.
8. `post_event_attendee`: agradecimiento y práctica para asistentes.
9. `post_event_no_show`: opcional, pendiente de validación humana.

### 8.2 Reglas de contenido

- Usar el nombre validado del evento y datos vigentes de fecha, hora y modalidad.
- No incluir afirmaciones clínicas ni promesas de resultados.
- Diferenciar “registro recibido” de “cupo confirmado”.
- No enviar el link privado de reunión a registros no confirmados.
- Incluir contacto y mecanismo simple para informar problemas o cancelación.
- El seguimiento comercial futuro solo se envía con consentimiento de marketing; los mensajes necesarios para ejecutar el evento se amparan en el consentimiento operativo informado.

### 8.3 Entrega y fallos

- Guardar el identificador devuelto por Resend.
- Recibir webhooks de entrega o fallo cuando se habiliten.
- Reintentar errores temporales con límite; no reintentar indefinidamente direcciones rechazadas.
- Mostrar fallos en el panel para contacto manual.

## 9. Recordatorios

- Un job programado corre al menos cada 15 minutos.
- Selecciona eventos activos y registros `confirmed` cuyo recordatorio corresponda.
- Crea el registro `email_messages` antes de enviar para impedir duplicados.
- Ventana sugerida para `reminder_24h`: entre 23 y 25 horas antes.
- Ventana sugerida para `reminder_2h`: entre 1,5 y 2,5 horas antes.
- Si el registro se cancela, los mensajes futuros pasan a `cancelled`.
- Si cambia la fecha, deben cancelarse recordatorios previos y recalcularse; el cambio relevante requiere además aviso explícito.
- Un administrador puede previsualizar, cancelar o reenviar, dejando trazabilidad.

## 10. Panel interno mínimo

### 10.1 Acceso

- Solo Alex, Helen u operadores explícitamente autorizados.
- Autenticación mediante proveedor seguro o credenciales con sesión protegida; no crear autenticación artesanal si puede evitarse.
- Roles iniciales: `admin` y `operator`. La autorización exacta puede simplificarse a `admin` en el primer despliegue si solo existen uno o dos usuarios.

### 10.2 Vistas

- Resumen de eventos: estado, fecha, cupos, registros, confirmados y asistencia.
- Lista filtrable de inscritos por estado, pago, asistencia y fuente.
- Ficha de registro con contacto, consentimientos, historial y notas.
- Cola de pagos reportados para verificar o rechazar.
- Lista de check-in para marcar asistencia.
- Estado de emails y fallos.
- Exportación CSV por evento.

### 10.3 Acciones

- Crear/editar evento en borrador.
- Publicar/cerrar evento, sujeto a validaciones.
- Confirmar reserva.
- Marcar pago reportado, verificado, rechazado o exento.
- Mover a lista de espera o confirmar cupo.
- Cancelar registro.
- Marcar asistencia/ausencia.
- Reenviar un email específico.
- Agregar nota interna.

No se permite cambiar consentimientos en nombre de la persona sin registrar fuente, motivo y actor.

## 11. Integración de pago o reserva

### 11.1 Reserva gratuita

- Si hay cupo y el evento lo permite, confirmar automáticamente.
- Si se alcanza el cupo, crear `waitlisted`.
- La capacidad debe comprobarse en una transacción para evitar sobreventa por registros simultáneos.

### 11.2 Transferencia

- Crear registro `pending_payment` y pago `pending`.
- Mostrar instrucciones definidas por el equipo y una referencia única.
- Permitir que el equipo marque `payment_reported` si recibe comprobante por el canal acordado.
- Un administrador verifica y cambia pago a `verified`; recién entonces confirma el cupo.
- No almacenar imágenes de comprobantes en esta versión, salvo decisión explícita y diseño de almacenamiento privado.

### 11.3 Link de pago externo

- Redirigir a una URL configurada por evento.
- Registrar la intención de salida, pero no asumir pago por el clic.
- Confirmar manualmente en el MVP.
- Una integración posterior puede usar webhook firmado y clave de idempotencia.

### 11.4 Reglas aún no definidas

- Plazo para pagar antes de liberar cupo.
- Política de devolución, cambio y cancelación.
- Tratamiento de pagos parciales o pagos sin referencia.
- Responsable de conciliación.

## 12. Endpoints o acciones necesarias

Los nombres son referenciales; pueden implementarse como rutas HTTP o acciones de servidor equivalentes.

### 12.1 Públicas

- `GET /api/events/{slug}`: obtener evento publicado y disponibilidad.
- `POST /api/events/{slug}/registrations`: validar y crear/reutilizar registro.
- `GET /registro/{public_reference}`: mostrar resultado seguro sin exponer información adicional.
- `POST /api/registrations/{public_reference}/cancel`: solicitar cancelación mediante token seguro o flujo verificado.

### 12.2 Administrativas

- `GET /api/admin/events`
- `POST /api/admin/events`
- `PATCH /api/admin/events/{id}`
- `GET /api/admin/events/{id}/registrations`
- `PATCH /api/admin/registrations/{id}/status`
- `POST /api/admin/registrations/{id}/verify-payment`
- `POST /api/admin/registrations/{id}/reject-payment`
- `POST /api/admin/registrations/{id}/attendance`
- `POST /api/admin/registrations/{id}/resend-email`
- `GET /api/admin/events/{id}/export.csv`

### 12.3 Internas

- `POST /api/internal/jobs/reminders`: calcula y encola recordatorios; protegido por secreto y restricción de método.
- `POST /api/internal/jobs/follow-up`: encola seguimiento posterior.
- `POST /api/webhooks/resend`: actualiza estado de entrega verificando firma.
- Endpoint de webhook de pago: no implementar hasta elegir proveedor.

Todas las mutaciones requieren validación en servidor, control de autorización, rate limiting donde corresponda y respuestas que no revelen si un email existe en otros eventos.

## 13. Variables de entorno

Variables mínimas sugeridas:

```text
APP_BASE_URL=
NODE_ENV=
DATABASE_URL=
SESSION_SECRET=
ADMIN_ALLOWED_EMAILS=
RESEND_API_KEY=
RESEND_FROM_EMAIL=
RESEND_FROM_NAME=
RESEND_WEBHOOK_SECRET=
INTERNAL_CRON_SECRET=
DEFAULT_TIMEZONE=America/Santiago
CONTACT_EMAIL=
CONTACT_WHATSAPP=
```

Según autenticación elegida:

```text
AUTH_SECRET=
AUTH_PROVIDER_CLIENT_ID=
AUTH_PROVIDER_CLIENT_SECRET=
```

Según modalidad de pago:

```text
BANK_TRANSFER_INSTRUCTIONS=
DEFAULT_EXTERNAL_PAYMENT_URL=
```

Reglas:

- No guardar secretos en el repositorio, logs, frontend ni documentación pública.
- Separar valores de desarrollo, prueba y producción.
- Rotar claves ante exposición.
- El remitente de Resend requiere dominio verificado antes de producción.

## 14. Seguridad, privacidad y operación

- Usar HTTPS en producción.
- Validar, normalizar y limitar longitud de todas las entradas.
- Aplicar protección anti-spam: campo trampa, rate limit y, si es necesario, captcha respetuoso con privacidad.
- Cifrar conexiones a base de datos y restringir acceso por credenciales.
- Hacer backups automáticos y probar restauración antes de depender del sistema.
- Minimizar logs con datos personales; ocultar tokens, secretos y contenido sensible.
- Definir plazo de retención y procedimiento de eliminación/corrección de datos.
- Exportar solo lo necesario y proteger los CSV descargados.
- Informar finalidad del registro, comunicaciones operativas y opción separada de novedades futuras.
- No pedir información clínica en el formulario.
- Mantener una forma manual de continuidad si falla email o aplicación.

## 15. Métricas mínimas

Por evento:

- Visitas o clics medibles, si se habilita analítica.
- Formularios completados.
- Registros únicos.
- Registros pendientes, confirmados y en espera.
- Pagos reportados y verificados.
- Asistentes y ausentes.
- Tasa registro -> confirmación.
- Tasa confirmación -> asistencia.
- Emails enviados, entregados y fallidos.
- Fuente de llegada.
- Interés declarado en continuidad.

Las métricas deben presentarse agregadas cuando no sea necesario identificar personas.

## 16. Riesgos técnicos y mitigaciones

### 16.1 Sobreconstrucción

Riesgo: retrasar la validación por construir pasarela, CRM o automatizaciones avanzadas.  
Mitigación: mantener el alcance semi-automatizado y una sola experiencia activa.

### 16.2 Sobreventa o doble confirmación

Riesgo: confirmar más personas que cupos.  
Mitigación: transacción de base de datos, conteo de confirmados y restricción de estados.

### 16.3 Correos duplicados o tardíos

Riesgo: mala experiencia y confusión.  
Mitigación: claves únicas por tipo de email, jobs idempotentes, zona horaria explícita y panel de fallos.

### 16.4 Pago atribuido incorrectamente

Riesgo: confirmar a quien no pagó o no reconocer un pago.  
Mitigación: referencia pública única, verificación humana y auditoría.

### 16.5 Exposición de datos

Riesgo: accesos indebidos, CSV perdidos o secretos en logs.  
Mitigación: acceso restringido, mínimo dato, sesiones seguras, secretos de entorno y política de exportación.

### 16.6 Dependencia de proveedores

Riesgo: caída o cambio de Railway, Resend o proveedor de pago.  
Mitigación: PostgreSQL portable, capa de email desacoplada, exportación y procedimiento manual alternativo.

### 16.7 Datos del evento incompletos

Riesgo: enviar mensajes con fecha, lugar o precio pendientes.  
Mitigación: impedir publicación y programación mientras falten campos obligatorios o validación humana.

### 16.8 Baja entregabilidad

Riesgo: confirmaciones en spam o rebote.  
Mitigación: dominio autenticado, remitente válido, contenido transaccional claro y monitoreo de fallos.

### 16.9 Confusión entre contacto operativo y marketing

Riesgo: uso de datos fuera de la finalidad informada.  
Mitigación: consentimientos separados y reglas de envío según propósito.

## 17. Decisiones humanas pendientes

Estas decisiones bloquean publicación o producción completa, pero no el diseño técnico:

- Validación de Helen del nombre, tono, estructura y promesa de `Volver a mí`.
- Modalidad: presencial, online o híbrida.
- Fecha, hora, lugar/link y cupos.
- Acceso gratuito, transferencia o link de pago.
- Precio y moneda si corresponde.
- Política de reserva, vencimiento, cancelación, cambios y devolución.
- Email y nombre oficial del remitente.
- Dominio y página actual a integrar o reemplazar.
- Canal principal de contacto y número de WhatsApp.
- Responsable de verificar pagos, gestionar inscritos y marcar asistencia.
- Datos opcionales que realmente se pedirán en el formulario.
- Texto de privacidad y retención de datos.
- Mensaje para no asistentes y oferta de continuidad.
- Proveedor de autenticación del panel.
- Presupuesto y cuenta propietaria de Railway, Resend y dominio.

Hasta resolverlas, se deben usar datos ficticios de prueba y mantener el evento en `draft` con `pending_human_validation`.

## 18. Orden de implementación

### Fase 0 - Cierre de decisiones mínimas

1. Validar la oferta con Helen o registrar ajustes.
2. Definir modalidad, fecha, cupos y regla de acceso.
3. Definir remitente, dominio, contacto y responsables operativos.
4. Aprobar texto de consentimiento y privacidad mínimo.

### Fase 1 - Base técnica

5. Crear repositorio/aplicación y ambientes.
6. Provisionar PostgreSQL y configurar migraciones.
7. Implementar entidades `events`, `people`, `registrations` y `payments`.
8. Cargar el evento como borrador.

### Fase 2 - Conversión

9. Construir landing y formulario.
10. Implementar validación, deduplicación, cupos y página de resultado.
11. Probar reserva gratuita y, según decisión, transferencia o link externo.

### Fase 3 - Comunicación

12. Verificar dominio de envío en Resend.
13. Implementar plantillas y cola de emails.
14. Implementar confirmación y fallos visibles.
15. Implementar cron idempotente de recordatorios.

### Fase 4 - Operación interna

16. Implementar acceso administrativo.
17. Construir listado, filtros, verificación de pago y check-in.
18. Agregar exportación CSV y auditoría mínima.

### Fase 5 - Seguimiento y medición

19. Implementar seguimiento según asistencia.
20. Agregar tablero de métricas agregadas.
21. Ejecutar prueba interna completa con emails de prueba y reloj controlado.
22. Ejecutar una prueba piloto sin anuncios pagados.
23. Documentar incidentes y aprendizaje antes de ampliar alcance.

## 19. Criterios de aceptación del MVP

El MVP está listo para una prueba real solo si:

- Un evento validado puede publicarse sin campos críticos pendientes.
- Una persona puede registrarse una sola vez por evento.
- El cupo no puede sobrepasarse bajo registros simultáneos.
- El estado correcto se asigna según reserva o pago.
- El sistema diferencia recepción de registro y confirmación de cupo.
- Los emails de confirmación, 24 horas, 2 horas y seguimiento se prueban sin duplicados.
- El equipo puede verificar pagos y marcar asistencia con trazabilidad.
- La cancelación impide recordatorios posteriores.
- Los fallos de email son visibles.
- Los datos pueden exportarse y restaurarse desde backup.
- El formulario informa finalidades y separa consentimientos.
- Existe un procedimiento manual documentado ante caída del sistema.

## 20. Evolución posterior, no comprometida

Después de validar al menos una ejecución completa se puede evaluar:

- Webhook e integración real de pasarela de pago.
- Automatización de WhatsApp con consentimiento y proveedor formal.
- Lista de espera automática y liberación temporizada de cupos.
- Gestión de múltiples experiencias y programas.
- Segmentación de continuidad.
- Embudo institucional separado.
- Acceso agregado y controlado para IAOS o subagentes.

Cada evolución requiere evidencia del piloto y una decisión explícita; no forma parte del MVP actual.

## 21. Conclusión

La arquitectura técnica mínima recomendada es una aplicación web única, PostgreSQL, Resend, pago externo o transferencia verificada manualmente y un panel interno básico. Esta combinación soporta el flujo comercial completo de la oferta de prueba con suficiente control, medición y trazabilidad, sin convertir una propuesta pendiente en oferta oficial ni construir tecnología mayor antes de validar el uso real.

El siguiente paso lógico dentro de la ruta es resolver las decisiones mínimas de la Fase 0 y, con ellas, convertir este diseño en un plan de implementación verificable.
