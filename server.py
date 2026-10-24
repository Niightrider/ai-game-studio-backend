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

# Inicializar cliente oficial de Groq (lee automáticamente la variable GROQ_API_KEY de Render)
client = Groq()

class GameRequest(BaseModel):
    prompt: str
    style: str = "pixel_art"

@app.post("/generate-game")
async def generate_game(request: GameRequest):
    system_prompt = (
        "Eres un desarrollador experto en Phaser 3. "
        "Genera ÚNICAMENTE código JavaScript plano, moderno y sintácticamente perfecto para un juego arcade en 2D. "
        "REGLAS OBLIGATORIAS:\n"
        "1. NO uses bloques de markdown como ```javascript o ```. Devuelve SOLO el código JS puro.\n"
        "2. NUNCA hagas asignaciones inválidas (como asignar valores a funciones o constantes).\n"
        "3. CONFIGURACIÓN DE PHASER:\n"
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
        "4. CARGA DE SPRITES:\n"
        "   Usa URLs limpias en preload():\n"
        "   this.load.image('player', 'https://image.pollinations.ai/prompt/pixel%20art%20character,%20isolated,%20white%20background');\n"
        "   this.load.image('enemy', 'https://image.pollinations.ai/prompt/pixel%20art%20enemy,%20isolated,%20white%20background');\n"
        "5. Define estrictamente las funciones preload(), create() y update() de forma independiente."
    )

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # El modelo oficial que te indica el panel de Groq
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.prompt}
            ],
            temperature=0.7,
            max_completion_tokens=2048,
            top_p=1
        )

        raw_code = completion.choices[0].message.content

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
        print(f"Error detallado en el servidor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
