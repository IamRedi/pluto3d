const API = "https://pluto3d-production.up.railway.app/api"

let uploadedImage = null


// ---------------- UPLOAD ----------------

async function uploadImage(){

const fileInput = document.querySelector("#fileInput")
const file = fileInput.files[0]

if(!file){
alert("Select an image first")
return
}

const formData = new FormData()
formData.append("file", file)

const res = await fetch(API + "/upload",{
method:"POST",
body:formData
})

const data = await res.json()

uploadedImage = data.filename

console.log("Uploaded:", data)

}


// ---------------- GENERATE SVG ----------------

async function generateSVG(){

if(!uploadedImage){
alert("Upload image first")
return
}

const res = await fetch(API + "/svg",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
image: uploadedImage
})
})

const data = await res.json()

console.log("Generated:", data)
showSVG(data.svg_url)

}


// ---------------- SHOW SVG ----------------

function showSVG(svgUrl){

const preview = document.querySelector("#preview")

preview.innerHTML = `
<object data="${API}${svgUrl}" type="image/svg+xml" width="100%"></object>
`

}

function downloadSVG(url) {
  const a = document.createElement("a")
  a.href = url
  a.download = "pluto.svg"
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

// ---------------- AI PHOTO ----------------

async function generateSVG(){

const fileInput = document.querySelector("#fileInput")
const file = fileInput.files[0]

if(!file){
alert("Select image first")
return
}

const formData = new FormData()
formData.append("file", file)

const res = await fetch(API + "/svg",{
method:"POST",
body:formData
})

const data = await res.json()

console.log("SVG Generated:", data)

showSVG(data.svg_url)

}



// ---------------- DOWNLOAD AI IMAGE ----------------

function downloadAI(){

const img = document.getElementById("svgViewer")

if(!img.src){
alert("No image to download")
return
}

const a = document.createElement("a")

a.href = img.src
a.download = "ai_image.png"

a.click()

}



// ---------------- BUTTON EVENTS ----------------

document.querySelector("#uploadBtn").onclick = uploadImage
document.querySelector("#generateBtn").onclick = generateSVG
document.querySelector("#generateToy").onclick = generateToy
document.querySelector("#generateAI").onclick = generateAIPhoto
document.querySelector("#downloadAI").onclick = downloadAI

// ---------------- TOY GENERATOR ----------------

async function generateToy() {

  const prompt = document.querySelector("#toyPrompt").value
  const template = document.querySelector("#template").value
  const size = document.querySelector("#size").value

  const res = await fetch(API + "/generate-toy", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      prompt,
      template,
      size
    })
  })

  const data = await res.json()
// 🔥 NEW: PolyPizza Gallery
const models = searchToyModels(prompt)
renderToyGallery(models)
  console.log("TOY:", data)

  // FIX PATH
const stlUrl = data.stl_url
const glbUrl = data.glb_url

// DEBUG NE UI
const viewer = document.querySelector("#viewer")

if(glbUrl){
    console.log("GLB OK:", glbUrl)
    loadGLB(glbUrl)
} else {
    console.error("GLB missing")
    viewer.innerHTML = "<h3 style='color:red'>❌ GLB NOT GENERATED</h3>"
}

// DOWNLOAD STL
if(stlUrl){
    setupDownload(stlUrl)
}
}


// ---------------- LOAD STL ----------------

function loadGLB(url) {

  const viewer = document.querySelector("#viewer")

  viewer.innerHTML = `
    <model-viewer 
      src="${url}" 
      camera-controls 
      auto-rotate 
      shadow-intensity="1"
      exposure="1"
      style="width:100%; height:100%;">
    </model-viewer>
  `
}


// ---------------- DOWNLOAD ----------------

function setupDownload(url){

  const btn = document.querySelector("#downloadBtn")

  btn.onclick = () => {
    const a = document.createElement("a")
    a.href = url
    a.download = "toy.stl"
    a.click()
  }

}

let TOY_LIBRARY = []

async function loadToyLibrary(){

  try{

    const res = await fetch("models.json")
    const data = await res.json()

    TOY_LIBRARY = data

    console.log("MODELS LOADED:", TOY_LIBRARY)

  }catch(err){

    console.error("Failed loading models.json", err)

  }

}

function searchToyModels(prompt){

  const q = prompt.toLowerCase()

  const results = TOY_LIBRARY.filter(m =>
    m.name.toLowerCase().includes(q) ||
    (m.tags && m.tags.some(tag => tag.toLowerCase().includes(q)))
  )

  return results.length ? results : TOY_LIBRARY
}

function renderToyGallery(models){

  const gallery = document.getElementById("toyGallery")

  if(!gallery) return

  gallery.innerHTML = ""

  models.forEach(model => {

    const img = document.createElement("img")
    img.src = model.thumb

    img.onclick = () => {

      loadGLB(model.url)
      showViewerDownload(model.url, "toy.glb")

    }

    gallery.appendChild(img)
  })
}

loadToyLibrary()

function loadFake3D(imageUrl){

const viewer = document.querySelector("#viewer")

viewer.innerHTML = `
  <div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; position:relative;">
    
    <img src="${imageUrl}" 
      style="
        width:60%;
        border-radius:12px;
        box-shadow:0 20px 60px rgba(0,0,0,0.5);
        transform:rotateY(-15deg) rotateX(8deg);
        transition:transform 0.3s;
      "
      id="fake3dImg"
    >

  </div>
`

// animation e lehtë
const img = document.getElementById("fake3dImg")

let angle = -15

setInterval(()=>{
  angle += 0.2
  img.style.transform = `rotateY(${angle}deg) rotateX(8deg)`
}, 30)

}