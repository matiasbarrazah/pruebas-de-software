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
7. **Criterios de consulta de reservas no definidos** (qué estados incluir, desde cuándo, orden y filtros).
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
7. **Consulta de reservas futuras:** devuelve reservas no canceladas con fecha/hora posterior o igual a la actual, ordenadas ascendentemente por fecha y hora.
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
   - Verificar que un email sea validado contra formato básico.
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

2. **Prueba de usabilidad: tiempo de consulta de reservas futuras no canceladas**
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

### Decisión 3: Criterios de consulta de reservas futuras

**Ambigüedad detectada:** No se define con precisión qué reservas se muestran en la consulta (estados incluidos, límite temporal y orden) (sección 1.1.7).

**Alternativas consideradas:**
- Mostrar todas las reservas, incluyendo canceladas.
- Mostrar solo reservas no canceladas con fecha/hora >= ahora.
- Mostrar reservas por estado configurable (pendiente/cancelada) con filtros manuales.

**Decisión tomada:** Mostrar solo reservas no canceladas con fecha/hora >= fecha/hora actual del servidor, ordenadas ascendentemente.

**Justificación:** La empresa necesita ver trabajo pendiente real; incluir canceladas genera ruido operativo. El límite temporal por fecha/hora actual permite ver lo que aún falta por atender hoy y días siguientes.

**Impacto en implementación:** Query con filtros `WHERE estado != 'cancelada' AND fecha_hora >= NOW()` ordenado ASC por fecha_hora.

**Impacto en pruebas:** Casos para reservas canceladas (no deben aparecer), reservas de hoy (antes/después de now), mañana y mes próximo; validar orden.

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

## 5. Estrategia, diseño y ejecución de pruebas

### 5.1 Objetivos de prueba

- Verificar que cada funcionalidad del sistema opera correctamente según las reglas de negocio definidas en la sección 1.3.
- Detectar fallos en validaciones de entrada, restricciones de negocio y manejo de errores.
- Confirmar que el sistema responde de forma controlada ante entradas límite, inválidas y situaciones de uso anómalas.

### 5.2 Alcance de pruebas

**Incluido:**
- Registro de clientes con validación de campos obligatorios (nombre, teléfono, email).
- Registro de técnicos con validación de campos obligatorios.
- Creación de reservas con restricciones de fecha futura y no solapamiento de horario por técnico.
- Cancelación de reservas (con y sin motivo).
- Consulta y orden de reservas futuras no canceladas.
- Comportamiento del sistema ante IDs inexistentes y operaciones duplicadas.

**Excluido:**
- Autenticación/login (fuera de alcance por decisión de diseño 5).
- Integración con servicios externos (email, WhatsApp).
- Pruebas de rendimiento o carga.
- Pruebas de interfaz de usuario (navegador automatizado).

### 5.3 Criterios de entrada y salida

**Criterios de entrada:**
- Base de datos inicializada con esquema correcto (`init_db()`).
- Al menos un cliente y un técnico registrados (precondición de tests de reservas).
- Aplicación Flask arrancada en modo testing.

**Criterios de salida:**
- 100% de los casos de prueba obligatorios ejecutados.
- 0 fallos en casos funcionales, negativos y de borde.
- Todos los casos disruptivos manejados sin crash ni corrupción de BD.

### 5.4 Estrategia de pruebas

Las pruebas son **automatizadas unitarias de integración** usando `unittest` y el cliente de pruebas de Flask (`app.test_client()`). Cada prueba realiza peticiones HTTP reales contra la aplicación con una base de datos SQLite en archivo temporal, verificando el comportamiento real de extremo a extremo (formulario → lógica → BD).

No se usan mocks de la base de datos: cada test opera sobre SQLite real para que las restricciones de integridad referencial y las queries sean ejercitadas de verdad.

El script de pruebas se ubica en `tests/test_suite.py` y puede ejecutarse con:

```bash
python -X utf8 tests/test_suite.py
```

### 5.5 Casos de prueba

#### 5.5.1 Casos funcionales

| ID | Nombre | Precondición | Pasos | Resultado esperado | Resultado obtenido |
|---|---|---|---|---|---|
| CP-F01 | Registrar cliente con datos válidos | Sin cliente con ese email | POST /clientes con nombre, teléfono y email válidos | Flash "registrado correctamente" | PASS |
| CP-F02 | Registrar técnico con datos válidos | Sin técnico previo | POST /tecnicos con nombre y especialidad | Flash "registrado correctamente" | PASS |
| CP-F03 | Crear reserva con fecha futura | Cliente y técnico registrados | POST /reservas/nueva con todos los campos, fecha 2099-06-15 10:00 | Redirect a index con flash de éxito | PASS |
| CP-F04 | Reservas futuras ordenadas ASC por fecha | Dos reservas futuras en fechas distintas | GET / y verificar orden en HTML | La fecha más próxima aparece primero | PASS |
| CP-F05 | Cancelar reserva con motivo | Reserva en estado pendiente | POST /reservas/{id}/cancelar con motivo | estado=cancelada y motivo guardado en BD | PASS |
| CP-F06 | Cancelar reserva sin motivo | Reserva en estado pendiente | POST /reservas/{id}/cancelar con motivo vacío | estado=cancelada, motivo_cancelacion=NULL en BD | PASS |
| CP-F07 | Reserva cancelada no aparece en listado | Reserva en estado pendiente | Cancelar y luego GET / | Descripción de la reserva ausente del HTML | PASS |
| CP-F08 | Dos técnicos distintos, misma hora | Técnicos distintos libres a esa hora | Crear dos reservas con técnicos distintos y misma fecha/hora | Ambas reservas se crean exitosamente | PASS |

#### 5.5.2 Casos de borde

| ID | Nombre | Precondición | Pasos | Resultado esperado | Resultado obtenido |
|---|---|---|---|---|---|
| CP-B01 | Email con '+' es válido | Sin cliente con ese email | POST /clientes con email='test+tag@dominio.cl' | Cliente registrado sin error | PASS |
| CP-B02 | Nombre con tildes y ñ | Sin cliente con ese email | POST /clientes con nombre con caracteres especiales | Cliente registrado sin error | PASS |
| CP-B03 | Teléfono formato internacional | Sin cliente con ese email | POST /clientes con teléfono='+56 9 1234 5678' | Cliente registrado sin error | PASS |
| CP-B04 | Descripción de 500 caracteres | Cliente y técnico registrados | POST /reservas/nueva con descripción de 500 chars | Reserva creada sin truncamiento ni error | PASS |
| CP-B05 | Reusar hora de reserva cancelada | Técnico con reserva cancelada a esa hora | Crear nueva reserva para el mismo técnico en la misma hora | El sistema acepta la reserva (la hora quedó libre) | PASS |

#### 5.5.3 Casos negativos

| ID | Nombre | Precondición | Pasos | Resultado esperado | Resultado obtenido |
|---|---|---|---|---|---|
| CP-N01 | Email inválido sin '@' | Cualquier estado | POST /clientes con email='noesuncorreo' | Flash de error indicando formato inválido | PASS |
| CP-N02 | Reserva con fecha pasada | Cliente y técnico registrados | POST /reservas/nueva con fecha_hora='2000-01-01T10:00' | Flash de error indicando que la fecha debe ser futura | PASS |
| CP-N03 | Solapamiento mismo técnico/hora | Técnico id=1 con reserva a las 2099-05-05 15:00 | POST /reservas/nueva con mismo técnico y misma hora | Flash "el técnico ya tiene una reserva en esa fecha y hora" | PASS |

#### 5.5.4 Casos disruptivos

| ID | Nombre | Precondición | Pasos | Resultado esperado | Resultado obtenido |
|---|---|---|---|---|---|
| CP-D01 | Doble cancelación de una reserva | Reserva ya en estado cancelada | GET /reservas/{id}/cancelar sobre reserva cancelada | Flash "La reserva ya fue cancelada", sin corrupción en BD | PASS |
| CP-D02 | Acceder a ID de reserva inexistente | No existe reserva con id=99999 | GET /reservas/99999/cancelar | Flash "Reserva no encontrada", redirect a index sin crash | PASS |

### 5.6 Evidencias de ejecución

```
=================================================================
  SUITE DE PRUEBAS - SISTEMA DE RESERVAS DE ATENCION TECNICA
=================================================================

  [Funcionales]
  [+] CP-F01 - Registrar cliente con datos validos
  [+] CP-F02 - Registrar tecnico con datos validos
  [+] CP-F03 - Crear reserva con datos validos y fecha futura
  [+] CP-F04 - Reservas futuras listadas ordenadas ASC por fecha
  [+] CP-F05 - Cancelar reserva con motivo guarda estado y motivo en BD
  [+] CP-F06 - Cancelar sin motivo deja motivo_cancelacion NULL en BD
  [+] CP-F07 - Reserva cancelada no aparece en listado de futuras
  [+] CP-F08 - Dos tecnicos distintos pueden tener reserva en la misma hora

  [Borde]
  [+] CP-B01 - Email con '+' es aceptado como valido
  [+] CP-B02 - Nombre con caracteres especiales (tildes, enie) es aceptado
  [+] CP-B03 - Telefono con formato internacional '+56 9 1234 5678' es aceptado
  [+] CP-B04 - Descripcion de 500 caracteres es aceptada sin error
  [+] CP-B05 - Tecnico puede ocupar hora de una reserva previamente cancelada

  [Negativos]
  [+] CP-N01 - Email sin '@' es rechazado con mensaje de error
  [+] CP-N02 - Reserva con fecha en el pasado es rechazada
  [+] CP-N03 - Solapamiento de horario para el mismo tecnico es rechazado

  [Disruptivos]
  [+] CP-D01 - Cancelar una reserva ya cancelada muestra error sin corromper BD
  [+] CP-D02 - Acceder a reserva con ID inexistente retorna error controlado

=================================================================
  RESUMEN
=================================================================
  Funcional     8/8 pasados
  Borde         5/5 pasados
  Negativo      3/3 pasados
  Disruptivo    2/2 pasados
-----------------------------------------------------------------
  TOTAL        18/18 pasados
=================================================================
```

### 5.7 Pruebas de detección de bugs

Tras ejecutar la suite principal, se diseñó una segunda ronda de pruebas orientada específicamente a encontrar fallos en la implementación, atacando supuestos no validados en el código. El script se encuentra en `tests/test_bugs.py`.

Se ejecutaron 12 casos adicionales y se detectaron **7 bugs reales**.

#### Evidencia de ejecución

```
=================================================================
  TESTS DE DETECCION DE BUGS — SISTEMA DE RESERVAS
=================================================================

  [Validacion de campos]
  [X] CP-V01 - Telefono con solo guiones es rechazado
  [+] CP-V02 - Telefono con solo espacios es rechazado
  [+] CP-V03 - Telefono de 6 digitos (bajo minimo) es rechazado
  [+] CP-V04 - Telefono con letras es rechazado

  [Validacion de fecha]
  [X] CP-F01 - Fecha con formato invalido 'not-a-date' es rechazada
  [X] CP-F02 - Fecha sin hora '2099-01-01' es rechazada
  [X] CP-F03 - Cadena 'zzz-zzz' no se acepta como fecha

  [Integridad referencial]
  [X] CP-R01 - Reserva con cliente_id inexistente muestra error controlado (no crash)
  [X] CP-R02 - Reserva con tecnico_id inexistente muestra error controlado (no crash)
  [X] CP-R03 - cliente_id no numerico ('abc') no produce crash

  [Duplicados]
  [+] CP-D01 - Email duplicado en mayusculas es detectado como duplicado

  [Comportamiento limite]
  [+] CP-L01 - Multiples errores simultaneos se muestran todos

=================================================================
  RESUMEN
=================================================================
  TOTAL  5/12 pasados  |  7 BUGS encontrados
=================================================================
```

#### Catálogo de bugs encontrados

| ID | Descripción | Causa raíz | Severidad |
|---|---|---|---|
| BUG-01 (CP-V01) | Teléfono `"-------"` es aceptado como válido | Regex `^\+?[\d\s\-]{7,15}$` no exige al menos un dígito | Media |
| BUG-02 (CP-F01) | Cadena `"not-a-date"` pasa la validación de fecha futura | La validación compara strings lexicográficamente: `"n" > "2"` → pasa | Alta |
| BUG-03 (CP-F02) | Fecha sin hora `"2099-01-01"` es aceptada y almacenada | Misma causa que BUG-02; además rompe la detección de solapamientos | Alta |
| BUG-04 (CP-F03) | Cualquier string mayor que `"2026..."` en ASCII pasa como fecha futura | Misma causa raíz que BUG-02 y BUG-03 | Alta |
| BUG-05 (CP-R01) | `cliente_id=9999` (inexistente) provoca crash en lugar de error controlado | `IntegrityError` de clave foránea no capturado en la ruta `/reservas/nueva` | Alta |
| BUG-06 (CP-R02) | `tecnico_id=9999` (inexistente) provoca crash y deja la BD bloqueada | Mismo origen que BUG-05; además `OperationalError: database is locked` en tests subsiguientes | Alta |
| BUG-07 (CP-R03) | `cliente_id="abc"` (no numérico) provoca crash | Sin validación de tipo entero antes del `INSERT`; la excepción no es capturada | Alta |

#### Análisis de causa raíz común

Los bugs BUG-02, BUG-03 y BUG-04 comparten la misma causa: la validación de fecha futura se implementó como comparación de strings (`fecha_hora <= now_str()`). Esto funciona correctamente solo cuando el input tiene formato ISO `YYYY-MM-DDTHH:MM`; cualquier otro string que sea lexicográficamente mayor que la fecha actual pasa la validación sin error.

Los bugs BUG-05, BUG-06 y BUG-07 comparten también una causa común: la ruta de creación de reservas no valida que `cliente_id` y `tecnico_id` sean enteros existentes en la BD antes de ejecutar el `INSERT`. La restricción de clave foránea de SQLite lanza una excepción que la aplicación no captura, resultando en un crash no controlado.

#### Estado actual

Los bugs están documentados y **pendientes de corrección** como parte de la próxima iteración del sistema. Su detección mediante pruebas automatizadas demuestra el valor de diseñar casos que ataquen los supuestos implícitos de la implementación, no solo el flujo feliz.

## 6. Uso de IA en el proyecto

### 6.1 Herramientas utilizadas

- Asistente de IA conversacional integrado al entorno de desarrollo.

### 6.2 Para qué fueron usadas

- Generación y mejora de borradores del análisis de requerimientos.
- Redacción y ajuste de secciones del informe técnico.
- Apoyo para estructurar casos de prueba y revisar coherencia entre reglas y pruebas.
- Sugerencias de implementación y validación de consistencia general del proyecto.

### 6.3 Decisiones no delegadas a IA y por qué

- Definición final de supuestos del negocio (qué entra y qué queda fuera de alcance).
- Selección final de reglas de negocio que se implementan en el sistema.
- Criterio final sobre qué considerar bug real, su severidad y su priorización.
- Aprobación final del contenido entregado en informe y repositorio.

Estas decisiones no se delegaron completamente porque requieren contexto del curso, criterio técnico del equipo y responsabilidad directa sobre la entrega.

### 6.4 Evaluación crítica del uso de IA

En este proyecto se usó IA de manera intensiva para acelerar análisis, redacción y soporte técnico. Sin embargo, todo lo producido fue revisado por el equipo antes de aceptarlo.

Consideramos que el uso de IA es necesario y útil en la mayoría de los casos para mejorar productividad, pero no reemplaza la responsabilidad profesional. La capacidad de validación del programador sigue siendo indispensable para detectar errores, cuestionar supuestos y asegurar que la solución realmente cumpla el problema planteado.

## 7. Reflexión final

El problema más importante detectado durante el desarrollo fue la validación incorrecta de fechas en la creación de reservas. La fecha futura se validaba comparando strings en vez de objetos de fecha/hora, lo que permitió entradas inválidas que debían rechazarse.

Este problema fue detectado al ejecutar pruebas negativas y disruptivas diseñadas para romper supuestos del sistema (`tests/test_bugs.py`). No se detectó antes porque inicialmente se priorizó el flujo feliz y casos funcionales, sin atacar de forma temprana entradas mal formadas ni errores de integridad referencial.

Como mejora de proceso, el equipo incorporará desde el inicio pruebas negativas y de borde junto con los casos funcionales, y además revisión de validaciones críticas antes de cerrar cada iteración.

La principal limitación actual del sistema es que aún existen bugs de validación e integridad pendientes de corrección, por lo que no está listo para un despliegue productivo sin una iteración adicional de hardening.

La mejora futura prioritaria es robustecer la capa de validación y manejo de errores en reservas (parseo estricto de fecha/hora, validación de IDs y captura controlada de excepciones de base de datos), seguida de una nueva ejecución completa de la suite de pruebas.

## Conclusiones

El proyecto permitió transformar un requerimiento ambiguo en una propuesta concreta, implementable y testeable, mostrando trazabilidad entre decisiones, reglas de negocio, implementación y pruebas. La distinción entre verificación y validación fue aplicada en forma práctica, y la estrategia de pruebas permitió detectar fallos relevantes que no aparecen en escenarios ideales. En síntesis, el resultado evidencia avance técnico y pensamiento crítico, junto con una hoja de ruta clara para estabilizar la solución en la siguiente iteración.