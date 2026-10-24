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
            "Eres un desarrollador experto en Phaser.js. "
            "Tu tarea es generar únicamente código JavaScript ejecutable para un juego arcade basado en la petición del usuario. "
            "El código debe usar Phaser 3, configurar un canvas que ocupe el ancho de la pantalla y el 70% de alto ('game-container'), "
            "y añadir mecánicas interactivas sencillas acordes al prompt. "
            "Devuelve EXCLUSIVAMENTE el código JavaScript plano, sin bloques de markdown (sin ```), listo para ejecutarse."
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
