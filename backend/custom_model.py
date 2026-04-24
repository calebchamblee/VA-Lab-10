# model HANDOUT
import os
import uuid
import pickle as pkl
import base64
import io
import numpy as np

import torch
from PIL import Image

# Data dirs
ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
LATENT_DIR = os.path.join(DATA_DIR, 'latents')
os.makedirs(LATENT_DIR, exist_ok=True)

# Load the pretrained StyleGAN2 generator once at import
print('Loading StyleGAN2 generator (this may take a while)...')
device = 'cpu'
if torch.cuda.is_available():
    device = 'cuda'
elif torch.backends.mps.is_available():
    device = 'mps'

with open('downloads/ffhq.pkl', 'rb') as f:
    G = pkl.load(f)['G_ema'].to(device)
G.eval()
print('Generator loaded: z_dim=', G.z_dim, 'resolution=', G.img_resolution)

# EXISTING FUNCTIONS

# convert tensor to python image
def _synth_to_pil(img_tensor):
    img = (img_tensor * 127.5 + 128).clamp(0, 255).to(torch.uint8).cpu().numpy()
    arr = img[0].transpose(1, 2, 0)
    return Image.fromarray(arr)

# save image
def _save_z_and_get_id(z_tensor):
    z_id = uuid.uuid4().hex
    path = os.path.join(LATENT_DIR, f"{z_id}.pth")
    torch.save(z_tensor.cpu(), path)
    return z_id

# get path for image
def _z_path(z_id):
    return os.path.join(LATENT_DIR, f"{z_id}.pth")

# convert to url for src
def _pil_to_data_url(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format='PNG')
    b = base64.b64encode(buf.getvalue()).decode('ascii')
    return f"data:image/png;base64,{b}"

# random image
def sample_z():
    return torch.randn([1, G.z_dim], device=device)
    
def sample_and_generate():
    z = sample_z()
    z_id = _save_z_and_get_id(z)
    img_b64 = generate_from_z_tensor(z)
    return z_id, img_b64

# whole process to get vector and produce image
def generate_from_z_tensor(z_tensor):
    z = z_tensor.to(device)
    with torch.no_grad():
        c = None
        w = G.mapping(z, c)
        img_tensor = G.synthesis(w)
        pil = _synth_to_pil(img_tensor)
        return _pil_to_data_url(pil)

# NEW CODE

# blend images together
def blend(z_ids, weights):
    """
    Blend n latents given weights, which are normalized to sum to 1.
    Returns (new_id, image_data_url)
    """
    # ensure lengths match up
    if len(z_ids) != len(weights):
        raise ValueError('z_ids and weights must have the same length')

    # normalize
    total = sum(weights)
    if total == 0:
        # all weights 0, pick new random unrelated face
        return sample_and_generate()
    
    normed_weights = [weight / total for weight in weights]

    # load and blend (similar to other functions, just more pictures)
    z_new = None
    for z_id, w in zip(z_ids, normed_weights):
        path = _z_path(z_id)
        if not os.path.exists(path):
            raise FileNotFoundError(f'latent id not found: {z_id}')
        z = torch.load(path).to(device)
        # take weighted average
        if z_new is None:
            z_new = w * z
        else:
            z_new += w * z
    
    # follow same pattern to return image and id
    new_id = _save_z_and_get_id(z_new)
    img_b64 = generate_from_z_tensor(z_new)
    return new_id, img_b64