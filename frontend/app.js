const API = "https://pluto3d-production.up.railway.app/api";

let uploadedImage = null;


// ---------------- UPLOAD ----------------

async function uploadImage() {

    const fileInput = document.querySelector("#fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Select an image first");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    uploadedImage = data.filename;

    console.log("Uploaded:", data);
}


// ---------------- GENERATE SVG ----------------

async function generateSVG() {

    if (!uploadedImage) {
        alert("Upload image first");
        return;
    }

    const res = await fetch(`${API}/generate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            image: uploadedImage
        })
    });

    const data = await res.json();

    console.log("Generated:", data);

    showSVG(data.svg);
}


// ---------------- SHOW SVG ----------------

function showSVG(svgUrl) {

    const preview = document.querySelector("#preview");

    preview.innerHTML = `
        <object data="${API}${svgUrl}" type="image/svg+xml" width="100%"></object>
    `;
}

// ----------------AIPhoto ---------------

async function generateAIPhoto(){

const prompt = document.getElementById("aiPrompt").value
const style = document.getElementById("aiStyle").value
const file = document.getElementById("aiInput").files[0]

let form = new FormData()

form.append("prompt",prompt)
form.append("style",style)

if(file){
form.append("image",file)
}

const res = await fetch(API_BASE+"/api/ai-photo",{
method:"POST",
body:form
})

const data = await res.json()

/* ERROR CHECK */

if(data.error){

alert("AI error: "+data.error)
return

}

if(!data.image_url){

alert("AI did not return image")
return

}

const viewer = document.getElementById("svgViewer")

viewer.src = data.image_url
viewer.style.display="block"

}
// ---------------- BUTTON EVENTS ----------------

document.querySelector("#uploadBtn").onclick = uploadImage;
document.querySelector("#generateBtn").onclick = generateSVG;