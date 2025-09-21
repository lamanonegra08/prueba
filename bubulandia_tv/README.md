# Bubulandia TV

Bubulandia TV es un juego educativo para niños pequeños creado con Python 3.12 y PyGame 2.6. Combina un estilo visual pastel muy suave, personajes adorables y actividades educativas en español.

## Características principales

- **Resolución 1920×1080 en pantalla completa** con animaciones fluidas a 60 FPS.
- **Asistente de voz** con pyttsx3 que pronuncia colores, frutas, formas, letras (incluyendo Ñ) y números.
- **Escena de inicio** con fondo animado, logo multicolor y el osito Bubú que parpadea y saluda.
- **Modo Aprender** que recorre automáticamente Colores → Frutas → Formas → Abecedario → Números, mostrando tarjetas animadas con audio en español.
- **Modo Jugar** con minijuegos:
  - Colores: arrastra stickers sonrientes al contenedor del color correcto, con confeti y estrellas de premio.
  - Frutas: juego de memoria de 8 cartas con frutas felices. Al completar, suena un “ding” y aparece confeti.
  - Formas, Abecedario y Números incluyen escenas placeholder listas para ampliarse.
- **Interfaz accesible** con botones gigantes, esquinas redondeadas, sombras suaves y animaciones de rebote.
- **Controles rápidos**: `ESPACIO` siguiente, `R` repetir, `J` cambiar modo, `ESC` salir.

## Requisitos

- Python 3.12
- Windows 10/11 recomendado (para scripts `.bat`)
- Dependencias listadas en `requirements.txt`:
  - `pygame==2.6.*`
  - `pyttsx3==2.90`

## Instalación y ejecución

1. Abre una terminal en la carpeta `bubulandia_tv`.
2. Instala las dependencias:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
3. Ejecuta el juego:
   ```bash
   python main.py
   ```

En Windows puedes utilizar los scripts proporcionados:

- **RUN - Bubulandia (Python).bat** instala requisitos y lanza el juego.
- **BUILD - Create EXE (PyInstaller).bat** genera un ejecutable `dist/BubulandiaTV.exe` listo para kioscos.

## Estructura del proyecto

```
bubulandia_tv/
├── main.py
├── core/
│   ├── audio.py
│   ├── scene.py
│   ├── theme.py
│   └── ui.py
├── data/
│   └── data.py
├── scenes/
│   ├── home.py
│   ├── learn.py
│   ├── play_colors.py
│   ├── play_fruits.py
│   ├── play_shapes.py  # TODO
│   ├── play_alphabet.py  # TODO
│   └── play_numbers.py  # TODO
├── assets/
├── requirements.txt
├── README.md
├── RUN - Bubulandia (Python).bat
└── BUILD - Create EXE (PyInstaller).bat
```

## Notas adicionales

- Si el sistema no cuenta con una voz española instalada, pyttsx3 utilizará la voz por defecto disponible.
- El juego intenta inicializar audio y fullscreen automáticamente; en caso de fallo se mantiene una ventana estándar.
- Para futuras expansiones puedes completar los archivos `play_shapes.py`, `play_alphabet.py` y `play_numbers.py` con las mecánicas solicitadas (sombras, selección de letras y globos de números).

¡Disfruta aprendiendo en Bubulandia TV! 💫
