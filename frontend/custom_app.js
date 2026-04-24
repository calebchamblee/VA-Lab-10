const API_BASE = 'http://127.0.0.1:8000';

// easier
const el = id => document.getElementById(id);

let zIds = [];

// post utility
async function postJSON(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt);
  }
  return res.json();
}

// set message and fomrula functions, get # faces, weights
function setMsg(text){ el('errorMsg').textContent = text }
// now always have formula displayed
function setFormula(text){ el('formula').textContent = text }
function getNumFaces() { return +(el('numFaces').value)}
function getWeights() {
  const n = getNumFaces();
  const weights = [];
  // get weights from DOM, default to 0 if not set
  for (let i = 0; i < n; i++) {
    weights.push(+el(`weight${i}`).value || 0);
  }
  return weights;
}

// create elements the input faces
function renderFaces() {
  const n = getNumFaces();
  const row = el('facesRow');
  // reset
  row.innerHTML = "";
  // create element for each and show
  for (let i = 0; i < n; i++) {
    const fig = document.createElement('figure');
    fig.className = "face-fig";
    const img = document.createElement('img');
    img.id = `face${i}`;
    img.alt = `Face ${i + 1}`;
    // caption each image
    const caption = document.createElement('figcaption');
    caption.textContent = `Face ${i + 1}`;
    // make image and caption siblings
    fig.appendChild(img);
    fig.appendChild(caption);
    row.appendChild(fig);
  }
}

// create the input boxes for weights of each image
function renderWeightInputs() {
    const n = getNumFaces();
    const container = el('weightInputs');
    // reset
    container.innerHTML = "";
    // one input box for each input face
    for (let i = 0; i < n; i++) {
        const div = document.createElement('div');
        div.className = 'weight-row';
        // label each box corresponding to jmage
        const label = document.createElement('label');
        label.textContent = `Weight ${i + 1}`;
        label.htmlFor = `weight${i}`;
        // create close to continuous input for the textbox
        const input = document.createElement('input');
        input.type = 'number';
        input.id = `weight${i}`;
        input.value = (1 / n).toFixed(2);
        input.step = '0.1';
        input.min = '-10';
        input.max = '10';
        // add to weightInputs on dom
        div.appendChild(label);
        div.appendChild(input);
        container.appendChild(div);
    }
}

// make the faces show up
async function generateFaces() {
  setMsg('')
  // any change to A or B invalidates existing filmstrip
  const n = getNumFaces();
  zIds = [];
  try {
    // create one image for each num faces
    for (let i = 0; i < n; i++){
        // get data from backend, set to source for image
        const data = await postJSON('/generate', {})
        zIds.push(data.latent_id);
        el(`face${i}`).src = data.image;
    } // catch error
  } catch (e) {
    setMsg('Generation error: ' + e.message)
    throw e
  }
}

// weight/blend the images based on users inputs
async function apply_weights() {
    // always reset error message first
    setMsg('');
    // make sure zIds is not empty
    if (zIds.length == 0) { setMsg('Generate Faces First'); return }
    // get weights and total for norming
    const weights = getWeights();
    let total = 0;
    for (let i = 0; i < weights.length; i++) {
    total += weights[i];
    }

    try {
        // get data from backend
        const data = await postJSON('/blend', { z_ids: zIds, weights: weights });
        // set output image
        el('imgOut').src = data.image;
        // set weights to normalized to show correctly in equationon screen
        let normed = []
        for (let i = 0; i < weights.length; i++) {
            normed[i] = (weights[i] / (total || 1)).toFixed(2);
        }
        // concat all terms
        let terms = '';
        for (let i = 0; i < normed.length; i++) {
            if (i > 0) {
                terms += ' + '
            }
            terms += `${normed[i]}*z${i + 1}`;
        }
        // set the formula
        setFormula(`z_out = ${terms}`);
    } catch (e) { // catch backend error here
        setMsg('Blend error: ' + e.message);
    }
} 

// for onload, input faces, weights, output
async function init() {
    renderFaces();
    renderWeightInputs();
    await generateFaces();
}

// whenever page loads
document.addEventListener('DOMContentLoaded', () => {
  // whene num faces change, reset completely
  el('numFaces').addEventListener('change', async () => {
    renderFaces();
    renderWeightInputs();
    await generateFaces();
  })
  // generate new faces with new faces, weights same
  el('newFacesBtn').addEventListener('click', generateFaces);
  // apply weights when asked, changes ouput image
  el('applyBtn').addEventListener('click', apply_weights);
  // kick off here
  init()
})