# Informe del Proyecto: Sistema de Reservas de Atención Técnica

## 1. Análisis inicial del requerimiento

### 1.1 Ambigüedades, vacíos y posibles conflictos detectados

A partir del enunciado original, se identifican 10 ambigüedades principales:

1. **Datos mínimos de cliente no definidos** (nombre, teléfono, email u otros).
2. **Datos mínimos de técnico no definidos** (especialidad, contacto, disponibilidad).
3. **Estructura de la reserva no especificada** (fecha/hora, duración, dirección, descripción de falla).
4. **No se define si se aceptan reservas en el pasado**.
5. **No se define si se permiten reservas superpuestas por técnico**.
6. **No hay reglas de cancelación** (quién cancela, hasta cuándo, condiciones).
7. **“Reservas futuras” no está acotado** (desde cuándo, orden, filtros).
8. **No se define autenticación/autorización** para usuarios del sistema.
9. **No se aclara si hay integración con email/WhatsApp** o solo carga manual.
10. **“Simple, usable y confiable” no tiene criterios medibles**.

### 1.2 Versión mejorada y precisa del requerimiento

La empresa requiere una aplicación web interna para gestionar reservas de atención técnica de electrodomésticos.

El sistema debe permitir:

- Registrar clientes con los campos obligatorios: nombre completo, teléfono y email.
- Registrar técnicos con los campos obligatorios: nombre completo y especialidad.
- Crear una reserva asociando exactamente un cliente y un técnico, indicando fecha y hora de atención, dirección y descripción breve del problema.
- Cancelar una reserva existente, registrando motivo de cancelación.
- Consultar reservas futuras ordenadas por fecha y hora ascendente.

El sistema debe considerar además:

- No permitir reservas en fechas/horas pasadas.
- No permitir superposición de reservas para un mismo técnico en el mismo horario.
- Mostrar mensajes de error claros cuando una operación no pueda realizarse.
- Persistir clientes, técnicos y reservas en una base de datos.