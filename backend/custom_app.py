from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import os

from . import custom_model as model

# Flask logic for supporting requests from other ports and FastAPI to handle routing
app = FastAPI(title='StyleGAN2 Lab API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend files
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
if os.path.isdir(frontend_dir):
    # Serve static frontend assets under /static to avoid shadowing API routes
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# now serve new frontend file
@app.get("/", include_in_schema=False)
def root():
    index_path = os.path.join(frontend_dir, 'custom_index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail='custom_index.html not found')

# classes to give the endpoints attributes
class GenerateResponse(BaseModel):
    latent_id: str
    image: str

# same pattern as other functions
class BlendRequest(BaseModel):
    z_ids: list[str]
    weights: list[float]

# endpoint for generating an image
@app.post('/generate', response_model=GenerateResponse)
def generate():
    try:
        # use model, provide to frontend
        z_id, img_b64 = model.sample_and_generate()
        return {"latent_id": z_id, "image": img_b64}
    # error if cant communicate
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# same pattern as other fields
@app.post('/blend', response_model=GenerateResponse)
def blend(req: BlendRequest):
    try:
        if len(req.z_ids) != len(req.weights):
            raise HTTPException(status_code=400, detail="z_ids and weights need same lenght")
        # get image from model
        new_id, img = model.blend(req.z_ids, req.weights)
        return {"latent_id": new_id, "image": img}
    # same pattern for error checking
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))