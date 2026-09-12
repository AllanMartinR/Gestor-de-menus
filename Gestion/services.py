"""Conversión de unidades para costeo de platillos (SCRUM-16).

Usa Ingrediente.equivalencia_pza (Opción A): cuántas unidades de la unidad
base del ingrediente equivalen a 1 pieza. No hay tabla genérica 1 pz = X kg.

Limitación aceptada: la equivalencia pz→unidad base es constante para un
mismo ingrediente; no varía por lote ni proveedor.

No implementa calcular_costo_platillo() (SCRUM-17).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Ingrediente

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
