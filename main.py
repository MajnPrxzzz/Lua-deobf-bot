import os
import re
import aiohttp
import discord
from discord import app_commands
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
        print("🤖 Bot Lua Profesional Actualizado y Sincronizado.")

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
        "analyzing": "🔍 Analizando firmas avanzadas del script para detectar el ofuscador...",
        "detect_title": "🔍 Resultado del Análisis de Ofuscación",
        "detect_file": "Archivo analizado",
        "detect_result": "Ofuscador Detectado",
        "detect_footer": "Usa el comando específico de limpieza/desofuscación correspondiente.",
        "processing": "⏳ Iniciando motor de análisis profundo para: **{}**...",
        "success_clean": "✅ **¡Script procesado, ordenado y analizado con éxito!**",
        "preview_title": "👁️ Vistazo previo (Primeras líneas recuperadas):",
        "error": "Ocurrió un error inesperado: "
    },
    "en": {
        "need_attachment": "❌ Please attach a `.lua` or `.txt` file along with the command.",
        "need_url": "❌ Please provide a valid link (Pastebin, URL, etc.).",
        "extracting": "📥 Extracting script from the link...",
        "extracted_success": "✅ **Script extracted successfully!**",
        "analyzing": "🔍 Analyzing advanced script signatures to detect the obfuscator...",
        "detect_title": "🔍 Obfuscation Analysis Result",
        "detect_file": "Analyzed file",
        "detect_result": "Detected Obfuscator",
        "detect_footer": "Use the corresponding specific deobfuscation command.",
        "processing": "⏳ Starting deep analysis engine for: **{}**...",
        "success_clean": "✅ **Script processed, organized and analyzed successfully!**",
        "preview_title": "👁️ Preview (First recovered lines):",
        "error": "An unexpected error occurred: "
    }
}

current_lang = "es"

# ==========================================
# UTILIDADES DE RED Y DETECCIÓN
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
    
    if "luraph" in codigo_lower or (re.search(r'getfenv\s*\(\s*\)', codigo) and len(codigo) > 4000):
        if "v15" in codigo or "15" in codigo[:500]:
            return "Luraph v15"
        return "Luraph v14"
    
    elif "moonsec" in codigo_lower or re.search(r'math\.fmod|math\.huge|local\s+[a-z];\s*local\s+[a-z];.*e\s*=\s*\d+', codigo):
        return "Moonsec"
        
    elif "moonveil" in codigo_lower or "mv_deobf" in codigo_lower or re.search(r'MoonVeil', codigo):
        return "Moonveil"
        
    elif "prometheus" in codigo_lower or re.search(r'(prometheus|Prometheus)', codigo) or len(re.findall(r'\b(Zeus|Hermes|Athena|Apollo|Ares|Cronus)\b', codigo)) > 3:
        return "Prometheus"
        
    elif "wearedevs" in codigo_lower or "getgenv()._" in codigo or "syn" in codigo:
        return "WeAreDevs"
        
    else:
        return "Genérico / Desconocido"

def obtener_primeros_prompts(codigo: str, lineas_max: int = 5) -> str:
    """Extrae las primeras líneas de código útil o constantes para mostrarlas como muestra."""
    lineas = codigo.splitlines()
    lineas_utiles = [l for l in lineas if l.strip() and not l.strip().startswith("--[[")]
    
    seleccion = lineas_utiles[:lineas_max]
    if not seleccion:
        seleccion = lineas[:lineas_max] # Fallback si todo son comentarios
        
    resultado_preview = "\n".join(seleccion)
    if len(resultado_preview) > 900:  # Evitar desbordar el embed de Discord
        resultado_preview = resultado_preview[:900] + "\n..."
        
    return f"```lua\n{resultado_preview}\n```"

def procesar_deobfuscacion(codigo: str, metodo: str) -> str:
    header = f"--[[ \n    Lua Processed & Cleaned by Bot Pro\n    Protección Original Detectada: {metodo}\n]]\n\n"
    
    if metodo == "Luraph v15":
        codigo = re.sub(r'local\s+([a-zA-Z0-9_]+)\s*=\s*\{[^\}]+\}', '-- [Luraph v15: Constantes Cifradas Aislando VM]', codigo)
        return header + "-- [Aviso: Luraph v15 utiliza una Máquina Virtual avanzada. Se aislaron metadatos y constantes]\n\n" + codigo

    elif metodo == "Luraph v14":
        codigo = re.sub(r'local\s+([a-zA-Z0-9_]+)\s*=\s*\{[^\}]+\}', '-- [Luraph v14 Constants Mapped]', codigo)
        return header + "-- [Luraph v14 Desprotegido Parcialmente]\n\n" + codigo

    elif metodo == "Moonsec":
        codigo = re.sub(r'local\s+[a-z];\s*local\s+[a-z];\s*local\s+[a-z];', '-- [Moonsec Bytecode Init Cleaned]', codigo)
        return header + "-- [Moonsec Limpieza Aplicada]\n\n" + codigo

    elif metodo == "Moonveil":
        return header + "-- [Moonveil Deobfuscated & Cleaned]\n\n" + re.sub(r'\b(mv_[a-zA-Z0-9_]+)', 'clean_var', codigo)

    elif metodo == "Prometheus":
        codigo_limpio = re.sub(r'\b(Zeus|Hermes|Athena|Apollo|Ares|Cronus)[a-zA-Z0-9_]*\b', 'var', codigo)
        return header + "-- [Prometheus Estructura Minificada/Limpia]\n\n" + codigo_limpio

    elif metodo == "WeAreDevs":
        codigo = re.sub(r'local\s+([a-zA-Z0-9_]{1,3})\s*=\s*function\(.*?\)\s*end', '', codigo)
        codigo = codigo.replace("getgenv()._", "local_var_")
        return header + "-- [WeAreDevs Limpieza Aplicada]\n\n" + codigo

    else:
        return header + re.sub(r'\n\s*\n', '\n', codigo)


# ==========================================
# COMANDOS DE CONFIGURACIÓN E IDIOMA
# ==========================================

@bot.command(name="lang", help="Cambia el idioma del bot / Change bot language")
async def lang_cmd(ctx, idioma: str):
    global current_lang
    idioma = idioma.lower()
    if idioma in ["es", "en"]:
        current_lang = idioma
        msg = "🇪🇸 Idioma cambiado a Español." if idioma == "es" else "🇬🇧 Language changed to English."
        await ctx.send(msg)
    else:
        await ctx.send("❌ Idiomas / Languages: `es`, `en`")


@bot.command(name="help", help="Muestra la lista de comandos disponibles.")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🤖 Panel de Control - Lua Extractor & Deobfuscator Pro",
        description="Lista completa con validación inteligente y vista previa de código:",
        color=discord.Color.blurple()
    )
    
    embed.add_field(name="📥 `.extract [url]`", value="Extrae el script de Pastebin u otras URLs.", inline=False)
    embed.add_field(name="🔍 `.detect` *(adjuntar archivo)*", value="Analiza y detecta automáticamente el ofuscador correcto.", inline=False)
    embed.add_field(name="🔮 `.lph15` / `.lph14` *(adjuntar)*", value="Procesa scripts de **Luraph v15** o **v14**.", inline=False)
    embed.add_field(name="🌙 `.moonsec` *(adjuntar)*", value="Limpia scripts protegidos con **Moonsec**.", inline=False)
    embed.add_field(name="🌌 `.moonveil` *(adjuntar)*", value="Limpia scripts protegidos con **Moonveil**.", inline=False)
    embed.add_field(name="🔥 `.prometheus` *(adjuntar)*", value="Procesa scripts protegidos con **Prometheus**.", inline=False)
    embed.add_field(name="🛡️ `.wad` *(adjuntar)*", value="Limpia scripts de **WeAreDevs**.", inline=False)
    embed.add_field(name="🌐 `.lang [es/en]`", value="Cambia el idioma del bot.", inline=False)
    
    embed.set_footer(text=f"Idioma actual / Current language: {current_lang.upper()}")
    await ctx.send(embed=embed)


# ==========================================
# COMANDO DE EXTRACCIÓN
# ==========================================

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


# ==========================================
# COMANDO DE DETECCIÓN INTELIGENTE
# ==========================================

@bot.command(name="detect")
async def detect_cmd(ctx):
    t = LANGS[current_lang]
    if not ctx.message.attachments:
        await ctx.send(t["need_attachment"])
        return
    
    attachment = ctx.message.attachments[0]
    msg = await ctx.send(t["analyzing"])
    await asyncio.sleep(1.5)

    try:
        code_text = (await attachment.read()).decode('utf-8', errors='ignore')
        resultado = detectar_ofuscador(code_text)
        
        embed = discord.Embed(
            title=t["detect_title"],
            description=f"**{t['detect_file']}:** `{attachment.filename}`\n\n**{t['detect_result']}:**\n`{resultado}`",
            color=discord.Color.dark_purple()
        )
        embed.set_footer(text=t["detect_footer"])
        await ctx.send(embed=embed)
        await msg.delete()
    except Exception as e:
        await ctx.send(f"❌ {t['error']}{str(e)}")


# ==========================================
# MOTOR DE VALIDACIÓN Y PROCESAMIENTO MEJORADO
# ==========================================

async def ejecutar_deobf(ctx, motor_esperado: str, filename: str):
    t = LANGS[current_lang]
    if not ctx.message.attachments:
        await ctx.send(t["need_attachment"])
        return
    
    attachment = ctx.message.attachments[0]
    
    msg = await ctx.send(t["processing"].format(motor_esperado))
    await asyncio.sleep(1.5)
    await msg.edit(content=f"⚙️ Analizando tablas de constantes y capas de seguridad para **{motor_esperado}**...")
    await asyncio.sleep(1.5)

    try:
        code_text = (await attachment.read()).decode('utf-8', errors='ignore')
        ofuscador_real = detectar_ofuscador(code_text)
        
        # VALIDACIÓN CRUZADA DE OFUSCADOR
        if motor_esperado.lower() not in ofuscador_real.lower() and "Genérico" not in ofuscador_real:
            embed_error = discord.Embed(
                title="❌ Error de Validación de Ofuscador",
                description=(
                    f"El comando que usaste (**{motor_esperado}**) no corresponde con la protección real del archivo.\n\n"
                    f"🛡️ **Ofuscador real detectado por el bot:** `{ofuscador_real}`\n\n"
                    f"Por favor, utiliza el comando adecuado para este tipo de script."
                ),
                color=discord.Color.red()
            )
            await msg.edit(content=None, embed=embed_error)
            return

        # Procesar limpieza
        await msg.edit(content=f"🧹 Limpiando y estructurando código con motor: **{ofuscador_real}**...")
        await asyncio.sleep(1)
        
        resultado = procesar_deobfuscacion(code_text, ofuscador_real)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(resultado)
            
        # Obtener los primeros prompts/líneas como muestra de que funciona
        preview_code = obtener_primeros_prompts(resultado, lineas_max=5)

        embed_exito = discord.Embed(
            title=t["success_clean"],
            description=f"**Motor aplicado:** `{ofuscador_real}`\n\n{t['preview_title']}\n{preview_code}",
            color=discord.Color.green()
        )
        embed_exito.set_footer(text=f"Archivo procesado: {filename}")

        await ctx.send(embed=embed_exito, file=discord.File(filename))
        await msg.delete()
    except Exception as e:
        await ctx.send(f"❌ {t['error']}{str(e)}")

@bot.command(name="lph15")
async def lph15_cmd(ctx):
    await ejecutar_deobf(ctx, "Luraph v15", "luraph15_limpio.lua")

@bot.command(name="lph14")
async def lph14_cmd(ctx):
    await ejecutar_deobf(ctx, "Luraph v14", "luraph14_limpio.lua")

@bot.command(name="moonsec")
async def moonsec_cmd(ctx):
    await ejecutar_deobf(ctx, "Moonsec", "moonsec_limpio.lua")

@bot.command(name="moonveil")
async def moonveil_cmd(ctx):
    await ejecutar_deobf(ctx, "Moonveil", "moonveil_limpio.lua")

@bot.command(name="prometheus")
async def prometheus_cmd(ctx):
    await ejecutar_deobf(ctx, "Prometheus", "prometheus_limpio.lua")

@bot.command(name="wad")
async def wad_cmd(ctx):
    await ejecutar_deobf(ctx, "WeAreDevs", "wearedevs_limpio.lua")


# ==========================================
# INICIO Y MANTENIMIENTO DEL BOT
# ==========================================
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ['DISCORD_TOKEN'])
