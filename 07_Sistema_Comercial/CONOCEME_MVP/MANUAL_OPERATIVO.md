# Manual operativo sencillo — CONÓCEME

Estado: guía del entorno de prueba desplegado. La página está accesible con aviso
de pruebas y los correos automáticos reales están desactivados.

## 1. Qué hace el sistema

Administra el recorrido:

`Inscripción → pago pendiente → confirmación → recordatorios → asistencia → seguimiento`

La aplicación no cobra automáticamente, no revisa transferencias y no envía WhatsApp. Esas acciones permanecen bajo control humano.

## 2. Responsabilidades

**Alex Martínez**:

1. Revisar nuevas inscripciones.
2. Comparar el comprobante con la cuenta bancaria.
3. Confirmar únicamente pagos efectivamente recibidos.
4. Marcar asistencia o inasistencia después del evento.
5. Proteger los CSV y eliminar copias innecesarias.

**Sistema**:

1. Evitar registros duplicados por evento y correo.
2. Impedir más de 20 duplas confirmadas.
3. Registrar cambios de estado y actor.
4. Preparar correos sin duplicarlos.
5. Ejecutar recordatorios mediante un comando independiente.

## 3. Estados

| Estado | Significado | Próxima acción habitual |
|---|---|---|
| Pago pendiente | Inscripción recibida, sin pago verificado | Revisar transferencia |
| Confirmada | Pago verificado y cupo reservado | Esperar recordatorios |
| Cancelada | Inscripción anulada | Aplicar política provisional |
| Asistió | Dupla presente | Enviar agradecimiento y seguimiento |
| No asistió | Dupla confirmada ausente | No enviar mensaje hasta aprobarlo |
| Seguimiento enviado | Flujo postexperiencia completado | Cerrar operación |

Los cambios no permitidos son rechazados. Por ejemplo, una inscripción confirmada no puede saltar directamente a “Seguimiento enviado”.

## 4. Operación diaria antes del evento

1. Entrar al panel mediante `/admin/login`.
2. Filtrar por **Pago pendiente**.
3. Abrir una inscripción y comprobar nombre, referencia y monto.
4. Revisar la transferencia fuera de la aplicación.
5. Si el pago existe, seleccionar **Confirmada** y escribir una nota breve: “Pago verificado”.
6. Si debe cancelarse, seleccionar **Cancelada** y registrar el motivo operativo sin información clínica.
7. Ejecutar el procesador de mensajes programado. En pruebas se mantiene `EMAIL_SIMULATION=1`.

Estado operativo del entorno de prueba al 16 de julio de 2026: el servicio
`conoceme-recordatorios` se ejecuta cada hora, mantiene desactivado el seguimiento
de no asistentes y simula todos los envíos. Antes de cambiar `EMAIL_SIMULATION` a
`0`, revisar los mensajes pendientes y obtener autorización humana explícita.

Nunca marcar un pago como confirmado solo porque la persona envió un comprobante: debe verificarse en la cuenta bancaria.

## 5. Día del evento

1. Exportar el CSV solo si es necesario para la recepción.
2. Guardarlo en un dispositivo controlado; no enviarlo a grupos de WhatsApp.
3. Después de la experiencia, abrir cada inscripción confirmada.
4. Marcar **Asistió** o **No asistió**.
5. No registrar observaciones clínicas en las notas.

## 6. Después del evento

- Asistentes: el sistema prepara un agradecimiento una hora después y un seguimiento a las 48 horas.
- No asistentes: el borrador existe, pero está desactivado hasta aprobación humana.
- Cuando el seguimiento final se envía, la inscripción cambia automáticamente a **Seguimiento enviado** y queda trazabilidad del sistema.

## 7. Política provisional de cancelación

- Hasta 7 días antes: devolución del 100%.
- Entre 6 días y 48 horas antes: devolución del 50% o abono completo para otra experiencia.
- Dentro de 48 horas o por inasistencia: sin devolución; se permite transferir el cupo a otra dupla elegible.
- Si Serenamente cancela o cambia fecha o lugar y la dupla no puede asistir: devolución completa.
- Los derechos legales de las personas consumidoras prevalecen.

La política requiere aprobación final y revisión jurídica antes de recibir pagos reales.

## 8. Privacidad y seguridad

- No guardar diagnósticos, antecedentes clínicos ni relatos personales.
- No modificar consentimientos en nombre de una persona.
- No compartir contraseñas ni claves por correo o chat.
- No dejar CSV descargados en computadores compartidos.
- No copiar datos reales a ambientes de prueba.
- Usar siempre una contraseña administrativa de al menos 12 caracteres.

## 9. Fallas y continuidad manual

Si la aplicación o el correo fallan:

1. No repetir envíos inmediatamente.
2. Revisar el estado del mensaje en el panel.
3. Contactar manualmente solo a las personas afectadas y únicamente por motivos operativos.
4. Registrar lo ocurrido y la acción tomada.
5. No borrar registros para “volver a empezar”.

## 10. Base local de prueba

La base funciona en `127.0.0.1:55432` y se llama `serenamente_test`. No acepta conexiones desde otros equipos.

- Iniciar: `powershell -ExecutionPolicy Bypass -File scripts/start_local_database.ps1`
- Detener: `powershell -ExecutionPolicy Bypass -File scripts/stop_local_database.ps1`
- URL local: `postgresql://postgres@127.0.0.1:55432/serenamente_test`

Esta configuración usa autenticación local de confianza exclusivamente para pruebas en el equipo. No debe copiarse a producción.

## 11. Antes de una prueba real

Falta completar y aprobar:

- Número definitivo de la cuenta corriente.
- Textos de los correos de este paquete.
- Mensaje para no asistentes.
- Política de cancelación y devolución.
- Correo y dominio remitente verificados.
- Responsable y procedimiento de respaldo.
- Contraseña administrativa de producción.

Ningún evento debe pasar de `draft` a `published` sin autorización humana explícita.
