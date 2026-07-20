# SER-IAOS-SCO-01 - Sistema Comercial Operativo Serenamente

Estado: Documento operativo IAOS aplicado
Fecha: 2026-07-10
Responsable operativo: Alex
Proyecto: Serenamente
Condicion: Arquitectura operativa propuesta para captacion, registro, pago/reserva, automatizacion y seguimiento; no implementa todavia software
Fuentes: SER-IAOS-MCO-01, SER-IAOS-CMS-01, SER-IAOS-ASM-01, SER-IAOS-MVIS-01, SER-IAOS-FOP-01

## 1. Proposito

Este documento define el sistema comercial operativo minimo que Serenamente necesita para convertir interes en registros, pagos o reservas, asistencia, seguimiento y continuidad.

No es una landing, una campana ni una oferta especifica. Es el mapa funcional del sistema que debe existir para que contenido, anuncios, subagentes, talleres y propuestas comerciales no generen interes que luego se pierda.

## 2. Problema actual

Serenamente cuenta con presencia visual, Instagram, piezas graficas, experiencias reales y material metodologico. Sin embargo, todavia no existe un sistema completo que permita:

- captar a una persona interesada;
- mostrarle una oferta clara;
- registrar sus datos;
- cobrar una entrada o reservar cupo;
- enviar confirmacion automatica;
- enviar recordatorios;
- registrar asistencia;
- enviar seguimiento posterior;
- ofrecer continuidad;
- medir conversiones.

Sin este sistema, los agentes de contenido, anuncios o landing pueden generar movimiento, pero no necesariamente conversion organizada.

## 3. Regla operativa

Antes de escalar anuncios, contenido o subagentes en paralelo, Serenamente necesita un flujo minimo de conversion.

Formula del flujo:

Atencion -> Interes -> Registro -> Pago o reserva -> Confirmacion -> Recordatorio -> Asistencia -> Seguimiento -> Continuidad

Cada pieza comercial debe conectarse a este flujo.

## 4. Sistema minimo viable

### 4.1 Entrada de trafico

Fuentes posibles:

- Instagram organico.
- Anuncios de Instagram.
- Historias.
- QR fisico.
- Referidos.
- Mensajes institucionales.
- Landing principal.
- Pagina de una experiencia especifica.

Necesidad:

Cada fuente debe enviar a una accion clara: registrarse, reservar, escribir por WhatsApp o solicitar informacion.

### 4.2 Pagina o punto de conversion

Funcion:

Explicar brevemente la oferta y permitir tomar accion.

Formatos posibles:

- Landing principal con seccion de proximas experiencias.
- Pagina especifica por experiencia.
- Formulario simple.
- Link de pago externo.
- WhatsApp como conversion manual inicial.

Requisito minimo:

Debe tener una llamada a accion unica y clara.

### 4.3 Registro

Datos minimos recomendados:

- Nombre.
- Email.
- Telefono o WhatsApp.
- Experiencia o evento de interes.
- Fecha del evento.
- Estado: interesado, reservado, pagado, asistio, no asistio, seguimiento enviado.
- Consentimiento basico para contacto.

Datos opcionales:

- Comuna o ciudad.
- Como llego.
- Necesidad principal.
- Si acepta recibir informacion futura.

### 4.4 Pago o reserva

Opciones posibles:

- Reserva gratuita con confirmacion manual.
- Pago por transferencia.
- Pago por link externo.
- Webpay/Mercado Pago/Flow u otra pasarela.
- Pago presencial, si se decide.

Criterio operativo:

Para primera version, no es obligatorio construir una pasarela propia. Se puede partir con reserva + pago externo, siempre que el sistema registre el estado.

### 4.5 Confirmacion automatica

Funcion:

Enviar al participante una confirmacion clara despues de registrarse o pagar.

Contenido minimo:

- Nombre de la experiencia.
- Fecha y hora.
- Lugar o link.
- Que llevar.
- Duracion.
- Contacto.
- Mensaje calido de bienvenida.

Canales posibles:

- Email automatico.
- WhatsApp manual o semiautomatico.

Herramienta posible:

- Resend para email transaccional.

### 4.6 Recordatorios

Funcion:

Reducir ausencias y aumentar asistencia.

Recordatorios recomendados:

- 24 horas antes.
- 2 o 3 horas antes.
- Recordatorio especial si cambia lugar, hora o instruccion.

Canales:

- Email.
- WhatsApp, si se gestiona manual o con herramienta futura.

### 4.7 Gestion interna

Funcion:

Permitir a Alex/Helen ver inscritos, estados, pagos y asistencia.

Vista minima requerida:

- Lista de inscritos.
- Estado de pago/reserva.
- Contacto.
- Evento asociado.
- Notas internas.
- Asistencia.
- Seguimiento enviado.

Opciones iniciales:

- Panel simple propio.
- Base de datos consultable.
- Exportacion CSV.
- Google Sheets si se decide usar como puente manual.

### 4.8 Asistencia

Funcion:

Registrar quien asistio realmente.

Metodos:

- Check-in manual.
- Lista impresa.
- Panel interno.
- Codigo o QR futuro.

Uso:

- Seguimiento.
- Medicion.
- Testimonios si hay permiso.
- Invitacion a continuidad.

### 4.9 Seguimiento posterior

Funcion:

Mantener relacion y abrir continuidad.

Mensajes posibles:

- Gracias por asistir.
- Recurso de practica.
- Encuesta breve.
- Invitacion a proxima experiencia.
- Solicitud de testimonio, si corresponde.

Tiempo recomendado:

- Mismo dia o dia siguiente.
- Segundo seguimiento 3 a 7 dias despues.

### 4.10 Medicion

Indicadores minimos:

- Visitas o clics.
- Registros.
- Pagos/reservas.
- Asistencia.
- Ausencias.
- Fuente de llegada.
- Conversion de registro a asistencia.
- Interes en continuidad.

## 5. Arquitectura funcional propuesta

### Modulo 1 - Catalogo de experiencias

Contiene:

- Nombre de experiencia.
- Descripcion.
- Publico.
- Fecha.
- Modalidad.
- Cupos.
- Precio o tipo de reserva.
- Estado: borrador, publicada, cerrada, realizada.

### Modulo 2 - Landing o paginas publicas

Contiene:

- Presentacion de Serenamente.
- Proximas experiencias.
- Pagina por evento.
- Formulario de registro.
- Llamada a accion.

### Modulo 3 - Registro de interesados e inscritos

Contiene:

- Personas interesadas.
- Inscritos por evento.
- Estado de pago/reserva.
- Fuente de llegada.
- Consentimiento de contacto.

### Modulo 4 - Pagos o confirmacion de reserva

Contiene:

- Estado de pago.
- Metodo de pago.
- Comprobante o referencia.
- Cupo confirmado.

### Modulo 5 - Automatizacion de mensajes

Contiene:

- Email de confirmacion.
- Email de recordatorio.
- Email post-evento.
- Plantillas por experiencia.

### Modulo 6 - Panel interno

Contiene:

- Eventos activos.
- Inscritos.
- Pagos/reservas.
- Asistencia.
- Seguimiento.
- Exportacion.

### Modulo 7 - Medicion y aprendizaje

Contiene:

- Conversiones.
- Fuentes de trafico.
- Asistencia.
- Respuestas post-evento.
- Aprendizajes para IAOS.

## 6. Stack tecnico posible

### Opcion A - Manual ligero

Componentes:

- Landing simple.
- Formulario externo.
- Google Sheets.
- Pago por transferencia o link externo.
- Correos manuales.

Ventajas:

- Rapido.
- Barato.
- Bajo riesgo tecnico.

Riesgos:

- Poco automatizado.
- Escala mal.
- Mucho trabajo manual.

Uso recomendado:

Prueba inicial si se necesita validar oferta antes de construir sistema propio.

### Opcion B - Semi-automatizado

Componentes:

- Landing propia.
- Formulario propio.
- Base de datos.
- Resend para correos automaticos.
- Pago externo o transferencia validada manualmente.
- Panel simple de inscritos.

Ventajas:

- Equilibrio entre velocidad y control.
- Permite automatizar confirmaciones y recordatorios.
- Base suficiente para agentes y medicion.

Riesgos:

- Requiere implementacion tecnica.
- Pago puede seguir siendo parcial/manual.

Uso recomendado:

Primera version seria del sistema Serenamente.

### Opcion C - Sistema completo

Componentes:

- Aplicacion web.
- Base de datos.
- Pasarela de pago integrada.
- Emails automaticos.
- Panel interno.
- Automatizaciones.
- Analitica.
- Gestion de eventos, cupos y asistentes.

Ventajas:

- Escalable.
- Profesional.
- Menos trabajo manual.

Riesgos:

- Mayor complejidad.
- Requiere mas decisiones tecnicas.
- Puede retrasar validacion comercial si se construye antes de validar oferta.

Uso recomendado:

Despues de validar flujo, oferta y demanda.

## 7. Herramientas candidatas

### Railway

Uso posible:

- Hospedar backend o aplicacion.
- Ejecutar base de datos.
- Mantener API de registros, eventos y asistentes.

Encaje:

Bueno para una version semi-automatizada o completa.

### Resend

Uso posible:

- Emails transaccionales.
- Confirmaciones.
- Recordatorios.
- Seguimiento posterior.

Encaje:

Muy adecuado para automatizacion de correos.

### Base de datos

Opciones:

- PostgreSQL en Railway.
- Supabase, si se decide.
- SQLite para prototipo local, no ideal para produccion.

Necesidad:

Registrar eventos, inscritos, pagos/reservas, asistencia y seguimiento.

### Pasarela de pago

Opciones a evaluar:

- Mercado Pago.
- Flow.
- Webpay/Transbank.
- Link de pago externo.
- Transferencia manual.

Decision pendiente:

Definir que metodo es viable para Helen/Alex y para el publico objetivo.

### WhatsApp

Uso posible:

- Contacto directo.
- Confirmacion manual.
- Resolucion de dudas.
- Seguimiento de alta cercania.

Cuidado:

No depender solo de WhatsApp si se quiere escalar.

## 8. Flujo minimo recomendado para primera version

Recomendacion operativa:

Partir con una version semi-automatizada, no con sistema completo.

Flujo:

1. Persona llega desde Instagram, anuncio, QR o link.
2. Entra a una pagina de Serenamente o experiencia disponible.
3. Lee informacion esencial.
4. Completa formulario de registro.
5. El sistema guarda sus datos.
6. El sistema envia confirmacion por email.
7. Si hay pago, se deriva a pago externo o instrucciones claras.
8. Alex/Helen revisan inscritos en panel o base.
9. El sistema envia recordatorio automatico.
10. Se registra asistencia.
11. El sistema envia seguimiento posterior.
12. IAOS analiza conversion y aprendizaje.

## 9. Datos iniciales requeridos antes de implementar

### Datos de marca y contacto

- Email remitente.
- Nombre del remitente.
- Telefono/WhatsApp de contacto.
- Instagram oficial.
- Logo final a usar.

### Datos de primera experiencia o evento

- Nombre.
- Fecha.
- Hora.
- Lugar o modalidad.
- Cupos.
- Precio o modalidad de reserva.
- Descripcion breve.
- Que incluye.
- Que debe llevar la persona.

### Datos operativos

- Metodo de pago.
- Politica de devolucion o cambios, si aplica.
- Quien recibe notificaciones internas.
- Quien confirma pagos manuales.
- Quien marca asistencia.

### Datos legales/comunicacionales basicos

- Consentimiento para contacto.
- Politica simple de uso de datos.
- Permiso para recibir informacion futura.
- Aviso si se toman fotos o videos durante el evento.

## 10. Relacion con subagentes

### Subagente Landing y Presencia Web

Debe construir paginas conectadas al flujo de registro, no solo paginas informativas.

### Subagente Contenido e Instagram

Debe crear piezas que lleven a una accion medible: registro, reserva, WhatsApp o consulta.

### Subagente Talleres y Experiencias

Debe entregar informacion estructurada que pueda convertirse en evento registrable: nombre, fecha, duracion, cupos, materiales y promesa.

### Subagente Institucional

Debe distinguir entre venta institucional y venta de entrada individual. Si vende a institucion, el flujo puede ser lead/propuesta/reunion, no pago por entrada.

### Subagente Medicion y Aprendizaje

Debe medir el embudo completo, no solo likes o visualizaciones.

## 11. Embudos por tipo de venta

### Embudo individual/comunidad

Instagram o anuncio -> pagina de experiencia -> registro -> pago/reserva -> confirmacion -> recordatorio -> asistencia -> seguimiento -> proxima experiencia.

### Embudo institucional

Contacto o propuesta -> reunion -> ajuste de servicio -> acuerdo -> ejecucion -> reporte -> continuidad.

### Embudo recursos

Contenido educativo -> recurso gratuito o producto -> registro o compra -> envio -> seguimiento -> experiencia o programa relacionado.

## 12. Criterios para decidir si construir tecnologia ahora

Conviene construir version semi-automatizada si:

- Existe o se definira pronto una experiencia a ofrecer.
- Se quiere captar por Instagram o anuncios.
- Se necesita reducir trabajo manual.
- Se quiere medir conversion.
- Se planea repetir eventos.

Conviene esperar si:

- No hay oferta priorizada.
- No hay fecha tentativa.
- No se sabe si sera venta individual o institucional.
- No se ha definido metodo de pago.

Decision recomendada:

Construir primero el diseño funcional del sistema y luego una version minima semi-automatizada cuando se defina la primera experiencia/evento.

## 13. Orden recomendado desde aqui

1. Definir oferta/evento minimo para probar el flujo.
2. Definir si el primer embudo sera individual/comunidad, institucional o mixto.
3. Definir metodo de pago o reserva.
4. Diseñar arquitectura tecnica minima.
5. Implementar registro + base de datos + email de confirmacion.
6. Agregar recordatorios.
7. Agregar panel interno simple.
8. Agregar medicion.
9. Activar subagentes de contenido/anuncios con destino claro.

## 14. Preguntas humanas pendientes

- Se venderan entradas individuales o se priorizara venta institucional?
- Que metodo de pago se usara inicialmente?
- Se aceptara reserva sin pago?
- Cual sera el email oficial de envio?
- Quien administrara inscritos?
- Que datos se pueden pedir sin generar friccion?
- Que plataforma actual existe y si conviene reemplazarla o integrarla?
- Hay dominio disponible?
- Que nivel de automatizacion se necesita en la primera version?

## 15. Conclusion

El sistema comercial operativo es el puente entre estrategia y ejecucion. Sin este sistema, el contenido, los anuncios y los agentes pueden generar atencion, pero no necesariamente registros, pagos, asistencia ni continuidad.

La ruta recomendada es construir una version semi-automatizada una vez definida la primera oferta o evento a probar: pagina o formulario, registro, base de datos, confirmacion por email, recordatorios, gestion interna y seguimiento posterior.
