# 🧠 Tres en Raya con IA Inteligente (Python + Tkinter)

## 🎥 Demo en acción

<p align="center">
  <img src="assets/tic_tac_toe_demo.gif" alt="Tic Tac Toe Demo" style="max-width: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border-radius: 10px;" />
</p>

---

## 📸 Capturas de pantalla

<p align="center">
  <img src="assets/tic_tac_toe_login.png" alt="Login" width="30%" style="margin-right: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.15); border-radius: 8px;" />
  <img src="assets/tic_tac_toe_game.png" alt="Human Game" width="30%" style="margin-right: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.15); border-radius: 8px;" />
  <img src="assets/tic_tac_toe_vs_machine.png" alt="AI Game" width="30%" style="box-shadow: 0 4px 8px rgba(0,0,0,0.15); border-radius: 8px;" />
</p>

---

<p align="center" style="margin-top: 1rem;">
  <a href="../LICENSE" style="margin-right: 20px; text-decoration:none;">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT" />
  </a>
  <a href="https://www.python.org/" style="margin-right: 20px; text-decoration:none;">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python Version" />
  </a>
  <a href="https://github.com/AndrewTeleco/tic_tac_toe_ai/actions/workflows/python-app.yml" style="margin-right: 20px; text-decoration:none;">
    <img src="https://github.com/AndrewTeleco/tic_tac_toe_ai/actions/workflows/python-app.yml/badge.svg" alt="Build Status" />
  </a>
  <a href="https://github.com/AndrewTeleco/tic_tac_toe_ai" style="text-decoration:none;">
    <img src="https://img.shields.io/badge/Open%20Source-Yes-brightgreen.svg" alt="Open Source" />
  </a>
</p>

---

Este es un juego completo de **Tres en Raya** construido en Python con una interfaz gráfica usando `tkinter`. El juego soporta modos de **jugador contra jugador** y **jugador contra IA**, con varios niveles de dificultad que van desde fácil hasta un oponente muy desafiante potenciado por heurísticas avanzadas y poda alfa-beta.

## 🎮 Características Clave

- ✅ Soporta tableros de **3x3 y 4x4**
- ✅ IA con 4 niveles: **FÁCIL, MEDIO, DIFÍCIL, MUY DIFÍCIL**
- ✅ Implementa el **Algoritmo Minimax** con poda alfa-beta y heurísticas de puntuación
- ✅ Registro de partidas y un **sistema de ranking** para los mejores jugadores
- ✅ Control total del juego vía interfaz gráfica con selectores de dificultad personalizados
- ✅ Soporte para colores ANSI en consola (compatible Linux/Unix)
- ✅ Código altamente **modular y mantenible**

---

## 🧩 Resumen de la Lógica del Juego (TicTacToeLogic)

La lógica está diseñada para ser modular y separada de la UI, facilitando su mantenimiento y futuras expansiones.

La mecánica principal del juego está implementada en la clase `TicTacToeLogic`, que gestiona:

- **Gestión de jugadores y turnos:** Controla quién juega, cambia turnos y maneja la identidad de los jugadores.
- **Validación de movimientos:** Verifica que las jugadas sean legales y las casillas estén vacías.
- **Gestión del estado del tablero:** Mantiene el estado actual del tablero para modos 3x3 y 4x4.
- **Detección de victoria y empate:** Revisa después de cada movimiento si hay un ganador o empate.
- **Actualización de puntuaciones y rankings:** Actualiza y lleva el puntaje y las victorias acumuladas.
- **Integración con IA:** Proporciona movimientos de IA según la dificultad seleccionada.
- **Control del flujo del juego:** Reinicia el tablero, inicia nuevas partidas y cambia modos de juego.

---

## 🖥️ Interfaz Principal y Utilidades Auxiliares

- **TicTacToeGame**: Ventana principal que administra toda la GUI, incluyendo el tablero, paneles de jugadores, botones y selectores de dificultad. Coordina la interacción y enlaza la UI con la lógica y la IA

- **DisplayGame**: Administra la visualización de información de los jugadores (nombres, símbolos, puntuaciones y victorias), además del panel central de mensajes dinámicos y parpadeantes.

- **BoardGame**: Maneja la representación gráfica del tablero, construyendo una cuadrícula interactiva N x N que responde a los cambios de estado, destacando combinaciones ganadoras y reiniciando el tablero.

- **ButtonsPanel**: Administra los botones de reinicio, reset y salida, manejando los eventos de usuario y comunicándose con el controlador principal.

- **DifficultyPanel**: Proporciona un selector semicircular para elegir entre cuatro niveles de dificultad de IA, gestionando el estado visual y notificando cambios.

- **RankingTopPlayers**: Gestiona el ranking y estadísticas de jugadores con persistencia usando shelve. Formatea una tabla con los mejores jugadores destacando posiciones, victorias y puntuaciones.

Ejemplo de salida en consola del ranking:

```
--------------------------------- 😎 LISTA TOP JUGADORES 😎 ----------------------------------------
|____POS____|_______USUARIO________|____PARTIDAS____|____VICTORIAS____|____PUNTOS___|_____RATIO_____|
|     1     |     username_1       |      026       |       09        |     037     |    34.62 %    |
|     2     |      MACHINE         |      026       |       07        |     031     |    26.92 %    |
|     3     |     username_2       |      000       |       00        |     000     |     0.0 %     |
-----------------------------------------------------------------------------------------------------
```

- **LogGame**: Sistema de logging para eventos clave del juego, con salida en consola y archivos .md en la carpeta /data/logs. Los logs son coloridos, con timestamps y muestran el tablero tras cada evento.

Ejemplo de salida por consola:

```
|TIME: 2025-07-18 18:38:06|
|EVENT: The game has ended in a match and both players get 1 point 🤝|
|GRID| +----+ +----+ +----+ +----+
       | 🐉 | |    | | 🐉 | | 🐬 |
       +----+ +----+ +----+ +----+
       |    | | 🐉 | | 🐬 | |    |
       +----+ +----+ +----+ +----+
       | 🐬 | | 🐬 | | 🐬 | | 🐉 |
       +----+ +----+ +----+ +----+
       | 🐉 | | 🐉 | | 🐬 | | 🐉 |
       +----+ +----+ +----+ +----+
```

- **enums.py**: Centraliza las enumeraciones usadas en todo el proyecto, mejorando claridad y modularidad.

- **helper_classes.py**: Contiene clases auxiliares y named tuples para UI, entidades del juego, excepciones y estructuras de configuración.

- **helper_methods.py**: Funciones utilitarias para serialización del tablero, heurísticas, detección de simetrías y mejoras para la IA.

- **literals.py**: Constantes globales como colores, fuentes y textos usados en la app para mantener consistencia.

---

## 🔐 Módulo de Configuración de Usuarios (user_config/)

Gestiona el login y la configuración de credenciales, asegurando identidades válidas antes de iniciar el juego:

- **user_credentials_gui.py**: (UserCredentialsGUI)  
  Ventana principal de login para que los jugadores ingresen su nombre y elijan animal (emoji) y color. Construye toda la GUI.

- **user_credentials_callbacks.py**: Maneja eventos interactivos (actualización de texto, selección en listas, toggles) y refresca la GUI dinámicamente.

- **user_credentials_storage.py**: Carga listas de animales y colores, guarda credenciales y registra logs de sesión.

- **user_credentials_validator.py**: Valida las entradas para evitar duplicados o datos inválidos y asegura las reglas de selección.

---

## 🤖 Niveles de Dificultad de la IA

| Nivel       | Descripción                                                                     |
| ----------- | ------------------------------------------------------------------------------- |
| FÁCIL       | Movimientos completamente aleatorios 😄                                         |
| MEDIO       | Minimax básico sin poda, con probabilidad de errores aleatorios 🤔              |
| DIFÍCIL     | Minimax con poda alfa-beta y lógica más profunda 😨                             |
| MUY DIFÍCIL | Minimax completo con heurísticas, puntuación estratégica y control de tiempo 🤖 |

---

## 🧱 Estructura del proyecto

```
TIC_TAC_TOE_GAME/          # Raíz del proyecto
│
├── LICENSE                # Archivo de licencia
├── README.md              # README principal
├── main.py                # Punto de entrada de la aplicación
├── .gitignore             # Reglas de Git para ignorar archivos
├── requirements.txt       # Dependencias de Python (opcional)
│
├── tic_tac_toe/           # Paquete principal
│   ├── __init__.py        # Convierte esta carpeta en un paquete de Python
│   │
│   ├── ai/                # Lógica de IA y ranking de jugadores
│   │   ├── __init__.py
│   │   ├── ai_player.py
│   │   └── ranking_top_players.py
│   │
│   ├── core/              # Lógica principal, utilidades, enums, constantes, logging
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   ├── helper_classes.py
│   │   ├── helper_methods.py
│   │   ├── literals.py
│   │   ├── log_game.py
│   │   ├── logic_game.py
│   │   └── paths.py
│   │
│   ├── data/              # Datos persistentes y registros
│   │   ├── credentials.shlv
│   │   ├── ranking_top_players.shlv
│   │   └── logs/          # Carpeta para logs de la aplicación
│   │
│   ├── gui/               # Módulos de interfaz gráfica y ventana principal
│   │   ├── __init__.py
│   │   ├── board_game.py
│   │   ├── buttons_panel.py
│   │   ├── difficulty_panel.py
│   │   ├── display_game.py
│   │   └── tic_tac_toe_game.py
│   │
│   ├── tests/                   # Scripts de tests y demos
│   │   ├── __init__.py
│   │   ├── conftest.py          # Configura el entorno de tests y hace mock de Tkinter para tests de GUI
│   │   ├── test_ai.py
│   │   ├── test_core.py
│   │   ├── test_gui.py
│   │   └── test_user_config.py
│   │
│   └── user_config/       # Gestión de credenciales de usuario
│       ├── __init__.py
│       ├── Animals.md
│       ├── Colors.md
│       ├── user_credentials_callbacks.py
│       ├── user_credentials_gui.py
│       ├── user_credentials_storage.py
│       └── user_credentials_validator.py
│
└──  docs/                        # Documentación y recursos
      ├── assets/                 # Archivos multimedia para la documentación
      │   ├── tic_tac_toe_demo.gif
      │   ├── tic_tac_toe_login.png
      │   ├── tic_tac_toe_game.png
      │   └── tic_tac_toe_vs_machine.png
      │
      ├── README_EN.md       # Documentación en inglés
      └── README_ES.md       # Documentación en español



```

## 📐 Distribución visual de la GUI (Diagramas)

### 🔐 Diseño de UserCredentialsGUI (Ventana de login)

Este diagrama representa la estructura general de la ventana de login del juego,
donde cada uno de los 2 jugadores introducen sus credenciales.

```
┌──────────────────────────────────────────────────────────────────────┐
│               MAIN LOGIN WINDOW (UserCredentialsGUI)                 │
│                                                                      │
│  ┌────────────────────────────┐   ┌────────────────────────────┐     │
│  │       PLAYER 1 Section     │   │       PLAYER 2 Section     │     │
│  │  Username | Animal | Color │   │  Username | Animal | Color │     │
│  │  [Entries | Lists | Radios]│   │  [Entries | Lists | Radios]│     │
│  └────────────────────────────┘   └────────────────────────────┘     │
│                                                                      │
│                      [ Button: "Start Game" ]                        │
└──────────────────────────────────────────────────────────────────────┘

```

### 🎮 Diseño de TicTacToeGame (Ventana principal)

Este diagrama representa la estructura general de la ventana principal del juego TicTacToe y sus componentes internos.

```
┌──────────────────────────────────────────────────────────────────────┐
│                   MAIN GAME WINDOW (TicTacToeGame)                   │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                WHOLE Frame: self.frames[WHOLE]                 │  │
│  │                                                                │  │
│  │    ┌────────────────────────────────────────────────────┐      │  │
│  │    │        DISPLAY Frame: self.frames[DISPLAY]         │      │  │
│  │    │     ┌──────────┐ ┌────────────┐ ┌──────────┐       │      │  │
│  │    │     │ Player 1 │ │   Message  │ │ Player 2 │       │      │  │
│  │    │     └──────────┘ └────────────┘ └──────────┘       │      │  │
│  │    └────────────────────────────────────────────────────┘      │  │
│  │                                                                │  │
│  │ ┌────────────────────┬───────────────────────────────────────┐ │  │
│  │ │    BOARD Frame:    │      CONFIGURATION_PANEL Frame:       │ │  │
│  │ │                    │    self.frames[CONFIGURATION_PANEL]   │ │  │
│  │ │ self.frames[BOARD] │ ┌───────────────────────────────────┐ │ │  │
│  │ │                    │ │ BUTTONS_PANEL Frame:              │ │ │  │
│  │ │                    │ │     self.frames[BUTTONS_PANEL]    │ │ │  │
│  │ │    (BoardGame)     │ │     (ButtonsPanel)                │ │ │  │
│  │ │                    │ │ - Radiobuttons (3x3 / 4x4)        │ │ │  │
│  │ │ N x N grid buttons │ │ - Checkbutton (vs machine)        │ │ │  │
│  │ │                    │ │ - Difficulty semicircle (panel)   │ │ │  │
│  │ │                    │ │ - Buttons (Start, Reset, Exit)    │ │ │  │
│  │ │                    │ └───────────────────────────────────┘ │ │  │
│  │ └────────────────────┴───────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### 🛠️ Estructura de ButtonsPanel (Panel de configuración)

Este diagrama muestra los controles dentro del panel de configuración, incluyendo opciones de tablero, modo de juego, selector de dificultad y botones de acción.

```
┌──────────────────────────────────────────────┐
│               ButtonsPanel                   │
│  (tk.Frame - contains all configuration UI)  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │     Board Size Selector (Radiobuttons) │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │ Label: "Board Size Dimension"    │  │  │
│  │  └──────────────────────────────────┘  │  │
│  │            [ 3x3 ]  [ 4x4 ]            │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │      Game Mode Toggle (Checkbutton)    │  │
│  │          [✓] Play vs Machine           │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │      Difficulty Selector Panel         │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │    Semicircle Difficulty UI      │  │  │
│  │  │      EASY   MEDIUM   HARD        │  │  │
│  │  └──────────────────────────────────┘  │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │            Action Buttons              │  │
│  │         START   RESET   EXIT           │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

## 🚀 Cómo ejecutar el proyecto

### Requisitos previos:

- Python 3.10 o superior
- tkinter instalado (normalmente viene con Python)
- Git (opcional, para clonar el repositorio)

### Instalación:

```bash
git clone https://github.com/AndrewTeleco/tic_tac_toe_ai.git
cd tic_tac_toe
pip install -r requirements.txt  # Opcional, sólo si agregas dependencias

```

### Ejecutar en el juego:

```bash
python3 main.py
```

💡En Windows, usa python en lugar de python3.

### 🧪 Ejecutando Tests

Este proyecto incluye tests automatizados ubicados en la carpeta [`tests/`](../tic_tac_toe/tests/).

Para ejecutarlos, simplemente usa:

```bash
pytest
```

### Cobertura y Tests Automatizados 🏆

Este proyecto incluye múltiples tests para asegurar que cada módulo funciona correctamente y que la integración entre lógica, IA y GUI es estable.
Resumen de tests principales:

```
--------------------------------------------------------------------------------------------------------------------------------------------------
| Test File             | Qué Prueba                                             | Comentarios / Resumen                                         |
| --------------------- | ------------------------------------------------------ | ------------------------------------------------------------- |
| `test_ai.py`          | **AIPlayer**                                           |  - Alta cobertura de la IA: heurísticas, Minimax y            |
|                       |                                                        |    decisiones en tableros 3x3 y 4x4.                          |
|                       | - Inicialización y getters/setters                     |  - Uso de `shelve` para independencia del almacenamiento      |
|                       | - `_get_remaining_moves`                               |                                                               |
|                       | - Selección de movimiento (                            |                                                               |
|                       |        `select_random_move`,                           |                                                               |
|                       |        `select_medjum_move`,                           |                                                               |
|                       |       `select_hard_move`,                              |                                                               |
|                       |       `select_very_hard_move`                          |                                                               |
|                       |     )                                                  |                                                               |
|                       |                                                        |                                                               |
|                       |                                                        |                                                               |
| --------------------- | ------------------------------------------------------ | ------------------------------------------------------------- |
| `test_core.py`        | **TicTacToeLogic**                                     |  - Cubre la lógica central del juego.                         |
|                       |                                                        |  - Maneja errores (`invalidMoveError`) y la interacción       |
|                       |                                                        |    entre jugadores humanos y la máquina.                      |
|                       | - Gestión de jugadores y turnos                        |                                                               |
|                       | - Validación de movimientos                            |                                                               |
|                       | - Estado del tablero                                   |                                                               |
|                       | - Detección de victoria/empate                         |                                                               |
|                       | - Actualización de puntuaciones y rankings             |                                                               |
|                       | - Integración con IA                                   |                                                               |
| --------------------- | ------------------------------------------------------ | ------------------------------------------------------------- |
| `test_gui.py`         | **TicTacToeGame**                                      |  - Evalúa integración GUI-lógica usando mocks.                |
|                       |                                                        |  - Sin abrir ventanas reales.                                 |
|                       | - Inicialización de GUI y construcción de tablero      |                                                               |
|                       | - Propiedades de celdas                                |                                                               |
| --------------------- | ------------------------------------------------------ | ------------------------------------------------------------- |
| `test_user_config.py` | **UserCredentialsGUI + Storage**                       |  - Mocks y FakeVars evitan abrir ventanas reales.             |
|                       |                                                        |  - Evalúa integridad de datos, carga y persistencia.          |
|                       | - Carga de recursos (animales/colores)                 |                                                               |
|                       | - Almacenamiento persistente (`Store_data`, etc.)      |                                                               |
| --------------------- | ------------------------------------------------------ | ------------------------------------------------------------- |

```

👉 Sobre conftest.py

El archivo tests/conftest.py configura el entorno de tests para que los tests nunca dependan de una GUI real (tkinter).
Los componentes de Tkinter están “mockeados”, por lo que no se abrirán ventanas.
Los tests funcionan correctamente en cualquier entorno (Linux, macOS, Windows, GitHub Actions).
Esto permite a los colaboradores escribir y ejecutar tests de la lógica de la GUI sin preocuparse por errores TclError ni por la ausencia de un display.

---

## 🧪 Estado del proyecto

El proyecto está en la fase final de optimización y revisión.
Todos los componentes principales han sido cuidadosamente implementados y evaluados con alta calidad.
Las estrategias de IA y la interfaz gráfica están estables y pulidas, listas para despliegue y liberación open-source.

---

## Contribuciones

¡Las contribuciones son muy bienvenidas! Por favor sigue estas pautas:

- Haz un fork del repositorio y crea una rama nueva (git checkout -b feature/tu-feature)
- Realiza commits claros y descriptivos (git commit -m "Añadir característica XYZ")
- Sube tu rama (git push origin feature/tu-feature)
- Abre un Pull Request describiendo tus cambios

Por favor mantén la consistencia del estilo de código e incluye tests para nuevas funcionalidades si es posible.

---

## 🛠️ FAQ y Solución de Problemas

P: ¿Qué hago si no tengo tkinter instalado?
R: En Linux, ejecuta sudo apt-get install python3-tk (Debian/Ubuntu) o el equivalente para tu distro.
En Windows/macOS, tkinter normalmente viene con Python.

P: ¿Cómo cambio la dificultad de la IA?
R: Usa el selector semicircular de dificultad en la ventana principal antes de iniciar una partida.

P: ¿Dónde se guardan los logs?
R: Los logs se guardan en archivos .md dentro de la carpeta /data/logs.

---

## ⭐ ¿Te gustó este proyecto?

¡Si este proyecto te ha parecido interesante o útil, considera darle una **estrella en GitHub**!  
Eso me ayuda a seguir creando proyectos de calidad y es un buen apoyo para seguir creciendo.

<p align="center">
  <a href="https://github.com/AndrewTeleco/tic_tac_toe_ai" target="_blank">
    <img src="https://img.shields.io/github/stars/AndrewTeleco/tic_tac_toe_ai?style=social" alt="GitHub Repo Stars">
  </a>
</p>

---

## 👤 Autor

**Andrés David Aguilar Aguilar**  
GitHub: [@AndrewTeleco](https://github.com/AndrewTeleco)
📅 Agosto 2025

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT – Modificada para Uso No Comercial**.

Puedes usar, modificar y compartir el código libremente siempre que no sea con fines comerciales.
Para uso comercial, contacta con el autor.

Consulta la licencia completa en el archivo [LICENSE](../LICENSE).
