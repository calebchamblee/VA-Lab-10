**What I Changed**

A custom version that lets you blend 2-5 faces using a weighted linear combination.

**New Files**

All custom files follow the custom_X naming convention and live alongside the originals in the same subdirectories:

backend/custom_model.py — copy of model.py with a new blend() function added at the bottom

backend/custom_app.py — copy of app.py, trimmed down to only the endpoints we need (/generate and /blend), plus the new /blend endpoint

frontend/custom_index.html — new layout with a side panel and N-face grid (not yet styled)

frontend/custom_app.js — new frontend logic for generating N faces and blending them

frontend/custom_style.css — styling for the custom interface (empty as of now)

**How to Run**

From the root of the project:
cmduvicorn backend.custom_app:app --reload --host 127.0.0.1 --port 8000
Then open http://127.0.0.1:8000 in your browser.

**How to Use**

Select the number of faces (2–5) from the dropdown — faces generate automatically
Set weights for each face (can be negative for subtraction)
Weights are auto-normalized to sum to 1 before blending
Hit Apply Weights to generate the blended result (even on page load)
Hit New Faces to regenerate random faces with the same count
