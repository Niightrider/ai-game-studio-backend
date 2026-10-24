import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="AI Game Studio Multi-Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar cliente oficial de Groq
client = Groq()

class GameRequest(BaseModel):
    prompt: str
    style: str = "pixel_art"

@app.post("/generate-game")
async def generate_game(request: GameRequest):
    try:
        # --- PASO 1: AGENTE PROGRAMADOR (Lógica base) ---
        prompt_coder = (
            "Eres un programador experto en Phaser 3. "
            "Crea la estructura lógica y el bucle de un juego arcade en 2D basado en esta idea: " + request.prompt + ". "
            "Usa la configuración estándar de Phaser con scale FIT, width 800, height 600. "
            "Devuelve SOLO el código JS base, sin markdown."
        )
        res1 = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt_coder}],
            temperature=0.3,
            max_completion_tokens=1500
        )
        base_code = res1.choices[0].message.content

        # --- PASO 2: AGENTE DISEÑADOR VISUAL (Gráficos avanzados sin CORS) ---
        prompt_designer = (
            "Eres un artista visual y diseñador de videojuegos. Toma este código de Phaser 3 y enriquece los elementos visuales "
            "utilizando 'this.add.graphics()', formas geométricas detalladas, colores vivos, efectos de brillo y partículas internas. "
            "NO uses URLs externas de imágenes para evitar fallos de red. Todo debe dibujarse mediante código gráfico interno. "
            "Código base:\n" + base_code + "\n"
            "Devuelve SOLO el código JS mejorado visualmente, sin markdown."
        )
        res2 = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt_designer}],
            temperature=0.4,
            max_completion_tokens=1500
        )
        styled_code = res2.choices[0].message.content

        # --- PASO 3: AGENTE AUDITOR / DEPURADOR (Corrección de sintaxis) ---
        prompt_reviewer = (
            "Eres un revisor de código experto en JavaScript y Phaser 3. "
            "Revisa exhaustivamente el siguiente código, corrige cualquier error de sintaxis (como asignaciones inválidas en el lado izquierdo tipo 'a+b=c') "
            "y asegúrate de que la inicialización del juego y las funciones preload, create y update estén perfectamente estructuradas y limpias. "
            "Código a revisar:\n" + styled_code + "\n"
            "REGLA ABSOLUTA: Devuelve ÚNICAMENTE el código JavaScript final, limpio y 100% ejecutable, sin ningún bloque de markdown ni texto adicional."
        )
        res3 = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt_reviewer}],
            temperature=0.1,
            max_completion_tokens=2000
        )
        final_code = res3.choices[0].message.content

        # Limpieza estricta de seguridad contra bloques markdown
        cleaned_code = re.sub(r"^```(?:javascript|js)?\n?", "", final_code, flags=re.MULTILINE)
        cleaned_code = re.sub(r"```$", "", cleaned_code, flags=re.MULTILINE).strip()

        return {
            "status": "success",
            "prompt": request.prompt,
            "style": request.style,
            "code": cleaned_code
        }

    except Exception as e:
        print(f"Error en pipeline multi-agente: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
