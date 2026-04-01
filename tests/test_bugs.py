"""
Tests orientados a encontrar fallos reales en la implementacion.
Ejecutar: python -X utf8 tests/test_bugs.py
"""
import sys, os, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
import database
database.DB_PATH = _tmp_db.name

from app import app
from database import init_db, get_db

results = []

def record(case_id, name, category, expected, actual_ok, actual_msg, bug_desc=None):
    status = "PASS" if actual_ok else "FAIL"
    results.append({
        "id": case_id, "name": name, "category": category,
        "expected": expected, "actual": actual_msg,
        "status": status, "bug": bug_desc
    })
    mark = "+" if actual_ok else "X"
    print(f"  [{mark}] {case_id} - {name}")
    if not actual_ok and bug_desc:
        print(f"       >> BUG: {bug_desc}")


class TestBugs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        init_db()
        cls.c = app.test_client()
        cls.c.post("/clientes", data={"nombre": "Ana Torres", "telefono": "+56912345678", "email": "ana@test.cl"})
        cls.c.post("/tecnicos", data={"nombre": "Carlos Rojo", "especialidad": "refrigeracion"})

    # ── VALIDACION DE TELEFONO ──────────────────────────────────────────

    def test_V01_telefono_solo_guiones(self):
        """'-------' (7 guiones) no contiene ningun digito; debe rechazarse."""
        r = self.c.post("/clientes", data={
            "nombre": "Test Guion", "telefono": "-------", "email": "guion@test.cl"
        }, follow_redirects=True)
        ok = b"correctamente" not in r.data
        record("CP-V01", "Telefono con solo guiones es rechazado",
               "Validacion",
               "Flash de error (no es un numero valido)",
               ok, "Rechazado correctamente" if ok else "ACEPTADO sin digitos",
               bug_desc="valid_phone acepta '-------': regex permite guiones sin exigir al menos un digito")

    def test_V02_telefono_solo_espacios(self):
        """'       ' (7 espacios) no es un numero de telefono valido."""
        r = self.c.post("/clientes", data={
            "nombre": "Test Espacios", "telefono": "       ", "email": "espacio@test.cl"
        }, follow_redirects=True)
        ok = b"correctamente" not in r.data
        record("CP-V02", "Telefono con solo espacios es rechazado",
               "Validacion",
               "Flash de error",
               ok, "Rechazado" if ok else "ACEPTADO sin digitos",
               bug_desc="valid_phone acepta cadena de solo espacios si tiene 7-15 chars")

    def test_V03_telefono_muy_corto(self):
        """Telefono de 6 digitos (bajo el minimo de 7) debe rechazarse."""
        r = self.c.post("/clientes", data={
            "nombre": "Test Corto", "telefono": "123456", "email": "corto@test.cl"
        }, follow_redirects=True)
        ok = b"correctamente" not in r.data
        record("CP-V03", "Telefono de 6 digitos (bajo minimo) es rechazado",
               "Validacion",
               "Flash de error por longitud insuficiente",
               ok, "Rechazado" if ok else "Aceptado incorrectamente")

    def test_V04_telefono_con_letras(self):
        """Telefono con letras alfabeticas debe rechazarse."""
        r = self.c.post("/clientes", data={
            "nombre": "Test Letras", "telefono": "9abc12345", "email": "letras@test.cl"
        }, follow_redirects=True)
        ok = b"correctamente" not in r.data
        record("CP-V04", "Telefono con letras es rechazado",
               "Validacion",
               "Flash de error",
               ok, "Rechazado" if ok else "Aceptado incorrectamente")

    # ── VALIDACION DE FECHA/HORA ────────────────────────────────────────

    def test_F01_fecha_formato_invalido(self):
        """'not-a-date' pasa la comparacion de strings porque 'n' > '2'.
        El sistema deberia rechazarlo pero lo acepta y lo almacena."""
        r = self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "1",
            "fecha_hora": "not-a-date",
            "direccion": "Dir invalida", "descripcion": "Fecha invalida"
        }, follow_redirects=True)
        ok = b"correctamente" not in r.data
        record("CP-F01", "Fecha con formato invalido 'not-a-date' es rechazada",
               "Validacion",
               "Flash de error de formato de fecha",
               ok, "Rechazado" if ok else "ACEPTADO con fecha invalida",
               bug_desc="Comparacion de strings: 'not-a-date' > '2026-...' => pasa la validacion de fecha futura")

    def test_F02_fecha_solo_dia_sin_hora(self):
        """'2099-01-01' (sin hora) pasa la comparacion de strings y se almacena."""
        r = self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "1",
            "fecha_hora": "2099-01-01",
            "direccion": "Dir sin hora", "descripcion": "Sin hora"
        }, follow_redirects=True)
        ok = b"correctamente" not in r.data
        record("CP-F02", "Fecha sin hora '2099-01-01' es rechazada",
               "Validacion",
               "Flash de error por formato incompleto",
               ok, "Rechazado" if ok else "ACEPTADO con formato incompleto",
               bug_desc="El campo se almacena como '2099-01-01' sin hora, rompiendo la comparacion de solapamiento")

    def test_F03_fecha_zzz_lexicograficamente_mayor(self):
        """'zzz-zzz' pasa cualquier comparacion lexicografica con fechas ISO."""
        r = self.c.post("/reservas/nueva", data={
            "cliente_id": "1", "tecnico_id": "1",
            "fecha_hora": "zzz-zzz",
            "direccion": "Dir zzz", "descripcion": "Fecha zzz"
        }, follow_redirects=True)
        ok = b"correctamente" not in r.data
        record("CP-F03", "Cadena 'zzz-zzz' no se acepta como fecha",
               "Validacion",
               "Flash de error",
               ok, "Rechazado" if ok else "ACEPTADO string arbitrario como fecha",
               bug_desc="Cualquier string > '2026' en orden ASCII pasa la validacion de fecha futura")

    # ── INTEGRIDAD REFERENCIAL ──────────────────────────────────────────

    def test_R01_reserva_con_cliente_inexistente(self):
        """cliente_id=9999 no existe; el FK debe bloquearlo.
        Si no se maneja, la app lanza excepcion no capturada."""
        try:
            r = self.c.post("/reservas/nueva", data={
                "cliente_id": "9999", "tecnico_id": "1",
                "fecha_hora": "2099-06-01T10:00",
                "direccion": "Dir FK", "descripcion": "FK cliente"
            }, follow_redirects=True)
            ok = r.status_code != 500 and b"correctamente" not in r.data
            msg = f"status={r.status_code}" if ok else f"CRASH HTTP 500"
        except Exception as e:
            ok = False
            msg = f"EXCEPCION NO CAPTURADA: {type(e).__name__}: {e}"
        record("CP-R01", "Reserva con cliente_id inexistente muestra error controlado (no crash)",
               "Integridad",
               "Flash de error sin crash",
               ok, msg if ok else msg,
               bug_desc="IntegrityError de FK no capturado: la app lanza excepcion en lugar de mostrar error")

    def test_R02_reserva_con_tecnico_inexistente(self):
        """tecnico_id=9999 no existe; mismo problema de FK sin manejo."""
        try:
            r = self.c.post("/reservas/nueva", data={
                "cliente_id": "1", "tecnico_id": "9999",
                "fecha_hora": "2099-06-02T10:00",
                "direccion": "Dir FK tec", "descripcion": "FK tecnico"
            }, follow_redirects=True)
            ok = r.status_code != 500 and b"correctamente" not in r.data
            msg = f"status={r.status_code}" if ok else f"CRASH HTTP 500"
        except Exception as e:
            ok = False
            msg = f"EXCEPCION NO CAPTURADA: {type(e).__name__}: {e}"
        record("CP-R02", "Reserva con tecnico_id inexistente muestra error controlado (no crash)",
               "Integridad",
               "Flash de error sin crash",
               ok, msg if ok else msg,
               bug_desc="IntegrityError de FK no capturado: excepcion no manejada")

    def test_R03_cliente_id_no_numerico(self):
        """cliente_id='abc' — el sistema no valida que sea entero."""
        try:
            r = self.c.post("/reservas/nueva", data={
                "cliente_id": "abc", "tecnico_id": "1",
                "fecha_hora": "2099-06-03T10:00",
                "direccion": "Dir abc", "descripcion": "ID no numerico"
            }, follow_redirects=True)
            ok = r.status_code != 500 and b"correctamente" not in r.data
            msg = f"status={r.status_code}" if ok else f"CRASH HTTP 500"
        except Exception as e:
            ok = False
            msg = f"EXCEPCION NO CAPTURADA: {type(e).__name__}: {e}"
        record("CP-R03", "cliente_id no numerico ('abc') no produce crash",
               "Integridad",
               "Error controlado sin crash",
               ok, msg if ok else msg,
               bug_desc="El valor 'abc' se pasa al INSERT sin validacion de tipo entero")

    # ── DUPLICADOS / ESTADO ─────────────────────────────────────────────

    def test_D01_email_duplicado_case_insensitive(self):
        """Registrar 'ANA@TEST.CL' cuando ya existe 'ana@test.cl' debe rechazarse."""
        r = self.c.post("/clientes", data={
            "nombre": "Ana Duplicada", "telefono": "912345678", "email": "ANA@TEST.CL"
        }, follow_redirects=True)
        ok = b"Ya existe" in r.data
        record("CP-D01", "Email duplicado en mayusculas es detectado como duplicado",
               "Duplicados",
               "Flash 'Ya existe un cliente' (email se normaliza a minusculas)",
               ok, "Duplicado detectado" if ok else "ACEPTADO como nuevo cliente (email case no normalizado)")

    def test_D02_tecnico_nombre_duplicado_permitido(self):
        """El sistema permite dos tecnicos con el mismo nombre (diferente persona).
        Verificar que esto es intencional y no genera confusion."""
        r = self.c.post("/tecnicos", data={
            "nombre": "Carlos Rojo", "especialidad": "hornos"
        }, follow_redirects=True)
        ok = b"correctamente" in r.data
        db = get_db()
        count = db.execute("SELECT COUNT(*) FROM tecnicos WHERE nombre='Carlos Rojo'").fetchone()[0]
        db.close()
        ok = ok and count == 2
        record("CP-D02", "Se permiten dos tecnicos con el mismo nombre (distinta especialidad)",
               "Duplicados",
               "Ambos registros existen en BD (comportamiento intencional documentado)",
               ok, f"count={count} tecnicos con ese nombre" if ok else "Fallo inesperado")

    # ── COMPORTAMIENTO LIMITE ───────────────────────────────────────────

    def test_L01_multiples_errores_simultaneos(self):
        """Enviar nombre vacio, telefono invalido y email invalido a la vez.
        El sistema debe mostrar todos los errores, no solo el primero."""
        r = self.c.post("/clientes", data={
            "nombre": "", "telefono": "abc", "email": "noemail"
        }, follow_redirects=True)
        errores = r.data.count(b"alert error")
        ok = errores >= 2
        record("CP-L01", "Multiples errores simultaneos se muestran todos",
               "Limite",
               "Al menos 2 mensajes de error distintos en la respuesta",
               ok, f"{errores} mensajes de error mostrados" if ok else f"Solo {errores} error mostrado",
               bug_desc=None if ok else "El sistema solo muestra el primer error y detiene la validacion")

    def test_L02_cancelar_reserva_pasada(self):
        """Una reserva que ya vencio (pasado) aun puede cancelarse.
        El sistema no debe impedirlo (no tiene restriccion de tiempo para cancelar)."""
        # Insertar directamente en BD una reserva con fecha pasada
        db = get_db()
        db.execute("""
            INSERT INTO reservas (cliente_id, tecnico_id, fecha_hora, direccion, descripcion, estado)
            VALUES (1, 1, '2020-01-01T10:00', 'Dir pasada', 'Reserva pasada', 'pendiente')
        """)
        db.commit()
        row = db.execute("SELECT id FROM reservas WHERE descripcion='Reserva pasada'").fetchone()
        db.close()
        rid = row["id"]
        r = self.c.post(f"/reservas/{rid}/cancelar", data={"motivo": "atraso"}, follow_redirects=True)
        ok = b"cancelada" in r.data.lower()
        record("CP-L02", "Reserva con fecha pasada puede cancelarse",
               "Limite",
               "Sistema permite cancelar reservas vencidas (no hay restriccion temporal en cancelacion)",
               ok, "Cancelacion permitida" if ok else "Cancelacion bloqueada incorrectamente")

    @classmethod
    def tearDownClass(cls):
        os.unlink(_tmp_db.name)


def run():
    order = [
        "test_V01_telefono_solo_guiones",
        "test_V02_telefono_solo_espacios",
        "test_V03_telefono_muy_corto",
        "test_V04_telefono_con_letras",
        "test_F01_fecha_formato_invalido",
        "test_F02_fecha_solo_dia_sin_hora",
        "test_F03_fecha_zzz_lexicograficamente_mayor",
        "test_R01_reserva_con_cliente_inexistente",
        "test_R02_reserva_con_tecnico_inexistente",
        "test_R03_cliente_id_no_numerico",
        "test_D01_email_duplicado_case_insensitive",
        "test_D02_tecnico_nombre_duplicado_permitido",
        "test_L01_multiples_errores_simultaneos",
        "test_L02_cancelar_reserva_pasada",
    ]
    labels = {
        "V": "Validacion de campos",
        "F": "Validacion de fecha",
        "R": "Integridad referencial",
        "D": "Duplicados",
        "L": "Comportamiento limite",
    }

    sep = "=" * 65
    print(sep)
    print("  TESTS DE DETECCION DE BUGS — SISTEMA DE RESERVAS")
    print(sep)

    suite = unittest.TestSuite()
    cur = None
    for name in order:
        cat = name[5]
        if cat != cur:
            cur = cat
            print(f"\n  [{labels.get(cat, cat)}]")
        suite.addTest(TestBugs(name))

    runner = unittest.TextTestRunner(stream=open(os.devnull, "w"), verbosity=0)
    runner.run(suite)

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = [r for r in results if r["status"] == "FAIL"]

    print(f"\n{sep}")
    print("  RESUMEN")
    print(sep)
    print(f"  TOTAL  {passed}/{len(results)} pasados  |  {len(failed)} BUGS encontrados")
    print(sep)

    if failed:
        print("\n  BUGS DETECTADOS:")
        for r in failed:
            print(f"\n  [{r['id']}] {r['name']}")
            if r["bug"]:
                print(f"   Causa : {r['bug']}")
            print(f"   Esperado : {r['expected']}")
            print(f"   Obtenido : {r['actual']}")


if __name__ == "__main__":
    run()
