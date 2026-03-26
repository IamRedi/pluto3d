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
    printStatus.innerHTML = "GLB model ready. Click Fix for Print to create STL."
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

  if(isPrintFixPaused()){
    printStatus.innerHTML = "Preparing print-ready STL preview..."
    await wait(900)

    const stlUrl = getPrintFixPlaceholderUrl()
    loadSTL(stlUrl, "print-ready-preview.stl")
    showViewerDownload(stlUrl, "print-ready-preview.stl")
    printStatus.innerHTML = "Print fix is paused during public testing. A ready STL preview is available for download."
    return
  }

  printStatus.innerHTML = "Uploading model to print fixer..."

  try{
    const stlUrl = await createPrintReadyStl(
      currentViewerAsset.url,
      currentViewerAsset.filename || "model.glb"
    )

    loadSTL(stlUrl, "print-ready.stl")
    showViewerDownload(stlUrl, "print-ready.stl")
    printStatus.innerHTML = "Print fix complete. STL is ready."

  }catch(err){
    console.error("Print fix error:", err)
    printStatus.innerHTML = "Print fix failed."

    const msg = err.message && err.message.includes("Failed to fetch")
      ? "Backend is not running on http://127.0.0.1:8000. Start FastAPI server first."
      : (err.message || "Print fix failed")

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
