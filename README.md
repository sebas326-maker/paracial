# Parcial — Detector de Transmisiones Sospechosas

Nombre:  Sebastian Andres Mercado Vega
Grupo: 4E

## 1. ¿Qué debe hacer el programa?

Escriba en máximo 3 o 4 líneas cuál es el objetivo del programa.

Respuesta:Sera un un programa que registrara y analizara transacciones marcando el nivel de riesgo de las 
mismas asi evitando fraudes o cualquier situacion que se contemple sopechosa generando 
un informe detllado de las transacciones y su nivel de riego.
---

## 2. Clase `Transmision`

La clase tendrá los siguientes atributos:

- `id`:
- `titular`:
- `valor`:
- `hora`:
- `pais`:
- `dispositivo_conocido`:

Escriba brevemente qué representa cada uno.
 el id es el numero unico generado para la transaccion
 el titular es el nombre del dueño de la transaccion
 el valor es el de la transccion
 la hora es a la que se hace la transaccion
 el pais es el origen de la transaccion
 el dispoditivo llevara el valor si es conocido o desconociso para el programa
---

## 3. Métodos

### `calcular_riesgo()`

Responsabilidad: calcula el riesgo de la transacion.

### `clasificar()`

Responsabilidad: clasifica el riesgo segun el valor del puntaje.

### `to_dict()`

Responsabilidad: Convierte el objeto Transaccion en un diccionario que pueda guardarse en JSON.

### `from_dict()`

Responsabilidad: Recibe un diccionario leído desde JSON y retorna un objeto.

---

## 4. Algoritmo de análisis

Complete el siguiente pseudocódigo:

```text
puntaje = 0

SI la condicion contiene Valor mayor o igual a $2.000.000	
    sumar +30 puntos

SI la condicion contiene Hora entre 0 y 5
    sumar +20 puntos

SI la condicion contiene País diferente de Colombia
    sumar +25 puntos
SI la condicion contiene Dispositivo NO conocido	
    sumar +30 puntos


```

---

## 5. Persistencia

Explique brevemente qué ocurre al iniciar el programa:

```text
JSON
 ↓
lista o diccionario 
 ↓
from_dict()
```

Explique qué ocurre al guardar:

```text
Objetos
 ↓
to_dict()

 ↓
JSON
```

---

## 6. Menú

Indique qué debe hacer cada opción:

### Opción 1 — Registrar transaccion

1.  se le pide el el titular, el valor,la hora,el pais, dispositivo
2.  se le asigna una id
3.  se guarda el archivo en el json

### Opción 2 — Listar transmisiones

1.  mostrar detalles de la transaccion
2.  mostrar el puntaje de riesgo

### Opción 3 — Salir

Acción: termina la ejecucion del programa
---

## Nota

Este archivo debe completarse durante los primeros 15 minutos del parcial, antes de comenzar la implementación.