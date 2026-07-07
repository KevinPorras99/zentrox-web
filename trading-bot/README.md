# Zentrox — Bot de Trading de Criptomonedas

Bot de trading modular construido según la especificación del proyecto, con un
principio rector por encima de todo: **preservación del capital y esperanza
matemática positiva, no maximizar el número de operaciones.**

El núcleo del bot está escrito **solo con la librería estándar de Python** (sin
dependencias de terceros), por lo que corre y se prueba en cualquier entorno.
`ccxt` es un extra opcional únicamente para datos de exchange en vivo.

> ⚠️ **Aviso**: software educativo / de investigación. No es asesoría
> financiera. El trading de criptomonedas conlleva riesgo de pérdida total.
> La ejecución contra un exchange real requiere trabajo adicional, claves de
> API auditadas y pruebas exhaustivas en *paper trading* antes de usar capital
> real.

---

## Inicio rápido

```bash
cd trading-bot

# Demo con datos sintéticos deterministas (no requiere red ni instalación):
python -m zentrox_bot demo

# Backtest con dashboard HTML y registro (journal) en SQLite:
python -m zentrox_bot backtest --bars 20000 --html report.html --journal journal.sqlite

# Backtest desde un archivo de configuración JSON:
python -m zentrox_bot backtest --config config.example.json

# Backtest con tus propios datos históricos (CSV: timestamp,open,high,low,close,volume):
python -m zentrox_bot backtest --csv BTC/USDT=data/btc_15m.csv --operational 15m

# Validación fuera de muestra (walk-forward) en 4 segmentos:
python -m zentrox_bot walkforward --folds 4

# Pruebas:
python -m unittest discover -s tests        # o: pytest
```

---

## Arquitectura

Cada componente de la *arquitectura sugerida* en la especificación tiene su
módulo. Estrategia y riesgo están **desacoplados**: la estrategia solo
*propone* operaciones; el gestor de riesgo decide el tamaño y el sí/no final.

```
zentrox_bot/
├── config.py        Configuración (riesgo, estrategia, ejecución) + JSON
├── models.py        Modelos de dominio (Candle, Signal, Position, Trade, …)
├── indicators.py    Indicadores puros (EMA, SMA, ATR, RSI, swings) + resampleo
├── data/            Ingesta de datos
│   ├── synthetic.py   Feed sintético determinista (offline)
│   ├── csv_feed.py    Feed desde CSV histórico
│   └── ccxt_feed.py   Feed en vivo vía ccxt (opcional)
├── strategy/        Motor de estrategia
│   ├── trend.py       Detección de régimen (alcista / bajista / lateral)
│   ├── levels.py      Soportes, resistencias, liquidez
│   └── trend_following.py  Estrategia multi-temporalidad (1D/4H → 15m)
├── risk.py          Gestor de riesgo (sizing + límites de capital)
├── portfolio.py     Gestor de portafolio (exposición, correlación, límites)
├── orders.py        Gestor de órdenes / broker de paper (SL, TP, trailing, parciales)
├── metrics.py       Métricas (win rate, profit factor, expectancy, drawdown, Sharpe/Sortino)
├── journal.py       Registro en SQLite (todas las operaciones y decisiones)
├── monitor.py       Monitor: estado, salud y reglas de seguridad
├── alerts.py        Sistema de alertas (log / webhook)
├── backtest.py      Motor event-driven (+ walk-forward)
├── dashboard.py     Dashboard HTML autocontenido (curva de equity + KPIs)
└── cli.py           Interfaz de línea de comandos
```

El mismo motor (`Strategy` + `RiskManager` + `PortfolioManager` + `OrderManager`)
se usa en backtest y (a futuro) en vivo: solo cambian la fuente de datos y el
broker. Un backtest que pasa ejercita la ruta de decisión real.

---

## Cómo el código cumple la especificación

| Requisito de la especificación | Dónde se implementa |
| :-- | :-- |
| Tendencia en 1D y 4H, confirmación en 15m–1H | `strategy/trend.py`, `strategy/trend_following.py` |
| Soportes, resistencias y liquidez | `strategy/levels.py` |
| RR mínimo 1:2 (ideal 1:3) | `risk.py` (compuerta `min_rr`), `strategy` (TP a `target_rr`) |
| Riesgo por operación 0.5–1 %, sizing automático | `risk.py` (`risk_per_trade`, sizing por distancia al stop) |
| Stop-loss obligatorio | `risk.py` (rechaza señales sin stop), `monitor.py` (`assert_protected`) |
| Máx. pérdidas consecutivas → pausa | `risk.py` (`max_consecutive_losses`) |
| Límite diario de pérdida | `risk.py` (`daily_loss_limit`) |
| Stop fijo/dinámico, trailing, salidas parciales, tiempo máx. | `orders.py` |
| Exposición máxima, correlación, límites por activo | `portfolio.py` |
| Adaptación al mercado (alcista/bajista/lateral o abstenerse) | `strategy/trend.py` (abstiene en rango o desalineación) |
| Métricas (WR, PF, Expectancy, DD, Sharpe/Sortino, …) | `metrics.py` |
| Backtesting: costos, slippage, fuera de muestra, walk-forward | `backtest.py` |
| Registro (fecha, activo, entrada/salida, motivo, resultado) | `journal.py` |
| Reglas de seguridad (no promediar, no quitar stop, pausar en DD) | `risk.py`, `monitor.py`, `orders.py` |
| Arquitectura (ingesta, estrategia, riesgo, órdenes, monitor, DB, dashboard, alertas) | módulos correspondientes |

### Reglas de seguridad (invariantes)

- **Nunca promediar pérdidas**: el bot no añade a posiciones perdedoras; una
  posición por símbolo (`max_positions_per_symbol`).
- **No eliminar el stop-loss**: `Monitor.assert_protected` impide que exista una
  posición sin stop válido.
- **No aumentar el riesgo tras pérdidas**: el sizing siempre se calcula sobre el
  *equity actual* (baja con las pérdidas, nunca sube), y la cuenta se **pausa**
  en vez de "revenge trading".
- **Pausar por drawdown**: al superar `max_drawdown_pause` el bot se **halt**
  (requiere intervención manual para reanudar).

### Realismo del backtest

- Comisiones y **slippage** adverso en cada fill.
- Resolución intrabar **pesimista**: si una vela toca stop y objetivo, gana el
  stop.
- **Sin lookahead**: en cada paso solo son visibles las velas 1D/4H ya
  *cerradas*.

---

## Configuración

Valores por defecto conservadores en `config.py`; ver `config.example.json`
para todas las opciones. Parámetros clave:

| Parámetro | Def. | Significado |
| :-- | :-- | :-- |
| `risk.risk_per_trade` | `0.01` | Fracción del equity arriesgada por operación (1 %) |
| `risk.min_rr` | `2.0` | RR mínimo para aprobar una entrada (1:2) |
| `risk.max_consecutive_losses` | `3` | Pausa tras N pérdidas seguidas |
| `risk.daily_loss_limit` | `0.03` | Corta el día tras -3 % |
| `risk.max_drawdown_pause` | `0.20` | Halt del bot más allá de -20 % |
| `risk.max_total_exposure` | `0.30` | Riesgo agregado máximo vs equity |
| `strategy.htf_trend/mtf_trend/operational` | `1d/4h/15m` | Temporalidades |
| `strategy.target_rr` | `3.0` | RR del take-profit (ideal 1:3) |
| `execution.commission/slippage` | `0.0004/0.0005` | Costos por fill |

---

## Notas sobre el trading en vivo

`data/ccxt_feed.py` obtiene OHLCV real (histórico o reciente) vía `ccxt`
(`pip install ccxt` o `pip install .[live]`). La **ejecución de órdenes reales
NO está implementada** a propósito: pasar a vivo exige claves de API con los
permisos correctos, manejo de errores de red/exchange, reconciliación de estado
y un periodo de paper trading. El diseño desacoplado permite añadir un
`LiveBroker` que reemplace al broker de paper de `orders.py` sin tocar la
estrategia ni el gestor de riesgo.

---

## Tests

34 pruebas cubren indicadores, sizing y compuertas de riesgo, ciclo de vida de
órdenes (SL/TP/trailing/parciales/costos), métricas, detección de tendencia y un
backtest end-to-end determinista.

```bash
python -m unittest discover -s tests    # sin dependencias
pytest                                  # si prefieres pytest
```
