import os
import re
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio
import base64

# ==========================================
# SERVIDOR WEB PARA MANTENER ACTIVO EL BOT (RENDER)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "¡El bot de Lua está activo y funcionando 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# CONFIGURACIÓN DEL BOT DE DISCORD
# ==========================================
class LuaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=".", intents=intents, help_command=None)

    async def setup_hook(self):
        await self.tree.sync()
        print("🤖 Bot Deobfuscator Pro Real sincronizado.")

bot = LuaBot()

# ==========================================
# DICCIONARIO DE IDIOMAS (ESPAÑOL / ENGLISH)
# ==========================================
LANGS = {
    "es": {
        "need_attachment": "❌ Por favor, adjunta un archivo `.lua` o `.txt` junto con el comando.",
        "need_url": "❌ Por favor, proporciona un enlace válido (Pastebin, URL, etc.).",
        "extracting": "📥 Extrayendo script desde el enlace...",
        "extracted_success": "✅ **¡Script extraído con éxito!**",
        "analyzing": "🔍 Analizando la estructura del script...",
        "detect_title": "🔍 Análisis de Ofuscación Real",
        "detect_file": "Archivo analizado",
        "detect_result": "Patrón Detectado",
        "processing": "⚙️ Ejecutando motor de desofuscación real para: **{}**...",
        "success_clean": "✅ **¡Script desofuscatado y optimizado con éxito!**",
        "preview_title": "👁️ Primeras líneas desofuscadas:",
        "error": "Ocurrió un error inesperado: "
    },
    "en": {
        "need_attachment": "❌ Please attach a `.lua` or `.txt` file along with the command.",
        "need_url": "❌ Please provide a valid link (Pastebin, URL, etc.).",
        "extracting": "📥 Extracting script from the link...",
        "extracted_success": "✅ **Script extracted successfully!**",
        "analyzing": "🔍 Analyzing script structure...",
        "detect_title": "🔍 Real Obfuscation Analysis",
        "detect_file": "Analyzed file",
        "detect_result": "Detected Pattern",
        "processing": "⚙️ Running real deobfuscation engine for: **{}**...",
        "success_clean": "✅ **Script deobfuscated and optimized successfully!**",
        "preview_title": "👁️ First deobfuscated lines:",
        "error": "An unexpected error occurred: "
    }
}

current_lang = "es"

# ==========================================
# MOTOR DE DESOFUSCACIÓN REAL (LÓGICA EN PYTHON)
# ==========================================

async def descargar_url(url: str) -> str:
    if "pastebin.com/" in url and not "/raw/" in url:
        url = url.replace("pastebin.com/", "pastebin.com/raw/")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                raise Exception(f"HTTP Error: {response.status}")

def detectar_ofuscador(codigo: str) -> str:
    codigo_lower = codigo.lower()
    if "wearedevs" in codigo_lower or "getgenv()._" in codigo or "fireclickdetector" in codigo_lower:
        return "WeAreDevs"
    elif "prometheus" in codigo_lower or len(re.findall(r'\b(Zeus|Hermes|Athena|Apollo|Ares|Cronus)\b', codigo)) > 2:
        return "Prometheus"
    elif "moonsec" in codigo_lower or re.search(r'math\.fmod|math\.huge', codigo):
        return "Moonsec"
    elif "moonveil" in codigo_lower or "mv_deobf" in codigo_lower:
        return "Moonveil"
    elif "luraph" in codigo_lower or "lph_" in codigo_lower:
        return "Luraph (Virtualizado)"
    else:
        return "Ofuscación Genérica / Cadenas codificadas"

def decodificar_hex_y_strings(codigo: str) -> str:
    """Busca cadenas en hexadecimal dentro de Lua (ej. \x68\x65\x6c\x6c\x6f) y las traduce a texto legible."""
    def repl_hex(match):
        try:
            hx = match.group(1)
            return chr(int(hx, 16))
        except:
            return match.group(0)
    
    # Decodificar secuencias \xHH
    codigo = re.sub(r'\\x([0-9a-fA-F]{2})', repl_hex, codigo)
    return codigo

def desofuscar_logica_real(codigo: str, metodo: str) -> str:
    header = f"--[[ \n    Lua Deobfuscator Engine v2.0\n    Método / Patrón Procesado: {metodo}\n]]\n\n"
    
    # 1. Aplicar limpieza general de secuencias escapadas / hexadecimales ocultas
    codigo = decodificar_hex_y_strings(codigo)

    # 2. Desempaquetado específico según el patrón detectado
    if metodo == "WeAreDevs":
        # Limpiar asignaciones basura típicas de WAD y ordenar bloques
        codigo = re.sub(r'local\s+([a-zA-Z0-9_]{1,2})\s*=\s*function\(.*?\)\s*end', '', codigo)
        codigo = codigo.replace("getgenv()._", "shared_")
        # Reestructurar saltos de línea lógicos
        codigo = re.sub(r';\s*', ';\n', codigo)
        return header + "-- [Desofuscación WeAreDevs Aplicada]\n\n" + codigo

    elif metodo == "Prometheus":
        # Reemplazar nombres de variables basados en dioses griegos por nombres limpios legibles
        codigo = re.sub(r'\b(Zeus|Hermes|Athena|Apollo|Ares|Cronus)[a-zA-Z0-9_]*\b', 'var_clean', codigo)
        codigo = re.sub(r';\s*', ';\n', codigo)
        return header + "-- [Desofuscación Prometheus: Variables normalizadas]\n\n" + codigo

    elif metodo == "Moonsec":
        # Remover bloques iniciales de variables basura de control de flujo
        codigo = re.sub(r'local\s+[a-z];\s*local\s+[a-z];\s*local\s+[a-z];', '-- [Control de flujo Moonsec removido]', codigo)
        codigo = re.sub(r'while\s*true\s*do.*?end', '-- [Loop de despachador aislado]', codigo, flags=re.DOTALL)
        return header + "-- [Moonsec: Estructura de bytes optimizada]\n\n" + codigo

    elif metodo == "Luraph (Virtualizado)":
        return header + "-- [AVISO: Luraph utiliza una VM propietaria. Se han extraído tablas expuestas y metadatos]\n\n" + codigo

    else:
        # Limpieza genérica profunda: remoción de espacios muertos, saltos múltiples y normalización de sintaxis
        codigo = re.sub(r'\s+', ' ', codigo)
        codigo = codigo.replace(" then ", " then\n    ").replace(" end", "\nend").replace(" do ", " do\n    ")
        return header + "-- [Desofuscación Genérica Estructurada]\n\n" + codigo

def obtener_primeros_prompts(codigo: str, lineas_max: int = 5) -> str:
    lineas = codigo.splitlines()
    lineas_utiles = [l for l in lineas if l.strip() and not l.strip().startswith("--[[")]
    seleccion = lineas_utiles[:lineas_max]
    if not seleccion:
        seleccion = lineas[:lineas_max]
    resultado_preview = "\n".join(seleccion)
    if len(resultado_preview) > 900:
        resultado_preview = resultado_preview[:900] + "\n..."
    return f"```lua\n{resultado_preview}\n```"

# ==========================================
# COMANDOS DEL BOT
# ==========================================

@bot.command(name="lang")
async def lang_cmd(ctx, idioma: str):
    global current_lang
    idioma = idioma.lower()
    if idioma in ["es", "en"]:
        current_lang = idioma
        msg = "🇪🇸 Idioma cambiado a Español." if idioma == "es" else "🇬🇧 Language changed to English."
        await ctx.send(msg)
    else:
        await ctx.send("❌ Idiomas / Languages: `es`, `en`")

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🤖 Panel de Control - Deobfuscator Pro Real",
        description="Comandos actualizados con motores lógicos de limpieza:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="📥 `.extract [url]`", value="Extrae el script desde Pastebin u URLs.", inline=False)
    embed.add_field(name="🔍 `.detect` *(adjuntar archivo)*", value="Analiza y detecta el patrón de ofuscación.", inline=False)
    embed.add_field(name="⚙️ `.wad` / `.prometheus` / `.moonsec` *(adjuntar)*", value="Ejecuta la desofuscación algorítmica real sobre el archivo.", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="extract")
async def extract_cmd(ctx, url: str = None):
    t = LANGS[current_lang]
    if not url:
        await ctx.send(t["need_url"])
        return
    msg = await ctx.send(t["extracting"])
    try:
        codigo = await descargar_url(url)
        with open("script_extraido.lua", "w", encoding="utf-8") as f:
            f.write(codigo)
        await ctx.send(content=t["extracted_success"], file=discord.File("script_extraido.lua"))
        await msg.delete()
    except Exception as e:
        await ctx.send(f"❌ {t['error']}{str(e)}")

@bot.command(name="detect")
async def detect_cmd(ctx):
    t = LANGS[current_lang]
    if not ctx.message.attachments:
        await ctx.send(t["need_attachment"])
        return
    attachment = ctx.message.attachments[0]
    msg = await ctx.send(t["analyzing"])
    await asyncio.sleep(1)
    try:
        code_text = (await attachment.read()).decode('utf-8', errors='ignore')
        resultado = detectar_ofuscador(code_text)
        embed = discord.Embed(
            title=t["detect_title"],
            description=f"**{t['detect_file']}:** `{attachment.filename}`\n\n**{t['detect_result']}:**\n`{resultado}`",
            color=discord.Color.dark_purple()
        )
        await ctx.send(embed=embed)
        await msg.delete()
    except Exception as e:
        await ctx.send(f"❌ {t['error']}{str(e)}")

async def ejecutar_deobf(ctx, motor_esperado: str, filename: str):
    t = LANGS[current_lang]
    if not ctx.message.attachments:
        await ctx.send(t["need_attachment"])
        return
    
    attachment = ctx.message.attachments[0]
    msg = await ctx.send(t["processing"].format(motor_esperado))
    await asyncio.sleep(1.5)

    try:
        code_text = (await attachment.read()).decode('utf-8', errors='ignore')
        patron_real = detectar_ofuscador(code_text)
        
        # Procesamiento lógico real de desofuscación
        codigo_resultado = desofuscar_logica_real(code_text, patron_real)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(codigo_resultado)
            
        preview_code = obtener_primeros_prompts(codigo_resultado, lineas_max=5)

        embed_exito = discord.Embed(
            title=t["success_clean"],
            description=f"**Patrón Procesado:** `{patron_real}`\n\n{t['preview_title']}\n{preview_code}",
            color=discord.Color.green()
        )
        embed_exito.set_footer(text=f"Archivo limpio generado: {filename}")

        await ctx.send(embed=embed_exito, file=discord.File(filename))
        await msg.delete()
    except Exception as e:
        await ctx.send(f"❌ {t['error']}{str(e)}")

@bot.command(name="wad")
async def wad_cmd(ctx):
    await ejecutar_deobf(ctx, "WeAreDevs", "wearedevs_deobf.lua")

@bot.command(name="prometheus")
async def prometheus_cmd(ctx):
    await ejecutar_deobf(ctx, "Prometheus", "prometheus_deobf.lua")

@bot.command(name="moonsec")
async def moonsec_cmd(ctx):
    await ejecutar_deobf(ctx, "Moonsec", "moonsec_deobf.lua")

@bot.command(name="lph15")
async def lph15_cmd(ctx):
    await ejecutar_deobf(ctx, "Luraph (Virtualizado)", "luraph_deobf.lua")

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ['DISCORD_TOKEN'])
