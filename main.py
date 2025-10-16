import discord
from discord.ext import commands
from discord import app_commands
import datetime
import os
import logging
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import secrets
import asyncio
from threading import Thread

load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EliteVerify')

# Configuración del bot
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Configuración de archivos
CONFIG_FILE = Path(__file__).parent / "config.json"

# Configuración por defecto
default_config = {
    "title": "Elite Verify • Sistema de Verificación",
    "description": "¡Bienvenido! Reacciona con el emoji de abajo para verificarte y obtener acceso completo al servidor.",
    "image_url": "",
    "color": 0x5865F2,
    "emoji": "✅",
    "verify_role_id": None,
    "verify_channel_id": None,
    "verify_message_id": None,
    "log_channel_id": None,
    "min_account_age_hours": 24,
    "use_server_emoji": False,
    "server_emoji_name": None,
    "server_emoji_id": None
}

config = {}

def save_config():
    """Guarda la configuración en un archivo JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info("✅ Configuración guardada correctamente")
    except Exception as e:
        logger.error(f"❌ Error al guardar configuración: {e}")

def load_config():
    """Carga la configuración desde el archivo JSON"""
    global config
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                config = {**default_config, **loaded}
            logger.info("✅ Configuración cargada correctamente")
        else:
            config = default_config.copy()
            save_config()
            logger.info("📝 Archivo de configuración creado con valores por defecto")
    except Exception as e:
        logger.error(f"❌ Error al cargar configuración: {e}")
        config = default_config.copy()

def get_verification_emoji(guild: discord.Guild):
    """Obtiene el emoji de verificación (del servidor o Unicode)"""
    if config.get("use_server_emoji") and config.get("server_emoji_id"):
        emoji = discord.utils.get(guild.emojis, id=int(config["server_emoji_id"]))
        if emoji:
            return emoji
    return config.get("emoji", "✅")

async def send_log(guild: discord.Guild, title: str, description: str, color: int = 0x5865F2, fields: list = None):
    """Envía un mensaje de log al canal configurado"""
    try:
        log_channel_id = config.get("log_channel_id")
        if not log_channel_id:
            return

        log_channel = guild.get_channel(int(log_channel_id))
        if not log_channel:
            logger.warning(f"⚠️ Canal de logs no encontrado: {log_channel_id}")
            return

        embed = discord.Embed(
            title=f"📋 {title}",
            description=description,
            color=color,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(
            text="Elite Verify • Sistema de Verificación",
            icon_url=guild.icon.url if guild.icon else None
        )

        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", True)
                )

        await log_channel.send(embed=embed)
    except discord.Forbidden:
        logger.error("❌ Sin permisos para enviar logs")
    except Exception as e:
        logger.error(f"❌ Error al enviar log: {e}")

@bot.event
async def on_member_join(member: discord.Member):
    """Maneja el evento cuando un nuevo miembro se une al servidor"""
    try:
        account_age = datetime.datetime.now(datetime.timezone.utc) - member.created_at
        hours = account_age.total_seconds() / 3600
        min_hours = config.get("min_account_age_hours", 24)

        if hours < min_hours:
            try:
                await member.send(
                    f"⚠️ **Cuenta Demasiado Nueva - Elite Verify**\n\n"
                    f"Tu cuenta debe tener al menos **{min_hours} horas** para unirte a **{member.guild.name}**.\n\n"
                    f"**Antigüedad actual:** {hours:.1f} horas\n"
                    f"**Requerido:** {min_hours} horas\n\n"
                    f"Intenta unirte nuevamente cuando tu cuenta cumpla con el requisito."
                )
            except discord.Forbidden:
                logger.warning(f"⚠️ No se pudo enviar DM a {member.name}")

            await member.kick(reason=f"Cuenta muy nueva (<{min_hours}h) - Elite Verify")

            await send_log(
                member.guild,
                "Usuario Expulsado - Cuenta Nueva",
                f"Usuario expulsado por tener una cuenta muy nueva.",
                0xe74c3c,
                [
                    {"name": "👤 Usuario", "value": f"{member.mention} (`{member}`)", "inline": True},
                    {"name": "🆔 ID", "value": f"`{member.id}`", "inline": True},
                    {"name": "⏰ Antigüedad", "value": f"{hours:.1f} horas", "inline": True},
                    {"name": "📅 Creado", "value": f"<t:{int(member.created_at.timestamp())}:R>", "inline": False}
                ]
            )

            logger.info(f"🚫 Usuario expulsado: {member} ({member.id}) - {hours:.1f}h")
        else:
            await send_log(
                member.guild,
                "Nuevo Miembro",
                f"Un nuevo usuario se ha unido al servidor.",
                0x2ecc71,
                [
                    {"name": "👤 Usuario", "value": f"{member.mention} (`{member}`)", "inline": True},
                    {"name": "🆔 ID", "value": f"`{member.id}`", "inline": True},
                    {"name": "📅 Se Unió", "value": f"<t:{int(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>", "inline": False}
                ]
            )
    except Exception as e:
        logger.error(f"❌ Error en on_member_join: {e}")

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Maneja el evento cuando se añade una reacción"""
    try:
        if payload.user_id == bot.user.id:
            return

        if payload.message_id != config.get("verify_message_id"):
            return

        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        emoji = get_verification_emoji(guild)

        # Comparar emojis correctamente
        if isinstance(emoji, discord.Emoji):
            if payload.emoji.id != emoji.id:
                return
        else:
            if str(payload.emoji) != emoji:
                return

        role_id = config.get("verify_role_id")
        if not role_id:
            return

        role = guild.get_role(int(role_id))
        if not role:
            logger.error(f"❌ Rol de verificación no encontrado: {role_id}")
            return

        if role in member.roles:
            logger.info(f"ℹ️ {member} ya tiene el rol de verificación")
            return

        await member.add_roles(role, reason="Verificado - Elite Verify")

        await send_log(
            guild,
            "Usuario Verificado",
            f"Un usuario se ha verificado exitosamente.",
            0x2ecc71,
            [
                {"name": "👤 Usuario", "value": f"{member.mention} (`{member}`)", "inline": True},
                {"name": "🆔 ID", "value": f"`{member.id}`", "inline": True},
                {"name": "✅ Rol", "value": f"{role.mention}", "inline": True},
                {"name": "📅 Verificado", "value": f"<t:{int(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>", "inline": False}
            ]
        )

        logger.info(f"✅ Usuario verificado: {member} ({member.id})")

        try:
            embed = discord.Embed(
                title="✅ ¡Verificación Exitosa!",
                description=f"Has sido verificado en **{guild.name}**.\n\n¡Disfruta del servidor!",
                color=0x2ecc71,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.set_footer(
                text="Elite Verify",
                icon_url=guild.icon.url if guild.icon else None
            )
            await member.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"⚠️ No se pudo enviar DM de confirmación a {member}")

    except Exception as e:
        logger.error(f"❌ Error en on_raw_reaction_add: {e}")

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    """Maneja el evento cuando se elimina una reacción"""
    try:
        if payload.message_id != config.get("verify_message_id"):
            return

        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        emoji = get_verification_emoji(guild)

        # Comparar emojis correctamente
        if isinstance(emoji, discord.Emoji):
            if payload.emoji.id != emoji.id:
                return
        else:
            if str(payload.emoji) != emoji:
                return

        role_id = config.get("verify_role_id")
        if not role_id:
            return

        role = guild.get_role(int(role_id))
        if role and role in member.roles:
            await member.remove_roles(role, reason="Reacción de verificación eliminada")

            await send_log(
                guild,
                "Verificación Removida",
                f"Verificación removida de un usuario.",
                0xf39c12,
                [
                    {"name": "👤 Usuario", "value": f"{member.mention} (`{member}`)", "inline": True},
                    {"name": "🆔 ID", "value": f"`{member.id}`", "inline": True},
                    {"name": "❌ Rol Removido", "value": f"{role.mention}", "inline": True}
                ]
            )

            logger.info(f"🔄 Verificación removida: {member} ({member.id})")
    except Exception as e:
        logger.error(f"❌ Error en on_raw_reaction_remove: {e}")

@tree.command(name="panel", description="🌐 Obtén el enlace al panel web de configuración")
@app_commands.checks.has_permissions(administrator=True)
async def panel_command(interaction: discord.Interaction):
    """Comando para obtener el enlace al panel web"""
    try:
        web_url = os.getenv("WEB_URL", "http://localhost:5000")

        embed = discord.Embed(
            title="🌐 Panel de Configuración - Elite Verify",
            description=f"Accede al panel web para configurar el sistema de verificación de forma visual.\n\n"
                       f"**🔗 Enlace:** {web_url}\n\n"
                       f"Desde el panel podrás:\n"
                       f"✅ Configurar el rol y canal de verificación\n"
                       f"✅ Personalizar el mensaje de verificación\n"
                       f"✅ Elegir emojis del servidor\n"
                       f"✅ Ver estadísticas en tiempo real\n"
                       f"✅ Publicar el mensaje de verificación",
            color=0x5865F2,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text="Elite Verify • Panel Web")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        logger.error(f"❌ Error en comando panel: {e}")
        await interaction.response.send_message(
            "❌ Error al obtener el enlace del panel.",
            ephemeral=True
        )

@tree.command(name="info", description="ℹ️ Información sobre Elite Verify")
async def info_command(interaction: discord.Interaction):
    """Muestra información sobre el bot"""
    try:
        embed = discord.Embed(
            title="ℹ️ Elite Verify - Sistema de Verificación Profesional",
            description="Bot de verificación avanzado con panel web de configuración.",
            color=0x5865F2,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        embed.add_field(
            name="✨ Características",
            value="• Panel web de configuración\n"
                  "• Emojis personalizados del servidor\n"
                  "• Protección contra cuentas nuevas\n"
                  "• Logs detallados\n"
                  "• Verificación por reacción",
            inline=False
        )

        embed.add_field(
            name="📊 Estadísticas",
            value=f"• Servidores: {len(bot.guilds)}\n"
                  f"• Usuarios: {sum(g.member_count for g in bot.guilds)}\n"
                  f"• Latencia: {round(bot.latency * 1000)}ms",
            inline=True
        )

        if interaction.user.guild_permissions.administrator:
            web_url = os.getenv("WEB_URL", "http://localhost:5000")
            embed.add_field(
                name="⚙️ Panel de Configuración",
                value=f"[Acceder al Panel]({web_url})",
                inline=True
            )

        embed.set_footer(text="Elite Verify • Desarrollado con ❤️")

        await interaction.response.send_message(embed=embed, ephemeral=False)

    except Exception as e:
        logger.error(f"❌ Error en comando info: {e}")
        await interaction.response.send_message(
            "❌ Error al mostrar información.",
            ephemeral=True
        )

@bot.event
async def on_ready():
    """Evento que se ejecuta cuando el bot está listo"""
    try:
        load_config()
        await tree.sync()

        logger.info("=" * 60)
        logger.info(f"✅ Elite Verify iniciado correctamente")
        logger.info(f"👤 Usuario: {bot.user.name} ({bot.user.id})")
        logger.info(f"📚 discord.py: {discord.__version__}")
        logger.info(f"🌐 Servidores: {len(bot.guilds)}")
        logger.info(f"📁 Config: {CONFIG_FILE}")
        logger.info("=" * 60)

        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Elite Verify • /panel para configurar"
        )
        await bot.change_presence(activity=activity, status=discord.Status.online)

    except Exception as e:
        logger.error(f"❌ Error en on_ready: {e}")

# Aplicación web con Flask
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
CORS(app)

@app.route("/")
def index():
    """Página principal del panel"""
    return render_template("index.html")

@app.route("/api/config", methods=["GET"])
def get_config():
    """Obtiene la configuración actual"""
    try:
        safe_config = config.copy()
        return jsonify({"success": True, "config": safe_config})
    except Exception as e:
        logger.error(f"❌ Error al obtener config: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/config", methods=["POST"])
def update_config():
    """Actualiza la configuración"""
    try:
        data = request.get_json()

        for key, value in data.items():
            if key in config:
                config[key] = value

        save_config()

        return jsonify({"success": True, "message": "Configuración actualizada correctamente"})
    except Exception as e:
        logger.error(f"❌ Error al actualizar config: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/guilds", methods=["GET"])
def get_guilds():
    """Obtiene información de los servidores"""
    try:
        guilds_data = []
        for guild in bot.guilds:
            guilds_data.append({
                "id": str(guild.id),  # Convertir a string
                "name": guild.name,
                "icon": str(guild.icon.url) if guild.icon else None,
                "member_count": guild.member_count
            })
        return jsonify({"success": True, "guilds": guilds_data})
    except Exception as e:
        logger.error(f"❌ Error al obtener guilds: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/guild/<guild_id>/roles", methods=["GET"])
def get_guild_roles(guild_id):
    """Obtiene los roles de un servidor"""
    try:
        logger.info(f"🔍 Buscando roles para guild_id: {guild_id} (tipo: {type(guild_id)})")

        # Convertir a int de forma segura
        try:
            guild_id_int = int(guild_id)
        except ValueError:
            logger.error(f"❌ ID de servidor inválido: {guild_id}")
            return jsonify({"success": False, "error": "ID de servidor inválido"}), 400

        guild = bot.get_guild(guild_id_int)

        if not guild:
            logger.error(f"❌ Servidor no encontrado: {guild_id_int}")
            logger.info(f"📋 Servidores disponibles: {[g.id for g in bot.guilds]}")
            return jsonify({"success": False, "error": "Servidor no encontrado"}), 404

        roles_data = []
        for role in guild.roles:
            if role.name != "@everyone":
                roles_data.append({
                    "id": str(role.id),
                    "name": role.name,
                    "color": role.color.value,
                    "position": role.position
                })

        # Ordenar por posición (más alto primero)
        roles_data.sort(key=lambda x: x["position"], reverse=True)

        logger.info(f"✅ Encontrados {len(roles_data)} roles para {guild.name}")
        return jsonify({"success": True, "roles": roles_data})
    except Exception as e:
        logger.error(f"❌ Error al obtener roles: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/guild/<guild_id>/channels", methods=["GET"])
def get_guild_channels(guild_id):
    """Obtiene los canales de un servidor"""
    try:
        logger.info(f"🔍 Buscando canales para guild_id: {guild_id}")

        try:
            guild_id_int = int(guild_id)
        except ValueError:
            return jsonify({"success": False, "error": "ID de servidor inválido"}), 400

        guild = bot.get_guild(guild_id_int)

        if not guild:
            logger.error(f"❌ Servidor no encontrado: {guild_id_int}")
            return jsonify({"success": False, "error": "Servidor no encontrado"}), 404

        channels_data = []
        for channel in guild.text_channels:
            channels_data.append({
                "id": str(channel.id),
                "name": channel.name,
                "category": channel.category.name if channel.category else "Sin categoría",
                "position": channel.position
            })

        logger.info(f"✅ Encontrados {len(channels_data)} canales para {guild.name}")
        return jsonify({"success": True, "channels": channels_data})
    except Exception as e:
        logger.error(f"❌ Error al obtener canales: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/guild/<guild_id>/emojis", methods=["GET"])
def get_guild_emojis(guild_id):
    """Obtiene los emojis personalizados de un servidor"""
    try:
        logger.info(f"🔍 Buscando emojis para guild_id: {guild_id}")

        try:
            guild_id_int = int(guild_id)
        except ValueError:
            return jsonify({"success": False, "error": "ID de servidor inválido"}), 400

        guild = bot.get_guild(guild_id_int)

        if not guild:
            logger.error(f"❌ Servidor no encontrado: {guild_id_int}")
            return jsonify({"success": False, "error": "Servidor no encontrado"}), 404

        emojis_data = []
        for emoji in guild.emojis:
            emojis_data.append({
                "id": str(emoji.id),
                "name": emoji.name,
                "url": str(emoji.url),
                "animated": emoji.animated
            })

        logger.info(f"✅ Encontrados {len(emojis_data)} emojis para {guild.name}")
        return jsonify({"success": True, "emojis": emojis_data})
    except Exception as e:
        logger.error(f"❌ Error al obtener emojis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/publish", methods=["POST"])
def publish_verification():
    """Publica el mensaje de verificación"""
    try:
        data = request.get_json()
        guild_id_str = data.get("guild_id")

        if not guild_id_str:
            return jsonify({"success": False, "error": "ID de servidor no proporcionado"}), 400

        try:
            guild_id = int(guild_id_str)
        except ValueError:
            return jsonify({"success": False, "error": "ID de servidor inválido"}), 400

        guild = bot.get_guild(guild_id)
        if not guild:
            return jsonify({"success": False, "error": "Servidor no encontrado"}), 404

        channel_id = config.get("verify_channel_id")
        role_id = config.get("verify_role_id")

        if not channel_id or not role_id:
            return jsonify({"success": False, "error": "Configura primero el rol y canal"}), 400

        channel = guild.get_channel(int(channel_id))
        if not channel:
            return jsonify({"success": False, "error": "Canal no encontrado"}), 404

        # Crear tarea asíncrona para publicar usando el loop del bot
        async def publish():
            embed = discord.Embed(
                title=config["title"],
                description=config["description"],
                color=config["color"]
            )

            if config.get("image_url"):
                embed.set_image(url=config["image_url"])

            emoji = get_verification_emoji(guild)
            emoji_text = emoji.name if isinstance(emoji, discord.Emoji) else emoji

            embed.set_footer(
                text=f"Reacciona al emoji para verificarte • Elite Verify",
                icon_url=guild.icon.url if guild.icon else None
            )

            message = await channel.send(embed=embed)
            await message.add_reaction(emoji)

            config["verify_message_id"] = message.id
            save_config()

            await send_log(
                guild,
                "Sistema de Verificación Publicado",
                "El mensaje de verificación ha sido publicado correctamente.",
                0x2ecc71,
                [
                    {"name": "📍 Canal", "value": f"{channel.mention}", "inline": True},
                    {"name": "🔰 Emoji", "value": emoji_text, "inline": True}
                ]
            )

        # Ejecutar en el loop del bot
        future = asyncio.run_coroutine_threadsafe(publish(), bot.loop)
        future.result(timeout=10)

        return jsonify({"success": True, "message": "Mensaje publicado correctamente"})
    except Exception as e:
        logger.error(f"❌ Error al publicar: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

def run_bot():
    """Ejecuta el bot en un thread separado"""
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("❌ DISCORD_BOT_TOKEN no configurado")
        return

    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"❌ Error al iniciar bot: {e}")

def run_web():
    """Ejecuta el servidor web"""
    # Railway proporciona el puerto dinámicamente
    port = int(os.getenv("PORT", 5000))
    host = "0.0.0.0"  # IMPORTANTE: debe ser 0.0.0.0, no localhost
    
    logger.info(f"🌐 Servidor web iniciando en {host}:{port}")
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == "__main__":
    try:
        logger.info("🚀 Iniciando Elite Verify...")
        
        # Iniciar bot en thread separado
        bot_thread = Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        # Esperar a que el bot se conecte
        import time
        time.sleep(5)
        
        # Iniciar servidor web (Railway asigna el puerto automáticamente)
        run_web()
        
    except KeyboardInterrupt:
        logger.info("⚠️ Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")

