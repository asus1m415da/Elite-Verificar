# 🛡️ Elite Verify

### Sistema de Verificación Profesional para Discord

[![Discord.py](https://img.shields.io/badge/discord.py-2.3.2-blue.svg)](https://github.com/Rapptz/discord.py)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

<p align="center">
  <img src="https://i.imgur.com/GV4iV7v.png" alt="Elite Verify Banner" width="600px">
</p>

**Bot de verificación avanzado con panel web moderno inspirado en Discord**

[Características](#-características) • [Instalación](#-instalación) • [Configuración](#%EF%B8%8F-configuración) • [Uso](#-uso) • [Comandos](#-comandos)

</div>

---

## 📋 Tabla de Contenidos

- [✨ Características](#-características)
- [🎨 Preview](#-preview)
- [🚀 Instalación](#-instalación)
- [⚙️ Configuración](#%EF%B8%8F-configuración)
- [🎮 Uso](#-uso)
- [📚 Comandos](#-comandos)
- [🛠️ Tecnologías](#%EF%B8%8F-tecnologías)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🤝 Contribuir](#-contribuir)

---

## ✨ Características

### 🌟 Panel Web Moderno
- **Diseño inspirado en Discord** con colores y tipografía oficiales
- **Sidebar de navegación** organizado por secciones
- **Interfaz responsive** que funciona en móvil, tablet y desktop
- **Animaciones suaves** y efectos visuales profesionales
- **Theme oscuro** siguiendo el estilo de Discord

### 🎨 Personalización Completa
- ✅ **Selector visual de emojis** del servidor con preview
- ✅ **Editor de embed** con vista previa en tiempo real
- ✅ **Color picker** con código hexadecimal
- ✅ **Configuración de imágenes** para el mensaje
- ✅ **Título y descripción** personalizables

### 🔒 Seguridad y Protección
- 🛡️ **Protección contra cuentas nuevas** (edad mínima configurable)
- 🛡️ **Verificación por reacción** automática
- 🛡️ **Sistema de logs** completo y detallado
- 🛡️ **Gestión de roles** inteligente

### 📊 Administración
- 📈 **Estadísticas en tiempo real** del bot
- 📈 **Panel de configuración intuitivo**
- 📈 **Gestión de múltiples servidores**
- 📈 **Canal de logs opcional** para auditoría

---

## 🎨 Preview

### Panel Web
<p align="center">
  <img src="https://i.imgur.com/placeholder1.png" alt="Panel Principal" width="700px">
  <br>
  <em>Panel de configuración principal con diseño moderno</em>
</p>

### Selector de Emojis
<p align="center">
  <img src="https://i.imgur.com/placeholder2.png" alt="Selector de Emojis" width="700px">
  <br>
  <em>Selector visual de emojis del servidor</em>
</p>

### Vista Previa en Discord
<p align="center">
  <img src="https://i.imgur.com/placeholder3.png" alt="Mensaje en Discord" width="700px">
  <br>
  <em>Mensaje de verificación en Discord</em>
</p>

---

## 🚀 Instalación

### Requisitos Previos

- **Python 3.11+** instalado
- **Git** para clonar el repositorio
- **Bot de Discord** creado en [Discord Developer Portal](https://discord.com/developers/applications)

### Paso 1: Clonar el Repositorio

```

git clone https://github.com/tu-usuario/elite-verify.git
cd elite-verify

```

### Paso 2: Crear Entorno Virtual (Recomendado)

```


# Windows

python -m venv venv
venv\Scripts\activate

# Linux/Mac

python3 -m venv venv
source venv/bin/activate

```

### Paso 3: Instalar Dependencias

```

pip install -r requirements.txt

```

### Paso 4: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```

cp .env.example .env

```

Edita el archivo `.env` con tus datos:

```

DISCORD_BOT_TOKEN=tu_token_del_bot_aqui

```

---

## ⚙️ Configuración

### 1. Crear un Bot en Discord

1. Ve al [Portal de Desarrolladores de Discord](https://discord.com/developers/applications)
2. Click en **"New Application"**
3. Dale un nombre a tu aplicación (ej: Elite Verify)
4. Ve a la sección **"Bot"** → **"Add Bot"**
5. Copia el **Token** y guárdalo en el archivo `.env`

### 2. Configurar Permisos del Bot

En la sección **OAuth2 → URL Generator**, selecciona:

#### Scopes:
- ✅ `bot`
- ✅ `applications.commands`

#### Permisos del Bot:
- ✅ `Manage Roles` (Gestionar roles)
- ✅ `Kick Members` (Expulsar miembros)
- ✅ `Manage Messages` (Gestionar mensajes)
- ✅ `Send Messages` (Enviar mensajes)
- ✅ `Add Reactions` (Añadir reacciones)
- ✅ `Read Message History` (Leer historial de mensajes)

### 3. Habilitar Intents

En la sección **Bot**, activa los siguientes **Privileged Gateway Intents**:

- ✅ `SERVER MEMBERS INTENT`
- ✅ `MESSAGE CONTENT INTENT`

### 4. Invitar el Bot a tu Servidor

Copia la URL generada en **OAuth2 → URL Generator** y ábrela en tu navegador para invitar el bot.

---

## 🎮 Uso

### Iniciar el Bot

```

python bot.py

```

Deberías ver algo como:

```

============================================================
✅ Elite Verify iniciado correctamente
👤 Usuario: Elite Verify (1234567890)
📚 discord.py: 2.3.2
🌐 Servidores: 1
============================================================

* Running on http://127.0.0.1:5000

```

### Acceder al Panel Web

Abre tu navegador y ve a:

```

http://localhost:5000

```

### Configurar el Bot desde el Panel

1. **Selecciona tu servidor** en la primera sección
2. **Elige el rol** que se asignará al verificarse
3. **Selecciona el canal** donde se publicará el mensaje
4. **Personaliza el mensaje** (título, descripción, color)
5. **Elige un emoji** del servidor o usa uno Unicode
6. **Guarda la configuración** con el botón verde
7. **Publica el mensaje** en el canal configurado

¡Listo! Los usuarios ahora pueden verificarse reaccionando al mensaje.

---

## 📚 Comandos

Elite Verify usa **Slash Commands** (comandos con `/`):

| Comando | Descripción | Permisos Requeridos |
|---------|-------------|---------------------|
| `/panel` | Obtiene el enlace al panel web de configuración | Administrador |
| `/info` | Muestra información sobre el bot y estadísticas | Todos |

---

## 🛠️ Tecnologías

### Backend
- **[discord.py 2.3.2](https://github.com/Rapptz/discord.py)** - Librería para interactuar con Discord API
- **[Flask 3.1.0](https://flask.palletsprojects.com/)** - Framework web para el panel de administración
- **[Flask-CORS](https://flask-cors.readthedocs.io/)** - Manejo de CORS para la API
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - Gestión de variables de entorno

### Frontend
- **HTML5** - Estructura del panel web
- **CSS3** - Estilos modernos inspirados en Discord
- **JavaScript (Vanilla)** - Interactividad y comunicación con la API
- **[Font Awesome 6.4.0](https://fontawesome.com/)** - Iconos profesionales

### Características Técnicas
- ✅ **Async/Await** - Programación asíncrona eficiente
- ✅ **JSON Storage** - Almacenamiento de configuración persistente
- ✅ **RESTful API** - Comunicación entre frontend y backend
- ✅ **Event-driven** - Sistema basado en eventos de Discord
- ✅ **Threading** - Ejecución simultánea del bot y servidor web

---

## 📁 Estructura del Proyecto

```

elite-verify/
│
├── bot.py                  \# Archivo principal del bot
├── requirements.txt        \# Dependencias de Python
├── .env                    \# Variables de entorno (NO SUBIR A GIT)
├── .env.example            \# Ejemplo de variables de entorno
├── .gitignore              \# Archivos ignorados por Git
├── README.md               \# Este archivo
├── LICENSE                 \# Licencia del proyecto
│
├── templates/              \# Templates HTML
│   └── index.html          \# Panel web principal
│
├── static/                 \# Archivos estáticos (opcional)
│   ├── css/
│   ├── js/
│   └── img/
│
└── config.json             \# Configuración guardada (generada automáticamente)

```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si quieres mejorar Elite Verify:

### Cómo Contribuir

1. **Fork** el repositorio
2. Crea una **rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add: AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. Abre un **Pull Request**

---

## 🙏 Agradecimientos

- [discord.py](https://github.com/Rapptz/discord.py) - Por la increíble librería
- [Flask](https://flask.palletsprojects.com/) - Por el framework web
- [Font Awesome](https://fontawesome.com/) - Por los iconos
- Discord - Por la increíble plataforma

---


<div align="center">

### ⭐ Si te gusta este proyecto, dale una estrella en GitHub ⭐

**Hecho con ❤️ y Python**

[⬆ Volver arriba](#-elite-verify)

</div>
```


***
