# Sistema de Reservas de Atención Técnica

Aplicación web para gestionar reservas de servicio técnico de electrodomésticos.

## Requisitos

- Python 3.10 o superior

## Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd pruebas-de-software

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
cd app
python app.py
```

La aplicación estará disponible en: http://127.0.0.1:5000

## Funcionalidades

| Ruta | Descripción |
|---|---|
| `/` | Lista de reservas futuras pendientes |
| `/clientes` | Registro y listado de clientes |
| `/tecnicos` | Registro y listado de técnicos |
| `/reservas/nueva` | Crear una nueva reserva |
| `/reservas/<id>/cancelar` | Cancelar una reserva existente |

## Base de datos

SQLite, archivo `app/reservas.db` (se crea automáticamente al iniciar).

## Tecnologías

- Python 3 + Flask
- SQLite (via módulo `sqlite3` estándar)
- HTML + CSS (sin frameworks externos)
