import json
import os


class Transaccion:
    def __init__(self, id, titular, valor, hora, pais, dispositivo_conocido):
        if not titular.strip():
            raise ValueError("El titular no puede estar vacío")

        if valor <= 0:
            raise ValueError("El valor debe ser mayor que cero")

        if hora < 0 or hora > 23:
            raise ValueError("La hora debe estar entre 0 y 23")

        if not pais.strip():
            raise ValueError("El país no puede estar vacío")

        if not isinstance(dispositivo_conocido, bool):
            raise ValueError("dispositivo_conocido debe ser True o False")

        self.id = id
        self.titular = titular
        self.valor = valor
        self.hora = hora
        self.pais = pais
        self.dispositivo_conocido = dispositivo_conocido
        self.puntaje_riesgo = self.calcular_riesgo()
        self.clasificacion = self.clasificar()

    def calcular_riesgo(self):
        puntaje = 0

        if self.valor >= 2000000:
            puntaje += 30

        if 0 <= self.hora <= 5:
            puntaje += 20

        if self.pais.strip().lower() != "colombia":
            puntaje += 25

        if self.dispositivo_conocido is False:
            puntaje += 30

        self.puntaje_riesgo = puntaje
        return puntaje

    def clasificar(self):
        if self.puntaje_riesgo <= 29:
            return "NORMAL"
        elif self.puntaje_riesgo <= 59:
            return "SOSPECHOSA"
        else:
            return "ALTO RIESGO"

    def to_dict(self):
        return {
            "id": self.id,
            "titular": self.titular,
            "valor": self.valor,
            "hora": self.hora,
            "pais": self.pais,
            "dispositivo_conocido": self.dispositivo_conocido,
            "puntaje_riesgo": self.puntaje_riesgo,
            "clasificacion": self.clasificacion
        }

    @classmethod
    def from_dict(cls, datos):
        return cls(
            datos["id"],
            datos["titular"],
            datos["valor"],
            datos["hora"],
            datos["pais"],
            datos["dispositivo_conocido"]
        )


def cargar_transacciones():
    if os.path.exists("transacciones.json"):
        with open("transacciones.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        return [Transaccion.from_dict(dato) for dato in datos]

    return []


def guardar_transacciones(transacciones):
    datos = [transaccion.to_dict() for transaccion in transacciones]

    with open("transacciones.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


transacciones = cargar_transacciones()

try:
    caso1 = Transaccion(
        1,
        "Laura Gómez",
        3500000,
        2,
        "Colombia",
        False
    )

    caso2 = Transaccion(
        2,
        "Carlos Pérez",
        500000,
        14,
        "Colombia",
        True
    )

    caso3 = Transaccion(
        3,
        "Ana Torres",
        2500000,
        10,
        "Perú",
        True
    )

    transacciones.extend([caso1, caso2, caso3])

    for transaccion in [caso1, caso2, caso3]:
        print("ID:", transaccion.id)
        print("Titular:", transaccion.titular)
        print("Puntaje de riesgo:", transaccion.puntaje_riesgo)
        print("Clasificación:", transaccion.clasificacion)
        print("-------------------------")

    guardar_transacciones(transacciones)

except ValueError as error:
    print("Error:", error)