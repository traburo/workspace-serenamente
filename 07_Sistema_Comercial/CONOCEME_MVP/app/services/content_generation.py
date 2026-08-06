from datetime import datetime, time, timedelta


class WeeklyContentGenerator:
    """Generador inicial reemplazable por un proveedor de IA externo."""

    def generate(self, campaign):
        start = campaign["starts_on"]
        theme = campaign["theme"].strip()
        audience = campaign["audience"].strip()
        common = {
            "assumptions": "Instagram continúa siendo el canal principal. El CTA es comunitario, no comercial.",
            "approval_pending": "Revisión final de lenguaje, dirección visual y autorización de publicación.",
            "blocking_issues": ["Revisión humana obligatoria antes de aprobar."],
        }

        def scheduled(day, hour):
            return datetime.combine(start + timedelta(days=day), time(hour, 0)).isoformat()

        return [
            {
                **common, "title": f"Carrusel — {theme}", "pillar": "Comprender",
                "format": "Carrusel", "scheduled_for": scheduled(0, 19),
                "objective": "Generar identificación, guardados y compartidos.",
                "cta": "Guárdalo para volver a esta idea y compártelo con quien pueda necesitarla.",
                "caption": (
                    f"{theme}\n\nA veces la sobrecarga no se nota como un gran momento de crisis. "
                    "Puede aparecer como cansancio constante, dificultad para detenerse o la sensación "
                    "de que siempre queda algo pendiente.\n\nHacer una pausa no elimina tus responsabilidades, "
                    "pero puede ayudarte a observarlas con más claridad y cuidado.\n\n"
                    "¿Qué señal te indica que necesitas bajar el ritmo?"
                ),
                "script": "Lámina 1: gancho. Láminas 2–4: señales cotidianas de sobrecarga. "
                          "Lámina 5: permiso para pausar. Lámina 6: pregunta y CTA.",
                "visual_direction": "Carrusel de seis láminas, lectura amplia, una idea por pantalla y contraste accesible.",
                "sources": "SER-NM-01; SER-MM-01; SER-IAOS-FIO-01.",
            },
            {
                **common, "title": "Reel — Una pausa de treinta segundos", "pillar": "Respirar",
                "format": "Reel", "scheduled_for": scheduled(2, 19),
                "objective": "Ofrecer una experiencia breve y favorecer guardados.",
                "cta": "Guarda este video para repetir la pausa cuando la necesites.",
                "caption": "Una pausa breve no tiene que ser perfecta. Solo necesita darte un momento para volver a escucharte.",
                "script": (
                    "0–3 s: Helen a cámara: ‘Si estás sosteniendo demasiado, hagamos una pausa breve’.\n"
                    "3–12 s: apoyar ambos pies y observar el contacto con el suelo.\n"
                    "12–22 s: respirar sin forzar y notar una sensación corporal.\n"
                    "22–30 s: ‘No tienes que resolver todo ahora. Empieza por volver a ti’."
                ),
                "visual_direction": "Helen real frente a cámara, luz natural, subtítulos grandes y planos de apoyo sencillos.",
                "sources": "SER-MM-01; plantilla VIDEO_REFERENCIA_01. Validar la práctica exacta antes de grabar.",
            },
            {
                **common, "title": "Publicación humana — Lo que también merece cuidado", "pillar": "Conectar",
                "format": "Publicación", "scheduled_for": scheduled(4, 19),
                "objective": "Crear cercanía y conversación con la comunidad.",
                "cta": "Si te hace sentido, cuéntanos con una palabra qué necesitas cuidar esta semana.",
                "caption": (
                    f"Esta semana estamos conversando sobre: {theme.lower()}\n\n"
                    "Detrás de muchas mujeres que sostienen familias, equipos, decisiones y tareas, "
                    "también hay una persona que necesita espacio, escucha y cuidado.\n\n"
                    "No siempre podemos soltar todo. Pero sí podemos comenzar reconociendo cómo estamos."
                ),
                "script": "", "visual_direction": "Retrato auténtico de Helen o escena cotidiana autorizada; evitar imagen de bienestar genérica.",
                "sources": "SER-NM-01; SER-IAOS-FIO-01.",
            },
            {
                **common, "title": "Historias — Reconocer la sobrecarga", "pillar": "Comprender",
                "format": "Historias", "scheduled_for": scheduled(1, 12),
                "objective": "Obtener respuestas e identificar situaciones de la comunidad.",
                "cta": "Responder la encuesta.",
                "caption": "Historia 1: ¿Sientes que estás sosteniendo demasiadas cosas al mismo tiempo?\n"
                           "Encuesta: Sí, necesito una pausa / A veces me pasa.\n"
                           "Historia 2: ¿Dónde notas primero la sobrecarga? Caja de respuestas.",
                "script": "", "visual_direction": "Fondos simples, texto breve y controles interactivos en zona segura.",
                "sources": "SER-IAOS-FIO-01.",
            },
            {
                **common, "title": "Historias — Pausa acompañada", "pillar": "Respirar",
                "format": "Historias", "scheduled_for": scheduled(3, 12),
                "objective": "Acompañar una acción breve y segura.",
                "cta": "Desliza para avanzar y responde cómo te sentiste.",
                "caption": "Historia 1: Antes de seguir, observa cómo estás.\nHistoria 2: Apoya los pies y permite una respiración sin esfuerzo.\n"
                           "Historia 3: ¿Cambió algo, aunque sea un poco? Sí / No todavía.",
                "script": "", "visual_direction": "Secuencia pausada con indicador de progreso y texto accesible.",
                "sources": "SER-MM-01. La práctica debe validarse antes de publicación.",
            },
            {
                **common, "title": "Historias — Conversación comunitaria", "pillar": "Avanzar",
                "format": "Historias", "scheduled_for": scheduled(6, 18),
                "objective": "Cerrar la semana con participación y obtener temas futuros.",
                "cta": "Responder la caja de preguntas.",
                "caption": f"Historia 1: Esta semana hablamos de ‘{theme}’.\nHistoria 2: ¿Qué tema te gustaría que abordáramos la próxima semana?",
                "script": "", "visual_direction": "Cierre humano, sobrio y abierto a respuestas.",
                "sources": "Brief de campaña; SER-IAOS-FIO-01.",
            },
        ]
