import os
import re
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

# Configuración de cliente Groq
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
            "2. El contenedor del juego es 'game-container'. Ajusta el canvas al tamaño del contenedor.\n"
            "3. GRÁFICOS ROBUSTOS: Dibuja las texturas o sprites usando Phaser.GameObjects.Graphics en la función preload() o create() "
            "(por ejemplo, this.add.graphics() dibujando rectángulos o círculos de colores) para garantizar que los gráficos carguen SIEMPRE al instante sin fallos de red.\n"
            "4. CONTROLES TÁCTILES: Configura eventos táctiles (como 'this.input.on(\"pointermove\", ...)' o 'pointerdown') para que el jugador se mueva y juegue deslizando el dedo o tocando la pantalla del smartphone.\n"
            "5. Incluye puntuación, colisiones, lógica de juego clara y condición de fin de juego o reinicio."
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

        # Limpieza de código Markdown
        cleaned_code = re.sub(r"^```(?:javascript|js)?\n?", "", raw_code, flags=re.MULTILINE)
        cleaned_code = re.sub(r"```$", "", cleaned_code, flags=re.MULTILINE).strip()

        return {
            "status": "success",
            "prompt": request.prompt,
            "style": request.style,
            "code": cleaned_code
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
