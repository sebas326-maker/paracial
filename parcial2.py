"""
Parcial práctico - Acceso a Datos 2026
Sistema de inventario y ventas (Python + SQLite) - TODO EN UN SOLO ARCHIVO

Ejecutar:
    python inventario.py            -> menú interactivo (crea tienda.db automáticamente)
    python inventario.py --demo     -> demostración del error controlado + rollback()
"""
import sqlite3
import sys

DB_NOMBRE = "tienda.db"


class ErrorNegocio(Exception):
    """Error de validación (producto inexistente, stock insuficiente, etc.)."""


def conectar(ruta=DB_NOMBRE):
    conn = sqlite3.connect(ruta)
    conn.execute("PRAGMA foreign_keys = ON") 
    conn.row_factory = sqlite3.Row
    return conn


def crear_tablas(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS productos (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT    NOT NULL UNIQUE,
            precio    REAL    NOT NULL CHECK (precio >= 0),
            cantidad  INTEGER NOT NULL CHECK (cantidad >= 0)
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id     INTEGER NOT NULL,
            cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
            precio_unitario REAL    NOT NULL,
            total           REAL    NOT NULL,
            fecha           TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
        );
        """
    )
    conn.commit()



def registrar_producto(conn, nombre, precio, cantidad):
    if not nombre.strip():
        raise ErrorNegocio("El nombre no puede estar vacío.")
    if precio < 0 or cantidad < 0:
        raise ErrorNegocio("Precio y cantidad no pueden ser negativos.")
    try:
        cur = conn.execute(
            "INSERT INTO productos (nombre, precio, cantidad) VALUES (?, ?, ?)",
            (nombre.strip(), precio, cantidad),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ErrorNegocio(f"Ya existe un producto llamado '{nombre}'.")


def listar_productos(conn):
    return conn.execute(
        "SELECT id, nombre, precio, cantidad FROM productos ORDER BY id"
    ).fetchall()


def obtener_producto(conn, producto_id):
    return conn.execute(
        "SELECT id, nombre, precio, cantidad FROM productos WHERE id = ?",
        (producto_id,),
    ).fetchone()


def actualizar_producto(conn, producto_id, precio=None, cantidad=None):
    if obtener_producto(conn, producto_id) is None:
        raise ErrorNegocio(f"No existe el producto con id {producto_id}.")
    if precio is not None:
        if precio < 0:
            raise ErrorNegocio("El precio no puede ser negativo.")
        conn.execute("UPDATE productos SET precio = ? WHERE id = ?", (precio, producto_id))
    if cantidad is not None:
        if cantidad < 0:
            raise ErrorNegocio("La cantidad no puede ser negativa.")
        conn.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (cantidad, producto_id))
    conn.commit()


def eliminar_producto(conn, producto_id):
    """Elimina un producto solo si no tiene ventas asociadas (integridad referencial)."""
    if obtener_producto(conn, producto_id) is None:
        raise ErrorNegocio(f"No existe el producto con id {producto_id}.")
    try:
        conn.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ErrorNegocio(
            "No se puede eliminar: el producto tiene ventas registradas en el historial."
        )



def registrar_venta(conn, producto_id, cantidad, simular_error=False):
    """Registra una venta de forma atómica.

    1. Validar que el producto exista.
    2. Validar que haya stock suficiente.
    3. INSERT en ventas.
    4. UPDATE del inventario (descontar unidades).
    5. commit() de ambas operaciones.

    Si ocurre CUALQUIER error entre el paso 3 y el 5 se ejecuta rollback().
    `simular_error=True` lanza una excepción controlada justo después del INSERT
    y antes del UPDATE (reto obligatorio del parcial).
    """
    if cantidad <= 0:
        raise ErrorNegocio("La cantidad a vender debe ser mayor que cero.")

    producto = obtener_producto(conn, producto_id)                     # 1
    if producto is None:
        raise ErrorNegocio(f"No existe el producto con id {producto_id}.")
    if producto["cantidad"] < cantidad:                                # 2
        raise ErrorNegocio(
            f"Stock insuficiente: hay {producto['cantidad']} unidad(es) de "
            f"'{producto['nombre']}' y se pidieron {cantidad}."
        )

    try:
        total = producto["precio"] * cantidad
        cur = conn.execute(                                            # 3
            "INSERT INTO ventas (producto_id, cantidad, precio_unitario, total) "
            "VALUES (?, ?, ?, ?)",
            (producto_id, cantidad, producto["precio"], total),
        )

        if simular_error:
            raise RuntimeError("Error simulado: falla antes de actualizar el inventario")

        conn.execute(                                                  # 4
            "UPDATE productos SET cantidad = cantidad - ? WHERE id = ?",
            (cantidad, producto_id),
        )
        conn.commit()                                                  # 5
        return cur.lastrowid
    except Exception:
        conn.rollback()   
        raise


def historial_ventas(conn):
    return conn.execute(
        """
        SELECT v.id, p.nombre, v.cantidad, v.precio_unitario, v.total, v.fecha
        FROM ventas v
        INNER JOIN productos p ON p.id = v.producto_id
        ORDER BY v.id
        """
    ).fetchall()


def contar_ventas(conn):
    return conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]


MENU = """
========== TIENDA DE COMPONENTES ==========
1. Registrar producto
2. Consultar productos
3. Actualizar precio o cantidad
4. Eliminar producto
5. Registrar venta
6. Historial de ventas
7. Demostración de rollback (error controlado)
0. Salir
==========================================="""


def pedir_float(msg):
    return float(input(msg).replace(",", "."))


def pedir_int(msg):
    return int(input(msg))


def mostrar_productos(conn):
    filas = listar_productos(conn)
    if not filas:
        print("No hay productos registrados.")
        return
    print(f"\n{'ID':<5}{'Nombre':<30}{'Precio':>12}{'Cantidad':>10}")
    print("-" * 57)
    for f in filas:
        print(f"{f['id']:<5}{f['nombre']:<30}{f['precio']:>12.2f}{f['cantidad']:>10}")


def mostrar_historial(conn):
    filas = historial_ventas(conn)
    if not filas:
        print("Aún no hay ventas registradas.")
        return
    print(f"\n{'ID':<5}{'Producto':<28}{'Cant.':>6}{'P.Unit':>11}{'Total':>12}  Fecha")
    print("-" * 80)
    for f in filas:
        print(f"{f['id']:<5}{f['nombre']:<28}{f['cantidad']:>6}"
              f"{f['precio_unitario']:>11.2f}{f['total']:>12.2f}  {f['fecha']}")


def opcion_actualizar(conn):
    mostrar_productos(conn)
    pid = pedir_int("\nID del producto: ")
    print("¿Qué deseas actualizar?  1) Precio  2) Cantidad  3) Ambos")
    op = input("Opción: ").strip()
    precio = pedir_float("Nuevo precio: ") if op in ("1", "3") else None
    cantidad = pedir_int("Nueva cantidad: ") if op in ("2", "3") else None
    if precio is None and cantidad is None:
        print("Opción no válida.")
        return
    actualizar_producto(conn, pid, precio, cantidad)
    print("Producto actualizado.")


def demo_rollback():
    """Error controlado entre el INSERT y el UPDATE; verifica que nada cambie.
    Usa una base en memoria, así no toca tienda.db."""
    def estado(conn, pid, titulo):
        p = obtener_producto(conn, pid)
        print(f"  [{titulo}] stock de '{p['nombre']}': {p['cantidad']} | "
              f"ventas registradas: {contar_ventas(conn)}")

    conn = conectar(":memory:")
    crear_tablas(conn)
    pid = registrar_producto(conn, "Arduino UNO R3", 85000, 10)

    print("\n1) Estado inicial")
    estado(conn, pid, "ANTES")

    print("\n2) Venta con error simulado (falla entre el INSERT y el UPDATE)")
    try:
        registrar_venta(conn, pid, 3, simular_error=True)
    except RuntimeError as e:
        print(f"  Excepción capturada: {e}")
        print("  -> se ejecutó rollback()")

    print("\n3) Verificación: los datos deben seguir intactos")
    estado(conn, pid, "DESPUÉS")
    assert obtener_producto(conn, pid)["cantidad"] == 10
    assert contar_ventas(conn) == 0
    print("  OK: no quedó venta huérfana y el inventario no cambió.")

    print("\n4) Venta normal (sin error) para comparar")
    registrar_venta(conn, pid, 3)
    estado(conn, pid, "VENTA OK")
    assert obtener_producto(conn, pid)["cantidad"] == 7
    assert contar_ventas(conn) == 1
    print("  OK: venta + descuento confirmados con commit().")
    conn.close()


def main():
    if "--demo" in sys.argv:
        demo_rollback()
        return

    conn = conectar()
    crear_tablas(conn)
    while True:
        print(MENU)
        op = input("Elige una opción: ").strip()
        try:
            if op == "1":
                nombre = input("Nombre: ")
                precio = pedir_float("Precio: ")
                cantidad = pedir_int("Cantidad disponible: ")
                pid = registrar_producto(conn, nombre, precio, cantidad)
                print(f"Producto registrado con id {pid}.")
            elif op == "2":
                mostrar_productos(conn)
            elif op == "3":
                opcion_actualizar(conn)
            elif op == "4":
                mostrar_productos(conn)
                eliminar_producto(conn, pedir_int("\nID a eliminar: "))
                print("Producto eliminado.")
            elif op == "5":
                mostrar_productos(conn)
                pid = pedir_int("\nID del producto a vender: ")
                cant = pedir_int("Cantidad: ")
                vid = registrar_venta(conn, pid, cant)
                print(f"Venta #{vid} registrada e inventario actualizado.")
            elif op == "6":
                mostrar_historial(conn)
            elif op == "7":
                demo_rollback()
            elif op == "0":
                print("Hasta luego.")
                break
            else:
                print("Opción no válida.")
        except ErrorNegocio as e:
            print(f"[!] {e}")
        except ValueError:
            print("[!] Entrada numérica inválida.")
        except EOFError:
            break
    conn.close()


if __name__ == "__main__":
    main()
