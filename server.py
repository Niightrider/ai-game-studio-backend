import os
import re
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

app = FastAPI(title="AI Game Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración del cliente Groq (puedes probar a poner la clave aquí temporalmente si en Render falla la variable)
API_KEY = os.environ.get("GROQ_API_KEY", "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")

client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

class GameRequest(BaseModel):
    prompt: str
    style: str = "pixel_art"

@app.post("/generate-game")
async def generate_game(request: GameRequest):
    try:
        system_prompt = (
            "Eres un desarrollador experto en Phaser 3. "
            "Genera ÚNICAMENTE código JavaScript plano y ejecutable para un juego arcade en 2D. "
            "REGLAS OBLIGATORIAS:\n"
            "1. NO uses bloques de markdown como ```javascript o ```. Devuelve SOLO el código JS puro.\n"
            "2. CONFIGURACIÓN DE PHASER:\n"
            "   const config = {\n"
            "       type: Phaser.AUTO,\n"
            "       parent: 'game-container',\n"
            "       scale: {\n"
            "           mode: Phaser.Scale.FIT,\n"
            "           autoCenter: Phaser.Scale.CENTER_BOTH,\n"
            "           width: 800,\n"
            "           height: 600\n"
            "       },\n"
            "       physics: { default: 'arcade', arcade: { gravity: { y: 0 }, debug: false } },\n"
            "       scene: { preload: preload, create: create, update: update }\n"
            "   };\n"
            "   if (window.currentGame) { window.currentGame.destroy(true); }\n"
            "   window.currentGame = new Phaser.Game(config);\n"
            "3. Declara las funciones preload(), create() y update() de forma limpia.\n"
            "4. Dibuja los gráficos usando 'this.add.graphics()' y programa los controles táctiles con 'this.input.on(\"pointermove\", ...)'."
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.prompt}
            ],
            temperature=0.6
        )

        raw_code = response.choices[0].message.content

        # Limpieza estricta de bloques Markdown
        cleaned_code = re.sub(r"^```(?:javascript|js)?\n?", "", raw_code, flags=re.MULTILINE)
        cleaned_code = re.sub(r"```$", "", cleaned_code, flags=re.MULTILINE).strip()

        return {
            "status": "success",
            "prompt": request.prompt,
            "style": request.style,
            "code": cleaned_code
        }

    except Exception as e:
        error_detalles = traceback.format_exc()
        print(error_detalles) # Se verá en los Logs de Render
        raise HTTPException(status_code=500, detail=error_detalles)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
