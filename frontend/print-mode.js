function setCurrentViewerAsset(asset){
  window.currentViewerAsset = asset
  if(typeof syncStudioLaunchButton === "function"){
    syncStudioLaunchButton()
  }

  const printStatus = document.getElementById("printStatus")

  if(!printStatus) return

  if(!asset){
    printStatus.innerHTML = "Load a GLB model to enable print fix."
    return
  }

  if(asset.type === "glb"){
    printStatus.innerHTML = "GLB model ready. Use Print, then Bambu Lab / Prusa to export STL in the browser."
    return
  }

  if(asset.type === "stl"){
    printStatus.innerHTML = "Print-ready STL loaded. You can download it now."
    return
  }

  printStatus.innerHTML = "Print fix works only with GLB models."
}

function resolveAssetUrl(url){
  if(url.startsWith("http://") || url.startsWith("https://") || url.startsWith("blob:")){
    return url
  }

  return new URL(url, window.location.href).href
}

function isPrintFixPaused(){
  return Boolean(window.PLUTO_APP_CONFIG?.printFixPaused)
}

function getPrintFixPlaceholderUrl(){
  return resolveAssetUrl(
    window.PLUTO_APP_CONFIG?.printFixPlaceholderStlUrl || "models/print-ready-preview.stl"
  )
}

function getCurrentPrintFilename(){
  const asset = window.currentViewerAsset
  const baseFilename = asset?.filename || "print-ready.glb"
  return baseFilename.replace(/\.(glb|gltf|stl)$/i, "") + ".stl"
}

function downloadBlobUrl(url, filename){
  const link = document.createElement("a")
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
}

function exportCurrentModelToStlUrl(){
  if(!window.currentModel){
    throw new Error("Load a model first")
  }

  const exportRoot = window.currentModel.clone(true)
  exportRoot.updateMatrixWorld(true)

  const exporter = new THREE.STLExporter()
  const exported = exporter.parse(exportRoot, { binary: true })
  const data = exported instanceof DataView ? exported.buffer : exported
  const blob = new Blob([data], { type: "model/stl" })

  return URL.createObjectURL(blob)
}

function downloadCurrentModelAsStl(){
  const stlUrl = exportCurrentModelToStlUrl()
  const filename = getCurrentPrintFilename()
  downloadBlobUrl(stlUrl, filename)
  window.setTimeout(() => {
    URL.revokeObjectURL(stlUrl)
  }, 2000)
  return { stlUrl, filename }
}

function wait(ms){
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

async function createPrintReadyStl(sourceUrl, sourceFilename = "model.glb"){
  const sourceRes = await fetch(sourceUrl)

  if(!sourceRes.ok){
    throw new Error("Could not read source GLB model")
  }

  const glbBlob = await sourceRes.blob()
  const form = new FormData()
  form.append("file", glbBlob, sourceFilename)

  const res = await fetch(window.PLUTO_API_BASE + "/api/print-fix", {
    method:"POST",
    body:form
  })

  const raw = await res.text()
  let data = null

  try{
    data = JSON.parse(raw)
  }catch{
    data = null
  }

  if(!res.ok){
    throw new Error((data && data.message) || raw || "Backend request failed")
  }

  if(!data || data.status !== "success" || !data.file){
    throw new Error((data && data.message) || "Print fix failed")
  }

  return window.PLUTO_API_BASE + data.file
}

async function fixCurrentModelForPrint(){
  const printStatus = document.getElementById("printStatus")
  const currentViewerAsset = window.currentViewerAsset

  if(!currentViewerAsset || currentViewerAsset.type !== "glb"){
    alert("Load a GLB model first")
    return
  }

  try{
    if(typeof setViewerMode === "function"){
      setViewerMode("print")
    }
    await wait(220)
    printStatus.innerHTML = "Direct STL export is ready. Use Bambu Lab / Prusa on the right."
  }catch(err){
    console.error("Print preparation error:", err)
    printStatus.innerHTML = "STL export setup failed."

    const msg = err.message && err.message.includes("Failed to fetch")
      ? "Backend is not running on http://127.0.0.1:8000. Start FastAPI server first."
      : (err.message || "STL export setup failed")

    alert(msg)
  }
}

function applyTransform(){
  if(!window.currentModel){
    alert("Load model first")
    return
  }

  const scale = document.getElementById("scaleSlider").value
  const rot = document.getElementById("rotateSlider").value

  window.currentModel.scale.set(scale, scale, scale)
  window.currentModel.rotation.y = THREE.MathUtils.degToRad(rot)
}
