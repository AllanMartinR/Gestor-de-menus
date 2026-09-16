"""Servicios de costeo de platillos y menús.

SCRUM-16: conversión de unidades (convertir_a_unidad_base).
Usa Ingrediente.equivalencia_pza (Opción A): cuántas unidades de la unidad
base del ingrediente equivalen a 1 pieza. No hay tabla genérica 1 pz = X kg.

Limitación aceptada: la equivalencia pz→unidad base es constante para un
mismo ingrediente; no varía por lote ni proveedor.

SCRUM-17: calcular_costo_platillo reutiliza convertir_a_unidad_base.

SCRUM-20: calcular_costo_total_menu y calcular_costo_por_comensal reutilizan
calcular_costo_platillo; no reimplementan el costeo de ingredientes. El
número de comensales no se guarda en el modelo Menu — se captura al momento
de calcular (permite cotizar el mismo menú para distintos tamaños de evento).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Ingrediente, Menu, Platillo

FAMILIA_MASA = 'masa'
FAMILIA_VOLUMEN = 'volumen'
FAMILIA_PIEZA = 'pieza'

FAMILIAS: dict[str, str] = {
    'kg': FAMILIA_MASA,
    'g': FAMILIA_MASA,
    'lt': FAMILIA_VOLUMEN,
    'ml': FAMILIA_VOLUMEN,
    'pz': FAMILIA_PIEZA,
}

# A la unidad canónica de la familia (kg o lt).
FACTOR_A_CANONICA: dict[str, Decimal] = {
    'kg': Decimal('1'),
    'g': Decimal('0.001'),
    'lt': Decimal('1'),
    'ml': Decimal('0.001'),
}


class UnidadNoConvertibleError(Exception):
    """Unidades de distinta familia sin conversión válida (p. ej. kg ↔ lt)."""


class EquivalenciaNoDefinidaError(Exception):
    """Se necesita pz y el ingrediente no tiene equivalencia_pza usable."""


def _a_decimal(valor: Decimal | int | str) -> Decimal:
    if isinstance(valor, Decimal):
        return valor
    return Decimal(str(valor))


def unidades_son_compatibles(unidad_origen: str, unidad_destino: str) -> bool:
    """Indica si dos unidades pueden convertirse (con o sin equivalencia_pza).

    Permitido: misma unidad; masa kg↔g; volumen lt↔ml; pz con masa o volumen.
    No permitido: masa ↔ volumen (sin densidad).
    """
    if unidad_origen == unidad_destino:
        return True
    fam_origen = FAMILIAS.get(unidad_origen)
    fam_destino = FAMILIAS.get(unidad_destino)
    if fam_origen is None or fam_destino is None:
        return False
    if fam_origen == fam_destino:
        return True
    return (
        (fam_origen == FAMILIA_PIEZA and fam_destino in (FAMILIA_MASA, FAMILIA_VOLUMEN))
        or (fam_destino == FAMILIA_PIEZA and fam_origen in (FAMILIA_MASA, FAMILIA_VOLUMEN))
    )


def convertir_a_unidad_base(
    ingrediente: Ingrediente,
    cantidad: Decimal,
    unidad_capturada: str,
) -> Decimal:
    """Convierte `cantidad` en `unidad_capturada` a la unidad base del ingrediente.

    La unidad base es ``ingrediente.unidad_medida`` (unidad del costo_unitario).
    Equivalencias pz: campo ``Ingrediente.equivalencia_pza`` (Opción A).

    Casos:
        - Misma unidad: huevo base kg, 2 kg → Decimal('2') (sin convertir).
        - Métrica: arroz base kg, 500 g → Decimal('0.5').
        - pz→base con equivalencia: huevo base kg, equivalencia_pza=0.060,
          3 pz → Decimal('0.180').
        - pz sin equivalencia: EquivalenciaNoDefinidaError con el nombre.
        - kg↔lt: UnidadNoConvertibleError con el nombre.

    Limitación: equivalencia_pza expresa 1 pz en unidades **base**. Si la base
    ya es pz, una captura en kg/lt/g/ml no se convierte (no hay densidad ni
    un segundo factor). Capturar en pz. No varía por lote ni proveedor.

    Función pura: no consulta ni escribe en la base de datos.
    """
    cantidad_dec = _a_decimal(cantidad)
    unidad_base = ingrediente.unidad_medida

    if unidad_capturada == unidad_base:
        return cantidad_dec

    if not unidades_son_compatibles(unidad_capturada, unidad_base):
        raise UnidadNoConvertibleError(
            f'No se puede convertir {unidad_capturada} a {unidad_base} '
            f'para el ingrediente "{ingrediente.nombre}".'
        )

    fam_capturada = FAMILIAS[unidad_capturada]
    fam_base = FAMILIAS[unidad_base]

    if fam_capturada == fam_base and fam_capturada in (FAMILIA_MASA, FAMILIA_VOLUMEN):
        return (
            cantidad_dec
            * FACTOR_A_CANONICA[unidad_capturada]
            / FACTOR_A_CANONICA[unidad_base]
        )

    equivalencia = ingrediente.equivalencia_pza
    if equivalencia is None or _a_decimal(equivalencia) <= 0:
        raise EquivalenciaNoDefinidaError(
            f'No hay equivalencia por pieza definida para el ingrediente '
            f'"{ingrediente.nombre}".'
        )
    equivalencia_dec = _a_decimal(equivalencia)

    if unidad_capturada == 'pz':
        return cantidad_dec * equivalencia_dec

    # Base pz y captura métrica: equivalencia_pza está en unidades base (pz),
    # no en kg/lt; Option A no resuelve el recíproco.
    raise UnidadNoConvertibleError(
        f'No se puede convertir {unidad_capturada} a {unidad_base} '
        f'para el ingrediente "{ingrediente.nombre}".'
    )


class PlatilloSinIngredientesError(Exception):
    """El platillo no tiene líneas de receta para costear."""


def calcular_costo_platillo(platillo: Platillo) -> Decimal:
    """Costo total de la receta, redondeado a 2 decimales (ROUND_HALF_UP).

    Recorre ``platillo.receta``. Cada ``IngredientePlatillo.cantidad`` se
    interpreta en la unidad base del ingrediente (``unidad_medida``); no hay
    unidad capturada en la línea. Por línea:

        cantidad_base = convertir_a_unidad_base(
            ingrediente, cantidad, ingrediente.unidad_medida
        )
        subtotal = cantidad_base * ingrediente.costo_unitario

    Reutiliza SCRUM-16; no reimplementa conversión. Las excepciones
    UnidadNoConvertibleError y EquivalenciaNoDefinidaError se propagan.

    Si no hay ingredientes, lanza PlatilloSinIngredientesError.
    """
    lineas = list(platillo.receta.select_related('ingrediente'))
    if not lineas:
        raise PlatilloSinIngredientesError(
            f'El platillo "{platillo.nombre}" no tiene ingredientes asociados.'
        )

    total = Decimal('0')
    for linea in lineas:
        ingrediente = linea.ingrediente
        cantidad_base = convertir_a_unidad_base(
            ingrediente,
            linea.cantidad,
            ingrediente.unidad_medida,
        )
        total += cantidad_base * _a_decimal(ingrediente.costo_unitario)

    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class MenuSinPlatillosError(Exception):
    """El menú no tiene platillos asociados para costear."""


class NumeroComensalesInvalidoError(Exception):
    """El número de comensales debe ser un entero mayor a cero."""


def calcular_costo_total_menu(menu: Menu) -> Decimal:
    """Costo total del menú: suma del costo de cada platillo que lo compone.

    Recorre ``menu.composicion`` y llama a ``calcular_costo_platillo`` por
    cada platillo (SCRUM-17); no reimplementa el costeo de ingredientes.

    Si algún platillo del menú no tiene ingredientes en su receta, se
    propaga ``PlatilloSinIngredientesError`` (o las excepciones de
    conversión de unidades) tal como las lanza ``calcular_costo_platillo``.

    Si el menú no tiene platillos asociados, lanza ``MenuSinPlatillosError``.
    """
    platillos = [
        mp.platillo for mp in menu.composicion.select_related('platillo')
    ]
    if not platillos:
        raise MenuSinPlatillosError(
            f'El menú "{menu.nombre}" no tiene platillos asociados.'
        )

    total = Decimal('0')
    for platillo in platillos:
        total += calcular_costo_platillo(platillo)

    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_costo_por_comensal(menu: Menu, numero_comensales: int) -> Decimal:
    """Costo del menú entre el número de comensales, redondeado a 2 decimales.

    El número de comensales no vive en el modelo ``Menu``: se recibe como
    parámetro para poder cotizar el mismo menú a distintos tamaños de evento
    sin duplicar registros. Reutiliza ``calcular_costo_total_menu``.

    Lanza ``NumeroComensalesInvalidoError`` si ``numero_comensales`` no es
    un entero mayor a cero. Propaga ``MenuSinPlatillosError`` y las
    excepciones de costeo de platillo si aplican.
    """
    if not isinstance(numero_comensales, int) or numero_comensales <= 0:
        raise NumeroComensalesInvalidoError(
            'El número de comensales debe ser un entero mayor a cero.'
        )

    costo_total = calcular_costo_total_menu(menu)
    return (costo_total / Decimal(numero_comensales)).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
