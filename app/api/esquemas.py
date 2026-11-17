"""Modelos pydantic de entrada y salida (nombres de campo literales de `01_contratos.md` §4 y §8)."""
import re
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

TICKER_RE = r"^[A-Z.\-]{1,6}$"
NOMBRES_ENTRADAS = ["deep value", "value", "valoración histórica"]
NOMBRES_SALIDAS = ["negativo", "base", "positivo"]


def normalizar_ticker(t: str) -> str:
    return t.strip().upper() if isinstance(t, str) else t


class Nivel(BaseModel):
    valor: float = Field(gt=0, allow_inf_nan=False)
    unidad: Literal["precio", "pe"]


class _ConTicker(BaseModel):
    @field_validator("ticker", mode="before", check_fields=False)
    @classmethod
    def _mayusculas(cls, v):
        return normalizar_ticker(v)


class NivelesUsuario(BaseModel):
    entradas: list[Nivel] = Field(min_length=3, max_length=3)
    salidas: list[Nivel] = Field(min_length=3, max_length=3)


class PedidoLecturas(_ConTicker):
    ticker: str = Field(pattern=TICKER_RE)
    entradas: list[Nivel] = Field(min_length=3, max_length=3)
    salidas: list[Nivel] = Field(min_length=3, max_length=3)


class Decision(_ConTicker):
    ticker: str = Field(pattern=TICKER_RE)
    nivel: str = Field(min_length=1, max_length=60)
    lectura: dict[str, Any] = Field(default_factory=dict)
    nota: str = Field(default="", max_length=2000)


class DecisionGuardada(Decision):
    id: int
    fecha: str


class Tecnica(BaseModel):
    prob: float | None
    ic_lo: float | None
    ic_hi: float | None
    linea_base: float | None
    k: float | None


class Probabilistica(BaseModel):
    prob: float | None
    ic_lo: float | None        # error de simulación, no la incertidumbre del futuro
    ic_hi: float | None
    semanas_mediana: float | None


class LecturaNivel(BaseModel):
    tipo: Literal["entrada", "salida"]
    nombre: str
    precio: float
    pct_vs_actual: float
    pe_implicito: float | None = None
    pb_implicito: float | None = None
    percentil_historia: float | None = None
    percentil_industria: float | None = None
    percentil_pe_norm: float | None = None
    lectura_trampa: str | None = None
    tecnica: Tecnica | None = None
    probabilistica: Probabilistica | None = None


class RespuestaLecturas(BaseModel):
    ticker: str
    precio: float
    fecha_dato: str
    fuente_datos: str
    industria_validada: bool
    niveles: list[LecturaNivel]
    advertencias: list[str]


class FrecCaidas(BaseModel):
    observada: float | None
    esperada: float | None


class Riesgo(BaseModel):
    vol_anual: float | None
    p5_semanal: float | None
    caida_maxima: float | None
    frec_caidas_fuertes: FrecCaidas
    r2_mercado_sector: float | None
    delta_r2_sector: float | None


class Estado(BaseModel):
    ultimo_dato: str | None
    ultimo_recalculo: str | None
    supabase_ok: bool
    fuente_datos: str
    tickers_piloto: list[str]


class Serie(BaseModel):
    fechas: list[str]
    cierres: list[float]
    fuente_datos: str


def validar_ticker_ruta(t: str) -> str:
    """Mismo patrón que el cuerpo de /lecturas; lanza ValueError (→ 422) si no cumple."""
    t = normalizar_ticker(t)
    if not re.match(TICKER_RE, t or ""):
        raise ValueError("El ticker debe tener de 1 a 6 caracteres entre letras mayúsculas, punto y guion")
    return t
