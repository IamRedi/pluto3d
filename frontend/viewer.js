const scene = new THREE.Scene()

const viewerContainer = document.getElementById("viewer")

const camera = new THREE.PerspectiveCamera(
  75,
  viewerContainer.clientWidth / viewerContainer.clientHeight,
  0.1,
  1000
)

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: true
})

renderer.setClearColor(0x000000, 0)
renderer.setPixelRatio(window.devicePixelRatio || 1)
renderer.outputEncoding = THREE.sRGBEncoding
renderer.toneMapping = THREE.ACESFilmicToneMapping
renderer.toneMappingExposure = 1.15
renderer.setSize(
  viewerContainer.clientWidth,
  viewerContainer.clientHeight
)

renderer.domElement.style.position = "absolute"
renderer.domElement.style.top = "0"
renderer.domElement.style.left = "0"
renderer.domElement.style.zIndex = "1"

const directionalLight = new THREE.DirectionalLight(0xffffff, 1.4)
directionalLight.position.set(2, 3, 4)

const ambientLight = new THREE.AmbientLight(0xffffff, 0.65)
const hemisphereLight = new THREE.HemisphereLight(0x7dd3fc, 0x12061f, 0.85)

camera.position.z = 3

const controls = new THREE.OrbitControls(camera, renderer.domElement)
window.currentViewerMode = window.currentViewerMode || "studio"

const VIEWER_SHELL = `
<button id="viewerDownload" class="viewer-download hidden">
Download
</button>
<div class="viewer-title">AI Viewer</div>
<div class="viewer-toolbar">
  <button id="studioLaunch" class="studio-launch hidden" onclick="openToyStudio()">
  Open Studio
  </button>
  <div class="viewer-modes">
    <button class="viewer-mode-btn" data-viewer-mode="wireframe">Wire</button>
    <button class="viewer-mode-btn" data-viewer-mode="print">Print</button>
  </div>
</div>
<img
  id="svgViewer"
  style="
    display:none;
    position:absolute;
    inset:0;
    margin:auto;
    width:70%;
    height:auto;
    max-width:700px;
    object-fit:contain;
    z-index:2;
    filter:none;
  "
>
`

function addDefaultLights(){
  scene.add(ambientLight)
  scene.add(hemisphereLight)
  scene.add(directionalLight)
}

function resetViewerShell(){
  viewerContainer.innerHTML = VIEWER_SHELL
  viewerContainer.appendChild(renderer.domElement)
  bindViewerModeControls()
  syncViewerModeButtons()
  syncStudioLaunchButton()
}

function bindViewerModeControls(){
  viewerContainer.querySelectorAll("[data-viewer-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      setViewerMode(button.dataset.viewerMode)
    })
  })
}

function syncViewerModeButtons(){
  viewerContainer.querySelectorAll("[data-viewer-mode]").forEach((button) => {
    const isActive = button.dataset.viewerMode === window.currentViewerMode
    button.classList.toggle("active", isActive)
  })
}

function getCurrentMeshList(){
  if(!window.currentModel){
    return []
  }

  if(window.currentModel.isMesh){
    return [window.currentModel]
  }

  const meshes = []
  window.currentModel.traverse((child) => {
    if(child.isMesh){
      meshes.push(child)
    }
  })

  return meshes
}

function cloneMaterial(material){
  if(Array.isArray(material)){
    return material.map((item) => item.clone())
  }

  return material.clone()
}

function ensureOriginalMaterials(){
  getCurrentMeshList().forEach((mesh) => {
    if(!mesh.userData.plutoOriginalMaterial){
      mesh.userData.plutoOriginalMaterial = cloneMaterial(mesh.material)
    }
  })
}

function buildModeMaterial(sourceMaterial, mode){
  if(mode === "studio"){
    return sourceMaterial.clone()
  }

  if(mode === "wireframe"){
    const wireMaterial = sourceMaterial.clone()
    wireMaterial.wireframe = true
    wireMaterial.transparent = true
    wireMaterial.opacity = 0.92
    return wireMaterial
  }

  const printMaterial = new THREE.MeshStandardMaterial({
    color: 0xff8a3d,
    metalness: 0.08,
    roughness: 0.72
  })

  return printMaterial
}

function applyViewerModeToModel(mode){
  ensureOriginalMaterials()

  getCurrentMeshList().forEach((mesh) => {
    const originalMaterial = mesh.userData.plutoOriginalMaterial

    if(Array.isArray(originalMaterial)){
      mesh.material = originalMaterial.map((item) => buildModeMaterial(item, mode))
      return
    }

    mesh.material = buildModeMaterial(originalMaterial, mode)
  })
}

function setViewerMode(mode){
  window.currentViewerMode = mode
  syncViewerModeButtons()

  if(window.currentModel){
    applyViewerModeToModel(mode)
  }
}

function syncStudioLaunchButton(){
  const launchButton = document.getElementById("studioLaunch")

  if(!launchButton){
    return
  }

  const shouldShow = Boolean(window.currentViewerAsset) && (
    window.currentViewerAsset.type === "glb" ||
    window.currentViewerAsset.type === "stl"
  )

  launchButton.classList.toggle("hidden", !shouldShow)
}

function openToyStudio(){
  const overlay = document.getElementById("toyStudioOverlay")
  if(!overlay) return
  overlay.classList.remove("hidden")
}

function closeToyStudio(){
  const overlay = document.getElementById("toyStudioOverlay")
  if(!overlay) return
  overlay.classList.add("hidden")
}

resetViewerShell()
addDefaultLights()

function loadModel(url){
  loadGLB(url, "model.glb")
}

function animate(){
  requestAnimationFrame(animate)
  renderer.render(scene, camera)
}

animate()

window.addEventListener("resize", () => {
  const width = viewerContainer.clientWidth
  const height = viewerContainer.clientHeight

  if(!width || !height){
    return
  }

  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
})

function loadSTL(url, filename="model.stl"){
  const loader = new THREE.STLLoader()

  loader.load(url, (geometry) => {
    const svgViewer = document.getElementById("svgViewer")
    if(svgViewer) svgViewer.style.display = "none"

    const fakeWrap = document.getElementById("fake3dWrap")
    if(fakeWrap) fakeWrap.remove()

    const aiCore = document.querySelector(".ai-core")
    if(aiCore) aiCore.style.display = "none"

    while(scene.children.length > 0){
      scene.remove(scene.children[0])
    }

    const material = new THREE.MeshStandardMaterial({
      color: 0x00d9ff,
      metalness: 0.22,
      roughness: 0.5
    })

    const mesh = new THREE.Mesh(geometry, material)
    window.currentModel = mesh

    geometry.center()
    addDefaultLights()
    scene.add(mesh)
    geometry.center()
    applyViewerModeToModel(window.currentViewerMode)

    const box = new THREE.Box3().setFromObject(mesh)
    const size = box.getSize(new THREE.Vector3()).length()
    const scale = 2 / size

    mesh.scale.setScalar(scale)
    camera.position.set(0, 0, 3)
    controls.update()

    setCurrentViewerAsset({
      type:"stl",
      url:resolveAssetUrl(url),
      filename
    })
  })
}

function loadGLB(url, filename="model.glb"){
  const loader = new THREE.GLTFLoader()

  loader.load(url, (gltf) => {
    console.log("GLB loaded:", url)

    const svgViewer = document.getElementById("svgViewer")
    if(svgViewer) svgViewer.style.display = "none"

    const fakeWrap = document.getElementById("fake3dWrap")
    if(fakeWrap) fakeWrap.remove()

    while(scene.children.length > 0){
      scene.remove(scene.children[0])
    }

    addDefaultLights()

    const model = gltf.scene
    window.currentModel = model

    const box = new THREE.Box3().setFromObject(model)
    const center = box.getCenter(new THREE.Vector3())
    model.position.x -= center.x
    model.position.z -= center.z

    const minY = box.min.y
    model.position.y -= minY

    const size = box.getSize(new THREE.Vector3()).length()
    const scale = 2 / size
    model.scale.setScalar(scale)

    scene.add(model)
    applyViewerModeToModel(window.currentViewerMode)

    camera.position.set(0, 0, 3)
    controls.update()

    setCurrentViewerAsset({
      type:"glb",
      url:resolveAssetUrl(url),
      filename
    })
  }, undefined, (error) => {
    console.error("GLB load error:", error)
  })
}

function showViewerDownload(url, filename="file"){
  const btn = document.getElementById("viewerDownload")

  btn.classList.remove("hidden")
  btn.innerText = "⬇ Download"
  btn.onclick = async () => {
    const res = await fetch(url)
    const blob = await res.blob()

    let type = blob.type
    if(filename.endsWith(".svg")){
      type = "image/svg+xml"
    }

    const fixedBlob = new Blob([blob], { type })

    const link = document.createElement("a")
    link.href = URL.createObjectURL(fixedBlob)
    link.download = filename

    document.body.appendChild(link)
    link.click()
    link.remove()
  }
}

function loadFake3D(imageUrl){
  const viewer = document.getElementById("viewer")

  while(scene.children.length > 0){
    scene.remove(scene.children[0])
  }

  addDefaultLights()
  window.currentModel = null

  setCurrentViewerAsset({
    type:"image",
    url:imageUrl,
    filename:"preview.png"
  })

  viewer.innerHTML += `
    <div id="fake3dWrap" style="
      position:absolute;
      width:100%;
      height:100%;
      display:flex;
      align-items:center;
      justify-content:center;
      z-index:2;
    ">
      <img src="${imageUrl}" id="fake3dImg"
        style="
          width:60%;
          border-radius:12px;
          box-shadow:0 20px 60px rgba(0,0,0,0.6);
          transform:rotateY(-15deg) rotateX(8deg);
          transition:transform 0.2s;
        "
      >
    </div>
  `

  const img = document.getElementById("fake3dImg")
  let angle = -15

  if(window.fakeInterval){
    clearInterval(window.fakeInterval)
  }

  window.fakeInterval = setInterval(() => {
    angle += 0.2
    img.style.transform = `rotateY(${angle}deg) rotateX(8deg)`
  }, 30)
}
