import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="AI Game Generator API")

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
    system_prompt = (
        "Eres un desarrollador experto en Phaser 3. "
        "Genera ÚNICAMENTE código JavaScript plano, moderno y sintácticamente perfecto para un juego arcade en 2D. "
        "REGLAS ABSOLUTAS DE SINTAXIS Y FORMATO:\n"
        "1. NO uses bloques de markdown como ```javascript o ```. Devuelve SOLO el código JS puro, sin ningún texto ni formato adicional.\n"
        "2. NUNCA escribas asignaciones inválidas en el lado izquierdo. Por ejemplo, JAMÁS escribas expresiones como 'a + b = c' o 'funcion() = 5'. Usa siempre asignaciones de variables directas y correctas (ej: 'score += 1' o 'player.x = 100').\n"
        "3. CONFIGURACIÓN OBLIGATORIA DE PHASER:\n"
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
        "4. Define de forma limpia, separada e independiente las funciones preload(), create() y update()."
    )

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.prompt}
            ],
            temperature=0.4,
            max_completion_tokens=2048,
            top_p=1
        )

        raw_code = completion.choices[0].message.content
        if not raw_code:
            raise HTTPException(status_code=500, detail="La IA devolvió una respuesta vacía.")

        # Limpieza estricta de bloques Markdown por seguridad
        cleaned_code = re.sub(r"^```(?:javascript|js)?\n?", "", raw_code, flags=re.MULTILINE)
        cleaned_code = re.sub(r"```$", "", cleaned_code, flags=re.MULTILINE).strip()

        return {
            "status": "success",
            "prompt": request.prompt,
            "style": request.style,
            "code": cleaned_code
        }

    except Exception as e:
        print(f"Error detallado en el servidor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
