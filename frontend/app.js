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


// ---------------- BUTTON EVENTS ----------------

document.querySelector("#uploadBtn").onclick = uploadImage;
document.querySelector("#generateBtn").onclick = generateSVG;