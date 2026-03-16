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

const res = await fetch(API + "/generate",{
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

showSVG(data.svg)

}


// ---------------- SHOW SVG ----------------

function showSVG(svgUrl){

const preview = document.querySelector("#preview")

preview.innerHTML = `
<object data="${API}${svgUrl}" type="image/svg+xml" width="100%"></object>
`

}



// ---------------- AI PHOTO ----------------

async function generateAIPhoto(){

const prompt = document.getElementById("aiPrompt").value
const style = document.getElementById("aiStyle").value
const fileInput = document.getElementById("aiInput")

const formData = new FormData()

formData.append("prompt",prompt)
formData.append("style",style)

if(fileInput.files.length > 0){
formData.append("image",fileInput.files[0])
}

const response = await fetch(API + "/ai-photo",{
method:"POST",
body:formData
})

const data = await response.json()

if(data.error){
alert(data.error)
return
}

if(!data.image_url){
alert("AI did not return image")
return
}

const viewer = document.getElementById("svgViewer")

viewer.src = data.image_url
viewer.style.display = "block"

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
document.querySelector("#generateAI").onclick = generateAIPhoto
document.querySelector("#downloadAI").onclick = downloadAI