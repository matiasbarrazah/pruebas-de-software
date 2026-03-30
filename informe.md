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

La solución corresponde a una primera versión operativa para uso administrativo interno de la empresa, con registro manual de pedidos recibidos por email y WhatsApp.

### 1.3 Reglas de negocio mínimas

1. **Datos obligatorios de cliente:** nombre completo, teléfono y correo electrónico válido.
2. **Datos obligatorios de técnico:** nombre completo y especialidad (ej.: refrigeración, lavadoras, hornos).
3. **Estructura de reserva:** una reserva vincula exactamente un cliente, un técnico, una fecha y hora, una dirección y una descripción del problema.
4. **No se permiten reservas en el pasado:** la fecha y hora de la reserva debe ser posterior a la fecha/hora actual del servidor.
5. **No se permiten solapamientos:** un técnico no puede tener dos reservas simultáneas (misma fecha y hora).
6. **Cancelación de reserva:** una reserva puede ser cancelada registrando el motivo de cancelación; una vez cancelada no puede reactivarse.
7. **Consulta de reservas futuras:** devuelve todas las reservas con fecha/hora posterior o igual a la actual, ordenadas ascendentemente por fecha y hora.
8. **Mensajes de error claros:** toda operación fallida debe mostrar un mensaje comprensible al usuario (ej.: "El técnico no está disponible en esa fecha").

### 1.4 Elementos fuera de alcance

1. **Integración con email o WhatsApp:** el sistema no envía ni recibe mensajes automáticos; la empresa sigue registrando pedidos manualmente.
2. **Edición de reservas:** una vez creada, una reserva solo puede cancelarse, no modificarse.
3. **Gestión de usuarios/roles:** no hay login ni diferenciación de permisos; es un sistema administrativo de acceso directo.
4. **Historial o auditoría de cambios:** no se registran modificaciones pasadas ni quién hizo cada acción.
5. **Disponibilidad de técnicos:** no hay calendario de disponibilidad predefinido; el sistema solo evita solapamientos.
6. **Notificaciones a clientes o técnicos:** el sistema no notifica cambios, solo almacena datos.
7. **Análisis de reportes o estadísticas:** fuera de esta versión; se enfoca en operación básica.
8. **Soporte multi-idioma o zonas horarias:** se asume un único idioma (español) y zona horaria local (Chile).

## 2. Verificación vs. Validación en el proyecto

### Definición aplicada al contexto

- **Verificación:** ¿Estamos construyendo el producto correctamente? Responde si el código, la lógica y los procesos cumplen con las especificaciones definidas en la sección 1.3 (reglas de negocio).
- **Validación:** ¿Estamos construyendo el producto correcto? Responde si el sistema resuelve realmente el problema de la empresa y es utilizable en operación.

### Actividades de verificación concretas

1. **Prueba de validación de datos de entrada**
   - Verificar que un cliente no se registre sin nombre, teléfono o email válido.
   - Verificar que el sistema rechace un teléfono con caracteres no numéricos.
   - Verificar que un email sea validado contra formato RFC básico.
   - **Por qué es verificación:** comprueba que el código cumple la regla de negocio definida (datos obligatorios).

2. **Prueba de superposición de horarios**
   - Verificar que al intentar agendar un técnico en una fecha/hora donde ya tiene reserva, el sistema lance error.
   - Verificar que dos reservas del mismo técnico a horas distintas (sin solapamiento) se acepten correctamente.
   - **Por qué es verificación:** valida que la lógica de negocio de "no solapamientos" está codificada correctamente.

3. **Prueba de rechazo de fechas pasadas**
   - Verificar que el sistema rechace una reserva con fecha anterior a hoy.
   - Verificar que una reserva con fecha = hoy pero hora anterior a la actual sea rechazada.
   - **Por qué es verificación:** confirma que la restricción "no pasado" está implementada según especificación.

### Actividades de validación concretas

1. **Prueba con datos reales de clientes/técnicos**
   - Trabajar con información real que la empresa utiliza: nombres de técnicos que existen, clientes que han solicitado servicio.
   - Crear un escenario donde se simula una mañana de operación (5-10 reservas) y verificar que el flujo es usable.
   - **Por qué es validación:** determina si los datos y el flujo reflejan la realidad operativa de la empresa.

2. **Prueba de usabilidad: tiempo de consulta de reservas futuras**
   - Un operario de la empresa debe poder listar todas las reservas del próximo mes en menos de 2 segundos.
   - **Por qué es validación:** valida si el sistema es "usable" en el sentido práctico (velocidad aceptable para el negocio).

3. **Prueba de confiabilidad: recuperación ante error**
   - Cancelar una reserva a mitad del proceso (ej.: red cae) y verificar que el sistema mantiene consistencia (no queda semi-cancelada).
   - **Por qué es validación:** confirma que el sistema es "confiable" ante fallos reales que la empresa puede experimentar.

## 3. Decisiones de diseño frente a ambigüedades

### Decisión 1: Campos mínimos de cliente

**Ambigüedad detectada:** No se define qué datos mínimos requiere un cliente (sección 1.1.1).

**Alternativas consideradas:**
- Solo nombre y teléfono.
- Nombre, teléfono, email y dirección.
- Nombre, teléfono, email, dirección, RUT.

**Decisión tomada:** Nombre completo, teléfono y email.

**Justificación:** La empresa necesita contactar al cliente; email es estándar para confirmaciones; RUT y dirección pueden variar entre llamadas de servicio (ir a dirección del cliente, no domicilio registrado). Mantener mínimo reduce fricción en registro.

**Impacto en implementación:** Tabla cliente con 3 campos obligatorios; validación de email contra formato RFC; índice en teléfono para búsquedas rápidas.

**Impacto en pruebas:** Casos de prueba para email inválido, teléfono vacío, nombre con caracteres especiales.

---

### Decisión 2: Política de superposición de horarios

**Ambigüedad detectada:** No se aclara si un técnico puede tener dos reservas simultáneas (sección 1.1.5).

**Alternativas consideradas:**
- Permitir solapamientos; confiar en que el técnico lo resuelve.
- Prohibir solapamientos totalmente; un técnico no puede tener dos reservas a la misma hora.
- Permitir solapamientos solo si la duración de cada reserva se conoce previamente.

**Decisión tomada:** Prohibir solapamientos; una reserva ocupa la fecha y hora exacta; no hay duración definida.

**Justificación:** Atención técnica es presencial y no puede delegarse; si se asigna un técnico a cierta hora, no puede estar en dos lugares. Mantener modelo simple sin duración reduce complejidad.

**Impacto en implementación:** Al crear reserva, consultar si existe otra reserva del mismo técnico en la misma fecha/hora; rechazar si existe.

**Impacto en pruebas:** Casos para agregar dos reservas mismo técnico/hora (rechazar), mismo técnico/hora diferente (aceptar), diferente técnico/hora igual (aceptar).

---

### Decisión 3: Definición de "reservas futuras"

**Ambigüedad detectada:** "Reservas futuras" no está acotado; no se sabe desde cuándo se consulta (sección 1.1.7).

**Alternativas consideradas:**
- Reservas estrictamente futuras (fecha/hora > ahora).
- Reservas desde hoy en adelante (fecha/hora >= ahora, considerando solo la fecha).
- Reservas desde la próxima hora redonda (ej.: 10:00).

**Decisión tomada:** Reservas con fecha/hora >= fecha/hora actual del servidor (precisión por segundo).

**Justificación:** Permite incluir la reserva de hoy si está a futuro en el día; útil operativamente (ver qué queda por atender hoy). Precisión por segundo evita ambigüedad de límites.

**Impacto en implementación:** Query con filtro `WHERE fecha_hora >= NOW()` ordenado ASC por fecha_hora.

**Impacto en pruebas:** Casos para reservas de hoy (antes/después de now), mañana, mes próximo; validar orden.

---

### Decisión 4: Cancelación de reservas sin motivo obligatorio

**Ambigüedad detectada:** No hay reglas para cancelación; no se especifica si el motivo es obligatorio (sección 1.1.6).

**Alternativas consideradas:**
- Motivo obligatorio; sin motivo, rechazo.
- Motivo opcional; se registra si se proporciona.
- Motivo con lista predefinida (ej.: "Cliente canceló", "Técnico no disponible", "Otro").

**Decisión tomada:** Motivo opcional; se acepta una cancelación sin motivo pero se guarda en BD si se proporciona.

**Justificación:** Primera versión simple; agregar motivo sin obligar reduce fricción. Si la empresa lo necesita después, es fácil agregar validación.

**Impacto en implementación:** Campo `motivo_cancelacion` VARCHAR nullable en tabla reserva.

**Impacto en pruebas:** Casos para cancelar sin motivo (aceptar), con motivo (guardar), validar que reserva queda marcada como cancelada.

---

### Decisión 5: Sin autenticación/roles en versión inicial

**Ambigüedad detectada:** No se define si hay usuarios, login o roles (sección 1.1.8).

**Alternativas consideradas:**
- Sistema con login obligatorio; roles de admin/operario.
- Sin login; acceso directo a la app desde red interna.
- Login simple (solo usuario/contraseña sin roles).

**Decisión tomada:** Sin autenticación en versión 1; acceso directo para uso interno en red de la empresa.

**Justificación:** La empresa menciona que es herramienta interna de los operarios. Agregar login agrega complejidad sin valor claro en fase inicial. Si después necesita trazabilidad de quién hace qué, se agrega login.

**Impacto en implementación:** No hay tablas de usuarios; la app asume acceso controlado por red/firewall corporativo.

**Impacto en pruebas:** No hay casos de login/logout; las pruebas asumen acceso directo a funcionalidades.