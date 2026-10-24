import os
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

# Configuramos Groq (Gratuito y compatible con el formato OpenAI)
client = openai.OpenAI(
    api_key=os.environ.get("GROQ_API_KEY", "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"),
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
            "4. CONTROLES TÁCTILES: Usa 'this.input.on(\"pointermove\", ...)' o 'pointerdown' para mover al personaje con el dedo.\n"
            "5. Incluye puntuación, colisiones y lógica de juego completa."
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.prompt}
            ],
            temperature=0.7
        )

        game_logic_code = response.choices[0].message.content

        return {
            "status": "success",
            "prompt": request.prompt,
            "style": request.style,
            "code": game_logic_code
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
