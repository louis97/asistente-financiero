"""Cliente HTTP de la API: un método por endpoint. Convierte los fallos en excepciones con mensaje en español."""
import httpx

TIMEOUT_PRIMERA = 70   # solo la primera llamada (estado): el plan gratuito de la API puede tardar ~1 min en despertar
TIMEOUT = 30


class ErrorAcceso(Exception):
    """La API respondió 401 (alias o código no válidos)."""


class ErrorValidacion(Exception):
    """La API respondió 422; `detalle` trae el mensaje de la API."""

    def __init__(self, detalle: str):
        super().__init__(detalle)
        self.detalle = detalle


class ErrorServicio(Exception):
    """Sin conexión, timeout u otro error del servicio; `sin_contacto` indica que ni siquiera hubo respuesta."""

    def __init__(self, mensaje: str, sin_contacto: bool = False):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.sin_contacto = sin_contacto


def _detalle(r: httpx.Response) -> str:
    try:
        d = r.json().get("detail")
    except Exception:
        return ""
    if isinstance(d, list):                       # forma por defecto de FastAPI, por si acaso
        return "; ".join(str(x.get("msg", x)) if isinstance(x, dict) else str(x) for x in d)
    return str(d or "")


class Cliente:
    def __init__(self, api_url: str, alias: str = "", codigo: str = ""):
        self.api_url = api_url.rstrip("/")
        self.encabezados = {"X-Alias": alias.strip(), "X-Codigo": codigo} if alias.strip() else {}

    def _pedir(self, metodo: str, ruta: str, json=None, timeout: int = TIMEOUT):
        try:
            r = httpx.request(metodo, self.api_url + ruta, json=json, headers=self.encabezados, timeout=timeout)
        except (httpx.TimeoutException, httpx.TransportError):
            raise ErrorServicio("No se pudo contactar con el servicio.", sin_contacto=True) from None
        if r.status_code == 401:
            raise ErrorAcceso()
        if r.status_code == 422:
            raise ErrorValidacion(_detalle(r))
        if r.status_code >= 400:
            raise ErrorServicio(_detalle(r) or "El servicio no pudo responder en este momento.")
        try:
            return r.json()
        except ValueError:
            raise ErrorServicio("El servicio devolvió una respuesta ilegible.") from None

    def estado(self, primera_vez: bool = False):
        return self._pedir("GET", "/estado", timeout=TIMEOUT_PRIMERA if primera_vez else TIMEOUT)

    def lecturas(self, ticker, entradas, salidas):
        return self._pedir("POST", "/lecturas", json={"ticker": ticker, "entradas": entradas, "salidas": salidas})

    def riesgo(self, ticker):
        return self._pedir("GET", f"/riesgo/{ticker}")

    def serie(self, ticker):
        return self._pedir("GET", f"/serie/{ticker}")

    def modelo(self):
        return self._pedir("GET", "/modelo")

    def decisiones(self):
        return self._pedir("GET", "/decisiones")

    def crear_decision(self, ticker, nivel, lectura, nota):
        return self._pedir("POST", "/decisiones", json={"ticker": ticker, "nivel": nivel, "lectura": lectura, "nota": nota})

    def niveles(self, ticker):
        return self._pedir("GET", f"/niveles/{ticker}")

    def guardar_niveles(self, ticker, entradas, salidas):
        return self._pedir("PUT", f"/niveles/{ticker}", json={"entradas": entradas, "salidas": salidas})
