import os
import re
import io
import aiohttp
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio

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
        print("🤖 Bot Deobfuscator Pro Definitivo sincronizado.")

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
        "analyzing": "🔍 Analizando y purgando bloques numéricos de ofuscación...",
        "detect_title": "🔍 Análisis del Motor de Limpieza",
        "detect_file": "Archivo analizado",
        "detect_result": "Patrón Identificado",
        "processing": "⚙️ Ejecutando purga total de números basura y reestructuración para: **{}**...",
        "success_clean": "✅ **¡Script completamente limpio y ordenado con éxito!**",
        "preview_title": "👁️ Primeras líneas limpias:",
        "error": "Ocurrió un error inesperado: "
    },
    "en": {
        "need_attachment": "❌ Please attach a `.lua` or `.txt` file along with the command.",
        "need_url": "❌ Please provide a valid link (Pastebin, URL, etc.).",
        "extracting": "📥 Extracting script from the link...",
        "extracted_success": "✅ **Script extracted successfully!**",
        "analyzing": "🔍 Analyzing and purging numeric obfuscation blocks...",
        "detect_title": "🔍 Cleaning Engine Analysis",
        "detect_file": "Analyzed file",
        "detect_result": "Identified Pattern",
        "processing": "⚙️ Executing total garbage number purge and restructuring for: **{}**...",
        "success_clean": "✅ **Script completely cleaned and ordered successfully!**",
        "preview_title": "👁️ First clean lines:",
        "error": "An unexpected error occurred: "
    }
}

current_lang = "es"

# ==========================================
# MOTOR DE PURGA Y LIMPIEZA PROFUNDA DE NÚMEROS
# ==========================================

async def descargar_url(url: str) -> str:
    if "pastebin.com/" in url and not "/raw/" in url:
        url = url.replace("pastebin.com/", "pastebin.com/raw/")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as response:
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
        return "Ofuscación Estándar / Tablas Numéricas"

def purgar_numeros_basura(codigo: str) -> str:
    codigo = re.sub(r'local\s+[a-zA-Z0-9_]+\s*=\s*\{[\d,\s\.\-\n]+\};?', '-- [Tabla numérica de bytes purgada]', codigo)
    
    def limpiar_matriz(match):
        bloque = match.group(0)
        digitos = len(re.findall(r'\d', bloque))
        if digitos > (len(bloque) * 0.35):
            return '{ --[[Bytes ofuscados eliminados]] }'
        return bloque

    codigo = re.sub(r'\{[^{}]*\}', limpiar_matriz, codigo)

    def repl_hex(match):
        try:
            return chr(int(match.group(1), 16))
        except:
            return match.group(0)
            
    codigo = re.sub(r'\\x([0-9a-fA-F]{2})', repl_hex, codigo)
    return codigo

def desofuscar_y_ordenar_absoluto(codigo: str, metodo: str) -> str:
    header = f"--[[ \n    Lua Ultimate Deobfuscator & Cleaner\n    Patrón Detectado: {metodo}\n]]\n\n"
    codigo = purgar_numeros_basura(codigo)

    if metodo == "WeAreDevs":
        codigo = re.sub(r'local\s+([a-zA-Z0-9_]{1,2})\s*=\s*function\(.*?\)\s*end', '', codigo)
        codigo = codigo.replace("getgenv()._", "shared_")
    elif metodo == "Prometheus":
        codigo = re.sub(r'\b(Zeus|Hermes|Athena|Apollo|Ares|Cronus)[a-zA-Z0-9_]*\b', 'variable_limpia', codigo)
    elif metodo == "Moonsec":
        codigo = re.sub(r'while\s*true\s*do.*?end', '-- [Loop de control Moonsec eliminado]', codigo, flags=re.DOTALL)

    codigo = re.sub(r'[ \t]+', ' ', codigo)
    codigo = re.sub(r'\n\s*\n', '\n\n', codigo)
    
    codigo = codigo.replace(" then ", " then\n    ")
    codigo = codigo.replace(" do ", " do\n    ")
    codigo = codigo.replace(" else ", "\nelse\n    ")
    codigo = codigo.replace(" end", "\nend")
    codigo = codigo.replace(";", ";\n")

    return header + codigo

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
        title="🤖 Panel de Control - Deobfuscator Definitivo",
        description="Comandos con purga activa de tablas numéricas y ordenamiento:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="📥 `.extract [url]`", value="Extrae el script desde Pastebin u URLs.", inline=False)
    embed.add_field(name="🔍 `.detect` *(adjuntar archivo)*", value="Analiza y detecta el patrón del script.", inline=False)
    embed.add_field(name="⚙️ `.wad` / `.prometheus` / `.moonsec` / `.lph15` *(adjuntar)*", value="Ejecuta la limpieza absoluta eliminando los números de ofuscación.", inline=False)
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
        file_bytes = io.BytesIO(codigo.encode('utf-8'))
        file_bytes.seek(0)
        
        await ctx.send(content=t["extracted_success"], file=discord.File(file_bytes, filename="script_extraido.lua"))
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
        
        codigo_resultado = desofuscar_y_ordenar_absoluto(code_text, patron_real)
        
        # Uso de BytesIO para evitar conflictos de concurrencia en archivos locales
        file_bytes = io.BytesIO(codigo_resultado.encode('utf-8'))
        file_bytes.seek(0)
            
        preview_code = obtener_primeros_prompts(codigo_resultado, lineas_max=5)

        embed_exito = discord.Embed(
            title=t["success_clean"],
            description=f"**Patrón Procesado:** `{patron_real}`\n\n{t['preview_title']}\n{preview_code}",
            color=discord.Color.green()
        )
        embed_exito.set_footer(text=f"Archivo limpio generado: {filename}")

        await ctx.send(embed=embed_exito, file=discord.File(file_bytes, filename=filename))
        await msg.delete()
    except Exception as e:
        await ctx.send(f"❌ {t['error']}{str(e)}")

@bot.command(name="wad")
async def wad_cmd(ctx):
    await ejecutar_deobf(ctx, "WeAreDevs", "script_limpio.lua")

@bot.command(name="prometheus")
async def prometheus_cmd(ctx):
    await ejecutar_deobf(ctx, "Prometheus", "script_limpio.lua")

@bot.command(name="moonsec")
async def moonsec_cmd(ctx):
    await ejecutar_deobf(ctx, "Moonsec", "script_limpio.lua")

@bot.command(name="lph15")
async def lph15_cmd(ctx):
    await ejecutar_deobf(ctx, "Luraph (Virtualizado)", "script_limpio.lua")

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ['DISCORD_TOKEN'])
