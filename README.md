# Betting Opportunity Analyzer ⚽📊

Una aplicación profesional en Python para analizar oportunidades deportivas mediante cuotas, estadísticas y modelos matemáticos (Surebets, Value Bets y Estrategias por Rangos/Gaps).

> [!IMPORTANT]
> **NO REALIZA APUESTAS AUTOMÁTICAMENTE.**
> El sistema recopila datos, analiza cuotas, calcula probabilidades y detecta oportunidades únicamente para que el usuario tome decisiones manualmente.

---

## 📋 Prerrequisitos de Software

Antes de clonar o ejecutar este proyecto, asegúrate de tener instalado en tu sistema:

* **Python**: Versión **3.10 o superior** (Recomendado: Python 3.10, 3.11 o 3.12).
  * *Verifica tu versión en la terminal ejecutando:* `python --version` o `python3 --version`.
* **Git**: Para el control de versiones y clonado del repositorio.
  * *Verifica tu instalación ejecutando:* `git --version`.

---

## 🚀 Guía de Instalación y Configuración Local

Si acabas de clonar este repositorio desde GitHub (o lo vas a instalar en una máquina nueva), sigue estos pasos minuciosos:

### 1. Clonar el Repositorio
```bash
git clone https://github.com/TU_USUARIO/betting-analyzer.git
cd betting-analyzer
```

### 2. Crear el Entorno Virtual (`.venv`)
> **¿Por qué creamos un entorno virtual local?**
> Las carpetas de entorno virtual (`.venv` o `venv`) contienen ejecutables binarios y paquetes específicos de la plataforma de tu máquina. **Nunca deben subirse a GitHub**. Por eso están incluidas en el archivo `.gitignore`.

**En Windows (PowerShell o CMD):**
```powershell
python -m venv .venv
```

**En Linux / macOS:**
```bash
python3 -m venv .venv
```

### 3. Activar el Entorno Virtual

**En Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```
*(Si PowerShell muestra error de políticas de ejecución, ejecuta una sola vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a activar).*

**En Windows (Command Prompt - CMD):**
```cmd
.\.venv\Scripts\activate.bat
```

**En Linux / macOS:**
```bash
source .venv/bin/activate
```

Una vez activado, verás `(.venv)` al inicio de tu línea de comandos en la terminal.

### 4. Configurar Variables de Entorno
Copia el archivo de variables de ejemplo `.env.example` para crear tu `.env` local:

**En Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**En Linux / macOS / Bash:**
```bash
cp .env.example .env
```

### 5. Instalar Dependencias
Con el entorno virtual activado, actualiza `pip` e instala las librerías requeridas:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 6. Ejecutar la Aplicación
```bash
python app.py
```

Abre tu navegador e ingresa a:
```text
http://127.0.0.1:5000
```
*(El sistema inicia por defecto en **MODO DEMO Offline**, cargando datos desde `data/sample_odds.json` para que puedas probar la interfaz inmediatamente).*

---

## 📤 ¿Cómo subir este proyecto a GitHub por primera vez?

Si creaste el proyecto localmente y deseas subirlo a un nuevo repositorio de GitHub:

### Paso 1: Confirmar el `.gitignore`
Asegúrate de que la carpeta `.venv` (y `.env`, `*.db`, `__pycache__`) esté ignorada para no subir archivos pesados ni credenciales privadas. Este repositorio ya cuenta con un `.gitignore` configurado.

### Paso 2: Inicializar Git y realizar el primer Commit
Abre tu terminal en la raíz del proyecto (`betting-analyzer`) y ejecuta:

```bash
# 1. Inicializar repositorio git local
git init

# 3. Agregar todos los archivos permitidos al área de preparación (staging)
git add .

# 4. Guardar el primer commit
git commit -m "feat: inicializar proyecto betting-analyzer"
```

### Paso 3: Vincular y Subir a GitHub
1. Ve a [GitHub](https://github.com) y crea un nuevo repositorio vacío (ej. `betting-analyzer`). **No** selecciones inicializar con README o .gitignore ya que los tenemos localmente.
2. Copia la URL del repositorio remoto.
3. En tu terminal ejecuta:

```bash
# Cambiar el nombre de la rama principal a main
git branch -M main

# Enlazar tu repositorio local con GitHub (reemplaza la URL con la tuya)
git remote add origin https://github.com/TU_USUARIO/betting-analyzer.git

# Subir el código a GitHub
git push -u origin main
```

---

## ✨ Características Principales

1. **Modo DEMO Offline**: Funciona completamente offline sin necesidad de APIs externas pagas utilizando `data/sample_odds.json` y `data/historical_matches.json`.
2. **Módulo 1: Surebet Analyzer**: Detección de arbitrajes matemáticos libres de riesgo directo ($\sum \frac{1}{\text{odd}_i} < 1$), cálculo de ROI y distribución de stakes con precisión `Decimal`.
3. **Módulo 2: Value Betting Analyzer**: Modelo de probabilidad estimada (Poisson / Estadístico) vs cuotas de mercado para hallar ventajas (Edge %) y stake recomendado según Criterio de Kelly.
4. **Módulo 3: Range Strategy Analyzer**: Análisis de coberturas y líneas (Corners / Goles), detección de huecos (gaps) entre operadores, probabilidad Poisson de hueco y riesgo.
5. **Estadísticas Avanzadas**: Cálculo de media, mediana, desviación estándar y distribuciones Poisson para equipos.
6. **Dashboard Moderno**: Interfaz oscura glassmorphic en HTML5/CSS3/Vanilla JS con gráficos, calculadora interactiva de bankroll y filtros en tiempo real.
7. **Base de Datos SQLite**: Almacenamiento persistente de eventos, cuotas, oportunidades detectadas e historial de auditoría.

---

## 📂 Estructura del Proyecto

```text
betting-analyzer/
├── app.py                      # Punto de entrada Flask y Servidor Local
├── requirements.txt            # Dependencias Python
├── README.md                   # Documentación oficial del proyecto
├── AGENTS.md                   # Guía de arquitectura para asistentes de IA
├── .env.example                # Variables de entorno de ejemplo
├── .env                        # Variables de entorno locales (git-ignored)
├── .gitignore                  # Filtros para ignorar .venv, .env, *.db, etc.
│
├── src/                        # Código fuente modular
│   ├── config.py               # Gestión de configuración y rutas
│   ├── database.py             # SQLite DDL y operaciones CRUD
│   ├── models.py               # Modelos Pydantic y Esquema Estándar de Eventos
│   ├── services.py             # Orquestador de proveedores y analizadores
│   │
│   ├── providers/              # Sistema de proveedores de cuotas
│   │   ├── base_provider.py    # Interfaz abstracta OddsProvider
│   │   ├── demo_provider.py    # Proveedor local DEMO (JSON)
│   │   └── api_provider.py     # Proveedor aislado para APIs externas
│   │
│   ├── odds/                   # Normalización y emparejamiento
│   │   ├── normalizer.py       # Conversor de formatos y remoción de margen
│   │   └── matcher.py          # Extracción de mejores cuotas por selección
│   │
│   ├── analyzers/              # Módulos principales de análisis
│   │   ├── surebet.py          # Módulo 1: Surebet Arbitrage
│   │   ├── value_betting.py    # Módulo 2: Value Betting (Edge %)
│   │   └── range_strategy.py   # Módulo 3: Range Strategy & Gap Detection
│   │
│   ├── calculators/            # Calculadoras matemáticas
│   │   ├── stakes.py           # Stake surebet (Decimal) & Kelly Criterion
│   │   ├── probability.py      # Probabilidad implícita y matriz Poisson
│   │   └── roi.py              # ROI y Expected Value (EV)
│   │
│   └── statistics/             # Análisis estadístico histórico
│       ├── goals.py            # Media, mediana y std dev de goles
│       ├── corners.py          # Estadísticas de corners
│       └── trends.py           # Rachas y estado de forma reciente
│
├── data/                       # Archivos de datos de muestra
│   ├── sample_odds.json        # Muestra de cuotas de casas de apuestas
│   └── historical_matches.json # Histórico de partidos para modelos
│
├── templates/                  # Vistas HTML Jinja2
├── static/                     # Archivos estáticos de interfaz (CSS / JS)
└── tests/                      # Suite de pruebas unitarias con pytest
```

---

## ⚡ Modo Real Con OddsPapi (Opcional)

El proyecto puede usar cuotas reales desde OddsPapi. La clave de API se configura **únicamente** en `.env` (nunca en código ni frontend).

### Configuración en `.env`

```env
PROVIDER_MODE=API
EXTERNAL_API_KEY=TU_API_KEY_DE_ODDSPAPI
EXTERNAL_API_URL=https://api.oddspapi.io/v4

ODDSPAPI_SPORT_ID=10
ODDSPAPI_LANGUAGE=es
ODDSPAPI_ODDS_FORMAT=decimal
ODDSPAPI_BOOKMAKERS=apuestatotal,betano.pe,inkabet,pinnacle
ODDSPAPI_USE_TOURNAMENTS=0
ODDSPAPI_TOURNAMENT_IDS=
ODDSPAPI_FIXTURE_DAYS=2
ODDSPAPI_MAX_FIXTURES=3
```

---

## 🧪 Pruebas Unitarias

Para ejecutar toda la suite de pruebas automatizadas con `pytest`:

```bash
pytest -q
```

---

## ⚖️ Exención de Responsabilidad

*Los cálculos presentados por esta herramienta son estimaciones matemáticas basadas en modelos estadísticos y algoritmos de arbitraje. Las cuotas de las casas de apuestas están sujetas a cambios constantes, límites de apuesta individuales y reglas específicas de liquidación por operador.*
