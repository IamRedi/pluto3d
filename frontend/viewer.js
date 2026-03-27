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
const idleKeyLight = new THREE.DirectionalLight(0xf4f9ff, 1.85)
idleKeyLight.position.set(-2.6, 2.8, 4.2)
const idleFillLight = new THREE.DirectionalLight(0xaed6ff, 1.05)
idleFillLight.position.set(2.4, 1.6, -2.4)
const idleModelLoader = new THREE.GLTFLoader()

window.currentViewerMode = "wireframe"
window.currentViewerAsset = window.currentViewerAsset || null
window.currentViewerIsIdle = window.currentViewerIsIdle || false
window.viewerIdleRequestId = window.viewerIdleRequestId || 0
window.viewerPrintCtaArmed = false
window.viewerPrintCtaAssetKey = window.viewerPrintCtaAssetKey || null

camera.position.z = 3

const controls = new THREE.OrbitControls(camera, renderer.domElement)

const VIEWER_SHELL = `
<button id="viewerDownload" class="viewer-download hidden">
Download
</button>
<div class="viewer-title">3D Viewer</div>
<div class="viewer-toolbar">
  <div class="viewer-modes">
    <button class="viewer-mode-btn" data-viewer-mode="wireframe">Wire</button>
    <button class="viewer-mode-btn" data-viewer-mode="print">Print</button>
  </div>
</div>
<div id="viewerPrintCta" class="viewer-print-cta hidden">
  <div id="viewerPrintNote" class="viewer-print-note">Printer STL export</div>
  <button id="viewerPrintDownload" class="viewer-print-download" type="button">Bambu Lab / Prusa STL</button>
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

function addIdleViewerLights(){
  scene.add(idleKeyLight)
  scene.add(idleFillLight)
}

function getIdleViewerModelUrl(){
  return window.PLUTO_APP_CONFIG?.idleViewerModelUrl || "models/f1car.glb"
}

function resolveAssetUrl(url){
  try{
    return new URL(url, window.location.href).href
  }catch(error){
    return url
  }
}

function setCurrentViewerAsset(asset){
  const previousAssetKey = getViewerAssetKey(window.currentViewerAsset)
  window.currentViewerAsset = asset || null
  window.currentViewerIsIdle = Boolean(asset && asset.type === "idle")

  const currentAssetKey = getViewerAssetKey(window.currentViewerAsset)
  if(previousAssetKey !== currentAssetKey){
    window.viewerPrintCtaArmed = false
    window.viewerPrintCtaAssetKey = null
    if(window.currentViewerMode === "print"){
      window.currentViewerMode = "wireframe"
    }
    syncViewerModeButtons()
  }

  syncStudioLaunchButton()
  syncViewerSurfaceChrome()
  syncViewerPrintCta()

  const printStatus = document.getElementById("printStatus")

  if(!printStatus){
    return
  }

  if(!asset || asset.type === "idle"){
    printStatus.innerHTML = "Load a GLB model to enable Print mode."
    return
  }

  if(asset.type === "glb"){
    printStatus.innerHTML = "GLB model ready. Open Print mode, then export STL for the printer."
    return
  }

  if(asset.type === "stl"){
    printStatus.innerHTML = "STL export is ready to download."
    return
  }

  printStatus.innerHTML = "Printer STL export works only with GLB models."
}

function clearSceneContents(){
  while(scene.children.length > 0){
    scene.remove(scene.children[0])
  }
}

function clearViewerOverlayArtifacts(options = {}){
  const {
    hideDownload = true,
    hideAiCore = true
  } = options

  const svgViewer = document.getElementById("svgViewer")
  if(svgViewer){
    svgViewer.style.display = "none"
  }

  const fakeWrap = document.getElementById("fake3dWrap")
  if(fakeWrap){
    fakeWrap.remove()
  }

  if(window.fakeInterval){
    clearInterval(window.fakeInterval)
    window.fakeInterval = null
  }

  const viewerDownload = document.getElementById("viewerDownload")
  if(hideDownload && viewerDownload){
    viewerDownload.classList.add("hidden")
  }

  const aiCore = document.querySelector(".ai-core")
  if(hideAiCore && aiCore){
    aiCore.style.display = "none"
  }
}

function fitModelToViewer(model){
  const box = new THREE.Box3().setFromObject(model)
  const center = box.getCenter(new THREE.Vector3())
  model.position.x -= center.x
  model.position.z -= center.z

  const minY = box.min.y
  model.position.y -= minY

  const size = box.getSize(new THREE.Vector3()).length()
  const scale = size > 0 ? 2 / size : 1
  model.scale.setScalar(scale)

  camera.position.set(0, 0, 3)
  controls.update()
}

function restoreIdleViewer(){
  if(window.currentViewerAsset && window.currentViewerAsset.type !== "idle"){
    return
  }

  window.currentViewerMode = "wireframe"
  const idleUrl = getIdleViewerModelUrl()
  const requestId = ++window.viewerIdleRequestId

  clearViewerOverlayArtifacts()
  clearSceneContents()
  addDefaultLights()
  window.currentModel = null

  idleModelLoader.load(idleUrl, (gltf) => {
    if(requestId !== window.viewerIdleRequestId){
      return
    }

    clearSceneContents()
    addDefaultLights()
    addIdleViewerLights()

    const model = gltf.scene
    window.currentModel = model

    fitModelToViewer(model)
    model.scale.multiplyScalar(1.5)
    model.position.y -= 0.12
    scene.add(model)

    setCurrentViewerAsset({
      type: "idle",
      url: resolveAssetUrl(idleUrl),
      filename: "idle-viewer.glb"
    })
  }, undefined, (error) => {
    console.error("Idle GLB load error:", error)
    window.currentViewerIsIdle = false
  })
}

function resetViewerShell(){
  viewerContainer.innerHTML = VIEWER_SHELL
  viewerContainer.appendChild(renderer.domElement)
  bindViewerModeControls()
  syncViewerModeButtons()
  syncStudioLaunchButton()
  syncViewerSurfaceChrome()
}

function bindViewerModeControls(){
  viewerContainer.querySelectorAll("[data-viewer-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      setViewerMode(button.dataset.viewerMode)
    })
  })
}

function getViewerAssetKey(asset){
  if(!asset){
    return ""
  }

  return `${asset.type || "asset"}::${asset.url || ""}::${asset.filename || ""}`
}

function syncViewerModeButtons(){
  viewerContainer.querySelectorAll("[data-viewer-mode]").forEach((button) => {
    const isActive = button.dataset.viewerMode === window.currentViewerMode
    button.classList.toggle("active", isActive)
  })
}

function syncViewerSurfaceChrome(){
  const toolbar = viewerContainer.querySelector(".viewer-toolbar")
  const wrap = document.getElementById("viewerPrintCta")
  const currentSurface = window.currentWorkspacePanel || "3d"
  const assetType = window.currentViewerAsset?.type || ""
  const hide3dControls = currentSurface === "svg" ||
    currentSurface === "relief" ||
    assetType === "svg" ||
    assetType === "relief-preview"

  if(toolbar){
    toolbar.style.display = hide3dControls ? "none" : ""
  }

  if(hide3dControls){
    window.viewerPrintCtaArmed = false
    window.viewerPrintCtaAssetKey = null
  }

  if(wrap){
    if(hide3dControls){
      wrap.classList.add("hidden")
      wrap.style.display = "none"
    }else{
      wrap.style.display = ""
    }
  }
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
    // Keep the idle showroom model clean instead of turning it into dense wire noise.
    if(window.currentViewerAsset?.type === "idle"){
      const idleMaterial = sourceMaterial.clone()
      idleMaterial.transparent = true
      idleMaterial.opacity = 0.96
      return idleMaterial
    }

    const wireMaterial = sourceMaterial.clone()
    wireMaterial.wireframe = true
    wireMaterial.transparent = true
    wireMaterial.opacity = 0.92
    return wireMaterial
  }

  const printMaterial = new THREE.MeshPhongMaterial({
    color: 0xe7decf,
    specular: 0x1e1810,
    shininess: 7,
    side: THREE.DoubleSide
  })
  printMaterial.flatShading = false
  printMaterial.vertexColors = false
  printMaterial.skinning = Boolean(sourceMaterial.skinning)
  printMaterial.morphTargets = Boolean(sourceMaterial.morphTargets)
  printMaterial.morphNormals = Boolean(sourceMaterial.morphNormals)
  printMaterial.transparent = false
  printMaterial.opacity = 1
  printMaterial.needsUpdate = true

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
  window.viewerPrintCtaArmed = mode === "print"
  window.viewerPrintCtaAssetKey = mode === "print"
    ? getViewerAssetKey(window.currentViewerAsset)
    : null
  syncViewerModeButtons()
  syncViewerPrintCta()

  if(window.currentModel){
    applyViewerModeToModel(mode)
  }
}

function attachViewerDownload(button, url, filename){
  button.onclick = async () => {
    const res = await fetch(url)
    const blob = await res.blob()

    let type = blob.type
    if(filename.endsWith(".svg")){
      type = "image/svg+xml"
    }else if(filename.endsWith(".stl")){
      type = "model/stl"
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

function syncViewerPrintCta(){
  const wrap = document.getElementById("viewerPrintCta")
  const button = document.getElementById("viewerPrintDownload")
  const printButton = viewerContainer.querySelector('[data-viewer-mode="print"]')

  if(!wrap || !button){
    return
  }

  const asset = window.currentViewerAsset
  const currentSurface = window.currentWorkspacePanel || "3d"
  const hideForSvg = currentSurface === "svg" ||
    currentSurface === "relief" ||
    asset?.type === "svg" ||
    asset?.type === "relief-preview"
  const currentAssetKey = getViewerAssetKey(asset)
  const printButtonActive = Boolean(printButton && printButton.classList.contains("active"))
  const show = !hideForSvg &&
    window.viewerPrintCtaArmed &&
    printButtonActive &&
    window.currentViewerMode === "print" &&
    currentAssetKey === window.viewerPrintCtaAssetKey &&
    Boolean(asset) && (
    asset.type === "glb" || asset.type === "stl"
  )

  wrap.classList.toggle("hidden", !show)
  wrap.style.display = show ? "" : "none"

  if(!show){
    button.onclick = null
    return
  }

  let downloadUrl = ""
  let filename = ""

  if(asset.type === "stl"){
    downloadUrl = asset.url
    filename = asset.filename || "print-ready.stl"
  }else if(asset.type === "glb" && typeof downloadCurrentModelAsStl === "function"){
    button.onclick = () => {
      const printStatus = document.getElementById("printStatus")
      try{
        downloadCurrentModelAsStl()
        if(printStatus){
          printStatus.innerHTML = "STL exported directly from the current GLB model."
        }
      }catch(error){
        console.error("Browser STL export failed:", error)
        if(printStatus){
          printStatus.innerHTML = "STL export failed."
        }
        alert(error.message || "STL export failed")
      }
    }
    return
  }

  if(!downloadUrl){
    wrap.classList.add("hidden")
    button.onclick = null
    return
  }

  attachViewerDownload(button, downloadUrl, filename)
}

function syncStudioLaunchButton(){
  const launchButton = document.getElementById("toyPanelStudioLaunch")

  if(!launchButton){
    return
  }
  launchButton.classList.add("hidden")
}

function openToyStudio(){
  if((window.currentWorkspacePanel || "3d") !== "toy"){
    return
  }

  if(!window.currentViewerAsset){
    return
  }

  const overlay = document.getElementById("toyStudioOverlay")
  if(!overlay) return
  if(typeof refreshToyStudioState === "function"){
    refreshToyStudioState()
  }
  overlay.classList.remove("hidden")
}

function closeToyStudio(){
  const overlay = document.getElementById("toyStudioOverlay")
  if(!overlay) return
  overlay.classList.add("hidden")
}

resetViewerShell()
addDefaultLights()
restoreIdleViewer()

function loadModel(url){
  loadGLB(url, "model.glb")
}

function animate(){
  requestAnimationFrame(animate)
  if(window.currentViewerIsIdle && window.currentModel){
    window.currentModel.rotation.y += 0.0052
  }
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

function loadSTL(url, filename="model.stl", options = {}){
  const {
    viewerMode = "wireframe",
    assetType = "stl",
    color = 0x00d9ff,
    metalness = 0.22,
    roughness = 0.5
  } = options
  const loader = new THREE.STLLoader()

  loader.load(url, (geometry) => {
    window.currentViewerMode = viewerMode
    window.viewerPrintCtaArmed = false
    syncViewerModeButtons()
    syncViewerPrintCta()
    window.viewerIdleRequestId += 1
    window.currentViewerIsIdle = false
    clearViewerOverlayArtifacts({ hideDownload: false })
    clearSceneContents()

    const material = new THREE.MeshStandardMaterial({
      color,
      metalness,
      roughness
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
    if(typeof refreshToyStudioState === "function"){
      refreshToyStudioState()
    }

    setCurrentViewerAsset({
      type:assetType,
      url:resolveAssetUrl(url),
      filename
    })
  })
}

function loadGLB(url, filename="model.glb"){
  const loader = new THREE.GLTFLoader()

  loader.load(url, (gltf) => {
    console.log("GLB loaded:", url)

    window.currentViewerMode = "wireframe"
    window.viewerPrintCtaArmed = false
    syncViewerModeButtons()
    syncViewerPrintCta()
    window.viewerIdleRequestId += 1
    window.currentViewerIsIdle = false
    clearViewerOverlayArtifacts({ hideDownload: false })
    clearSceneContents()

    addDefaultLights()

    const model = gltf.scene
    window.currentModel = model

    fitModelToViewer(model)
    scene.add(model)
    applyViewerModeToModel(window.currentViewerMode)

    if(typeof refreshToyStudioState === "function"){
      refreshToyStudioState()
    }

    setCurrentViewerAsset({
      type:"glb",
      url:resolveAssetUrl(url),
      filename
    })
  }, undefined, (error) => {
    console.error("GLB load error:", error)
    restoreIdleViewer()
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
    }else if(filename.endsWith(".stl")){
      type = "model/stl"
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

  window.viewerIdleRequestId += 1
  window.currentViewerIsIdle = false
  clearSceneContents()

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
