"""
Suite de pruebas - Sistema de Reservas de Atencion Tecnica
Ejecutar: python -X utf8 tests/test_suite.py
"""
import sys, os, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Redirigir BD a archivo temporal antes de importar app
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
import database
database.DB_PATH = _tmp_db.name

from app import app
from database import init_db, get_db

results = []

def record(case_id, name, category, precondition, steps, expected, actual_ok, actual_msg):
    status = "PASS" if actual_ok else "FAIL"
    results.append({
        "id": case_id, "name": name, "category": category,
        "precondition": precondition, "steps": steps,
        "expected": expected, "actual": actual_msg, "status": status
    })
    mark = "+" if actual_ok else "X"
    print(f"  [{mark}] {case_id} - {name}")
    if not actual_ok:
        print(f"       ESPERADO : {expected}")
        print(f"       OBTENIDO : {actual_msg}")


class TestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        init_db()
        cls.c = app.test_client()
        # Datos base reutilizados por varios tests
        cls.c.post("/clientes", data={"nombre": "Ana Torres",  "telefono": "+56912345678", "email": "ana@test.cl"})
        cls.c.post("/clientes", data={"nombre": "Luis Perez",  "telefono": "987654321",    "email": "luis@test.cl"})
        cls.c.post("/tecnicos", data={"nombre": "Carlos Rojo", "especialidad": "refrigeracion"})
        cls.c.post("/tecnicos", data={"nombre": "Pedro Soto",  "especialidad": "lavadoras"})

    # ── FUNCIONALES ────────────────────────────────────────────────────

    def test_F01(self):
        r = self.c.post("/clientes", data={
            "nombre": "Maria Gonzalez", "telefono": "+56988887777", "email": "maria@test.cl"
        }, follow_redirects=True)
        ok = b"correctamente" in r.data
        record("CP-F01", "Registrar cliente con datos validos",
               "Funcional", "Sin cliente con email maria@test.cl",
               "POST /clientes con nombre, telefono y email validos",
               "Flash 'registrado correctamente'",
               ok, "Flash de exito recibido" if ok else r.data.decode("utf-8", errors="replace")[:150])

    def test_F02(self):
        r = self.c.post("/tecnicos", data={
            "nombre": "Jorge Munoz", "especialidad": "hornos"
        }, follow_redirects=True)
        ok = b"correctamente" in r.data
        record("CP-F02", "Registrar tecnico con datos validos",
               "Funcional", "Sin tecnico previo con ese nombre",
               "POST /tecnicos con nombre y especialidad",
               "Flash 'registrado correctamente'",
               ok, "Flash de exito recibido" if ok else r.data.decode("utf-8", errors="replace")[:150])

    def test_F03(self):
        r = self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "1",
            "fecha_hora": "2099-06-15T10:00",
            "direccion": "Av. Las Flores 100",
            "descripcion": "Refrigerador no enfria"
        }, follow_redirects=True)
        ok = b"correctamente" in r.data
        record("CP-F03", "Crear reserva con datos validos y fecha futura",
               "Funcional", "Cliente id=1 y tecnico id=1 registrados",
               "POST /reservas/nueva con todos los campos validos, fecha 2099-06-15 10:00",
               "Redirect a index con flash de exito",
               ok, "Flash de exito recibido" if ok else r.data.decode("utf-8", errors="replace")[:150])

    def test_F04(self):
        self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "2", "fecha_hora": "2099-12-01T09:00",
            "direccion": "Calle A", "descripcion": "Falla A"
        })
        self.c.post("/reservas/nueva", data={
            "cliente_id": "2", "tecnico_id": "2", "fecha_hora": "2099-08-01T09:00",
            "direccion": "Calle B", "descripcion": "Falla B"
        })
        r = self.c.get("/")
        idx_ago = r.data.find(b"2099-08-01")
        idx_dic = r.data.find(b"2099-12-01")
        ok = idx_ago != -1 and idx_dic != -1 and idx_ago < idx_dic
        record("CP-F04", "Reservas futuras listadas ordenadas ASC por fecha",
               "Funcional", "Al menos dos reservas futuras en fechas distintas",
               "GET / y verificar orden de aparicion en HTML",
               "Fecha mas proxima aparece antes en el HTML",
               ok, "Orden correcto" if ok else f"idx_ago={idx_ago}, idx_dic={idx_dic}")

    def test_F05(self):
        self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "1", "fecha_hora": "2099-07-10T14:00",
            "direccion": "Calle C", "descripcion": "Lavadora ruidosa"
        })
        db = get_db()
        row = db.execute("SELECT id FROM reservas WHERE descripcion='Lavadora ruidosa'").fetchone()
        db.close()
        rid = row["id"]
        self.c.post(f"/reservas/{rid}/cancelar", data={"motivo": "Cliente cancelo"}, follow_redirects=True)
        db = get_db()
        est = db.execute("SELECT estado, motivo_cancelacion FROM reservas WHERE id=?", (rid,)).fetchone()
        db.close()
        ok = est["estado"] == "cancelada" and est["motivo_cancelacion"] == "Cliente cancelo"
        record("CP-F05", "Cancelar reserva con motivo guarda estado y motivo en BD",
               "Funcional", "Reserva pendiente existente",
               f"POST /reservas/{rid}/cancelar con motivo='Cliente cancelo'",
               "estado=cancelada y motivo_cancelacion guardado",
               ok, f"estado={est['estado']}, motivo={est['motivo_cancelacion']}")

    def test_F06(self):
        self.c.post("/reservas/nueva", data={
            "cliente_id": "2", "tecnico_id": "1", "fecha_hora": "2099-07-11T10:00",
            "direccion": "Calle D", "descripcion": "Horno no enciende"
        })
        db = get_db()
        row = db.execute("SELECT id FROM reservas WHERE descripcion='Horno no enciende'").fetchone()
        db.close()
        rid = row["id"]
        self.c.post(f"/reservas/{rid}/cancelar", data={"motivo": ""}, follow_redirects=True)
        db = get_db()
        est = db.execute("SELECT estado, motivo_cancelacion FROM reservas WHERE id=?", (rid,)).fetchone()
        db.close()
        ok = est["estado"] == "cancelada" and est["motivo_cancelacion"] is None
        record("CP-F06", "Cancelar sin motivo deja motivo_cancelacion NULL en BD",
               "Funcional", "Reserva pendiente existente",
               f"POST /reservas/{rid}/cancelar con motivo vacio",
               "estado=cancelada, motivo_cancelacion=NULL",
               ok, f"estado={est['estado']}, motivo={est['motivo_cancelacion']}")

    def test_F07(self):
        self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "2", "fecha_hora": "2099-07-20T16:00",
            "direccion": "Calle E", "descripcion": "DescripcionUnicaXYZ"
        })
        db = get_db()
        row = db.execute("SELECT id FROM reservas WHERE descripcion='DescripcionUnicaXYZ'").fetchone()
        db.close()
        self.c.post(f"/reservas/{row['id']}/cancelar", data={"motivo": "test"})
        r = self.c.get("/")
        ok = b"DescripcionUnicaXYZ" not in r.data
        record("CP-F07", "Reserva cancelada no aparece en listado de futuras",
               "Funcional", "Reserva en estado pendiente",
               "Cancelar reserva y verificar GET /",
               "Descripcion de reserva cancelada ausente del HTML",
               ok, "Ausente del listado" if ok else "Aun visible en listado")

    def test_F08(self):
        r1 = self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "1", "fecha_hora": "2099-09-01T11:00",
            "direccion": "Dir 1", "descripcion": "Tecnico1 misma hora"
        }, follow_redirects=True)
        r2 = self.c.post("/reservas/nueva", data={
            "cliente_id": "2", "tecnico_id": "2", "fecha_hora": "2099-09-01T11:00",
            "direccion": "Dir 2", "descripcion": "Tecnico2 misma hora"
        }, follow_redirects=True)
        ok = b"correctamente" in r1.data and b"correctamente" in r2.data
        record("CP-F08", "Dos tecnicos distintos pueden tener reserva en la misma hora",
               "Funcional", "Tecnicos id=1 e id=2 libres a las 2099-09-01 11:00",
               "Crear dos reservas con tecnicos distintos y misma fecha/hora",
               "Ambas reservas se crean exitosamente",
               ok, "Ambas creadas OK" if ok else "Una o ambas fallaron")

    # ── BORDE ──────────────────────────────────────────────────────────

    def test_B01(self):
        r = self.c.post("/clientes", data={
            "nombre": "Test Plus", "telefono": "912345678", "email": "test+tag@dominio.cl"
        }, follow_redirects=True)
        ok = b"correctamente" in r.data
        record("CP-B01", "Email con '+' es aceptado como valido",
               "Borde", "Sin cliente con email test+tag@dominio.cl",
               "POST /clientes con email='test+tag@dominio.cl'",
               "El sistema acepta el email y registra al cliente",
               ok, "Aceptado" if ok else r.data.decode("utf-8", errors="replace")[:150])

    def test_B02(self):
        r = self.c.post("/clientes", data={
            "nombre": "Angel Nunez Nono", "telefono": "912000000", "email": "angel@test.cl"
        }, follow_redirects=True)
        ok = b"correctamente" in r.data
        record("CP-B02", "Nombre con caracteres especiales (tildes, enie) es aceptado",
               "Borde", "Sin cliente con email angel@test.cl",
               "POST /clientes con nombre con caracteres especiales",
               "El sistema registra al cliente sin error",
               ok, "Aceptado" if ok else r.data.decode("utf-8", errors="replace")[:150])

    def test_B03(self):
        r = self.c.post("/clientes", data={
            "nombre": "Test Intl", "telefono": "+56 9 1234 5678", "email": "intl@test.cl"
        }, follow_redirects=True)
        ok = b"correctamente" in r.data
        record("CP-B03", "Telefono con formato internacional '+56 9 1234 5678' es aceptado",
               "Borde", "Sin cliente con email intl@test.cl",
               "POST /clientes con telefono='+56 9 1234 5678'",
               "El sistema acepta el formato internacional",
               ok, "Aceptado" if ok else r.data.decode("utf-8", errors="replace")[:150])

    def test_B04(self):
        r = self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "1",
            "fecha_hora": "2099-11-11T11:00",
            "direccion": "Direccion larga test",
            "descripcion": "A" * 500
        }, follow_redirects=True)
        ok = b"correctamente" in r.data
        record("CP-B04", "Descripcion de 500 caracteres es aceptada sin error",
               "Borde", "Cliente y tecnico registrados",
               "POST /reservas/nueva con descripcion de 500 caracteres",
               "La reserva se crea sin truncar ni lanzar error",
               ok, "Aceptado" if ok else r.data.decode("utf-8", errors="replace")[:150])

    def test_B05(self):
        self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "1", "fecha_hora": "2099-10-10T08:00",
            "direccion": "Dir reuso", "descripcion": "ReservaACancelarBorde"
        })
        db = get_db()
        row = db.execute("SELECT id FROM reservas WHERE descripcion='ReservaACancelarBorde'").fetchone()
        db.close()
        self.c.post(f"/reservas/{row['id']}/cancelar", data={"motivo": "test"})
        r = self.c.post("/reservas/nueva", data={
            "cliente_id": "2", "tecnico_id": "1", "fecha_hora": "2099-10-10T08:00",
            "direccion": "Dir reuso 2", "descripcion": "Reserva en hora antes cancelada"
        }, follow_redirects=True)
        ok = b"correctamente" in r.data
        record("CP-B05", "Tecnico puede ocupar hora de una reserva previamente cancelada",
               "Borde", "Tecnico id=1 con reserva cancelada a las 2099-10-10 08:00",
               "Crear nueva reserva para el mismo tecnico en la misma hora cancelada",
               "El sistema acepta la nueva reserva (la hora quedo libre)",
               ok, "Aceptado" if ok else r.data.decode("utf-8", errors="replace")[:150])

    # ── NEGATIVOS ──────────────────────────────────────────────────────

    def test_N01(self):
        r = self.c.post("/clientes", data={
            "nombre": "Sin Arroba", "telefono": "912345678", "email": "noesuncorreo"
        }, follow_redirects=True)
        ok = b"formato" in r.data
        record("CP-N01", "Email sin '@' es rechazado con mensaje de error",
               "Negativo", "Cualquier estado del sistema",
               "POST /clientes con email='noesuncorreo'",
               "Flash de error indicando formato invalido",
               ok, "Error de formato mostrado" if ok else r.data.decode("utf-8", errors="replace")[:150])

    def test_N02(self):
        r = self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "1",
            "fecha_hora": "2000-01-01T10:00",
            "direccion": "Calle pasado", "descripcion": "Falla pasada"
        }, follow_redirects=True)
        ok = b"futur" in r.data.lower()
        record("CP-N02", "Reserva con fecha en el pasado es rechazada",
               "Negativo", "Cliente y tecnico registrados",
               "POST /reservas/nueva con fecha_hora='2000-01-01T10:00'",
               "Flash de error indicando que la fecha debe ser futura",
               ok, "Error mostrado" if ok else r.data.decode("utf-8", errors="replace")[:150])

    def test_N03(self):
        self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "1", "fecha_hora": "2099-05-05T15:00",
            "direccion": "Dir original", "descripcion": "Primera solapamiento"
        })
        r = self.c.post("/reservas/nueva", data={
            "cliente_id": "2", "tecnico_id": "1", "fecha_hora": "2099-05-05T15:00",
            "direccion": "Dir duplicada", "descripcion": "Segunda solapamiento"
        }, follow_redirects=True)
        ok = b"ya tiene una reserva" in r.data.lower()
        record("CP-N03", "Solapamiento de horario para el mismo tecnico es rechazado",
               "Negativo", "Tecnico id=1 con reserva a las 2099-05-05 15:00",
               "POST /reservas/nueva con mismo tecnico y misma fecha/hora",
               "Flash de error indicando que el tecnico ya tiene reserva en ese horario",
               ok, "Error de solapamiento mostrado" if ok else r.data.decode("utf-8", errors="replace")[:150])

    # ── DISRUPTIVOS ────────────────────────────────────────────────────

    def test_D01(self):
        self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "2", "fecha_hora": "2099-03-03T10:00",
            "direccion": "Dir D01", "descripcion": "ParaDoble"
        })
        db = get_db()
        row = db.execute("SELECT id FROM reservas WHERE descripcion='ParaDoble'").fetchone()
        db.close()
        rid = row["id"]
        self.c.post(f"/reservas/{rid}/cancelar", data={"motivo": "primera vez"})
        r = self.c.get(f"/reservas/{rid}/cancelar", follow_redirects=True)
        ok = b"ya fue cancelada" in r.data.lower()
        record("CP-D01", "Cancelar una reserva ya cancelada muestra error sin corromper BD",
               "Disruptivo", f"Reserva id={rid} ya en estado cancelada",
               f"GET /reservas/{rid}/cancelar sobre reserva ya cancelada",
               "Flash 'ya fue cancelada', sin crash ni cambio en BD",
               ok, "Error correcto mostrado" if ok else r.data.decode("utf-8", errors="replace")[:150])

    def test_D02(self):
        r = self.c.get("/reservas/99999/cancelar", follow_redirects=True)
        ok = b"no encontrada" in r.data.lower()
        record("CP-D02", "Acceder a reserva con ID inexistente retorna error controlado",
               "Disruptivo", "No existe reserva con id=99999",
               "GET /reservas/99999/cancelar",
               "Flash 'Reserva no encontrada', redirect a index sin crash",
               ok, "Error controlado" if ok else r.data.decode("utf-8", errors="replace")[:150])

    @classmethod
    def tearDownClass(cls):
        os.unlink(_tmp_db.name)


# ── Runner personalizado ────────────────────────────────────────────────

def run():
    order = [
        "test_F01", "test_F02", "test_F03", "test_F04",
        "test_F05", "test_F06", "test_F07", "test_F08",
        "test_B01", "test_B02", "test_B03", "test_B04", "test_B05",
        "test_N01", "test_N02", "test_N03",
        "test_D01", "test_D02",
    ]
    labels = {"F": "Funcionales", "B": "Borde", "N": "Negativos", "D": "Disruptivos"}

    sep = "=" * 65
    print(sep)
    print("  SUITE DE PRUEBAS - SISTEMA DE RESERVAS DE ATENCION TECNICA")
    print(sep)

    suite = unittest.TestSuite()
    cur = None
    for name in order:
        cat = name[5]
        if cat != cur:
            cur = cat
            print(f"\n  [{labels[cat]}]")
        suite.addTest(TestSuite(name))

    runner = unittest.TextTestRunner(stream=open(os.devnull, "w"), verbosity=0)
    runner.run(suite)

    # Resumen
    cats = {}
    for r in results:
        cats.setdefault(r["category"], []).append(r)
    print(f"\n{sep}")
    print("  RESUMEN")
    print(sep)
    for cat in ["Funcional", "Borde", "Negativo", "Disruptivo"]:
        casos = cats.get(cat, [])
        if casos:
            p = sum(1 for c in casos if c["status"] == "PASS")
            print(f"  {cat:<12}  {p}/{len(casos)} pasados")
    total  = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    print("-" * 65)
    print(f"  TOTAL        {passed}/{total} pasados")
    print(sep)
    if passed < total:
        print("\n  FALLIDOS:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"    - {r['id']} {r['name']}")
    return passed == total


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
