function getToyPromptCategory(prompt){
  const query = prompt.toLowerCase()

  if(query.includes("f1") || query.includes("car") || query.includes("race") || query.includes("vehicle")){
    return "car"
  }

  if(
    query.includes("robot") ||
    query.includes("android") ||
    query.includes("mech") ||
    query.includes("figure")
  ){
    return "robot"
  }

  return "robot"
}

function resolveToyAssetUrl(assetUrl){
  if(!assetUrl){
    return ""
  }

  if(assetUrl.startsWith("http")){
    return assetUrl
  }

  if(assetUrl.startsWith("/frontend/")){
    return new URL(assetUrl, window.location.origin).href
  }

  if(assetUrl.startsWith("models/")){
    return new URL(assetUrl, window.location.href).href
  }

  return window.PLUTO_API_BASE + assetUrl
}

async function generateToyTest(){
  if(!window.canUseFeature("toyGeneration")){
    window.openUsageLimitPrompt("toyGeneration")
    return
  }

  const prompt = document.getElementById("toyPrompt").value.toLowerCase()
  const status = document.getElementById("toyStatus")
  const promptCategory = getToyPromptCategory(prompt)
  const testModels = window.PLUTO_TEST_MODELS || {}

  await window.showSponsorPreview("toyGeneration")
  status.innerHTML = "Loading test toy model..."

  if(promptCategory === "car" && testModels.car?.url){
    loadGLB(testModels.car.url, testModels.car.filename)
    showViewerDownload(testModels.car.url, testModels.car.filename)
    window.incrementUsage("toyGeneration")
    status.innerHTML = "Test F1 toy loaded. Use Scale / Rotate, then Print and download STL."
    return
  }

  if(!testModels.default?.url){
    status.innerHTML = "Test toy models are not available."
    return
  }

  loadGLB(testModels.default.url, testModels.default.filename)
  showViewerDownload(testModels.default.url, testModels.default.filename)
  window.incrementUsage("toyGeneration")
  status.innerHTML = "Test toy loaded. Use Scale / Rotate, then Print and download STL."
}

async function generateToyPro(){
  const prompt = document.getElementById("toyPrompt").value
  const template = document.getElementById("toyTemplate").value
  const size = document.getElementById("toySize").value
  const status = document.getElementById("toyStatus")

  if(!prompt){
    alert("Write prompt first")
    return
  }

  await window.showSponsorPreview("toyGeneration")
  status.innerHTML = "Generating Toy PRO..."

  try{
    const res = await fetch(window.PLUTO_API_BASE + "/api/generate-toy", {
      method:"POST",
      headers:{
        "Content-Type":"application/json"
      },
      body: JSON.stringify({
        prompt,
        template,
        size
      })
    })

    const data = await res.json()

    if(!data.glb_url && !data.stl_url){
      status.innerHTML = "Toy PRO failed."
      return
    }

    if(data.glb_url){
      const glbUrl = resolveToyAssetUrl(data.glb_url)

      loadGLB(glbUrl, "toy-pro.glb")
      showViewerDownload(glbUrl, "toy-pro.glb")
      window.incrementUsage("toyGeneration")
      status.innerHTML = "Toy PRO ready. Use Scale / Rotate, then Print and download STL."
      return
    }

    if(data.stl_url){
      const stlUrl = resolveToyAssetUrl(data.stl_url)

      loadSTL(stlUrl, "toy-pro.stl")
      showViewerDownload(stlUrl, "toy-pro.stl")
      window.incrementUsage("toyGeneration")
      status.innerHTML = "Toy PRO STL ready. You can still review it in the viewer."
      return
    }

    status.innerHTML = "No Toy PRO model returned."
  }catch(err){
    console.log(err)
    status.innerHTML = "Toy PRO generation error."
  }
}

function bindToyModeActions(){
  const testButton = document.getElementById("generateToyTestBtn")
  const proButton = document.getElementById("generateToyProBtn")

  if(testButton && !testButton.dataset.bound){
    testButton.addEventListener("click", generateToyTest)
    testButton.dataset.bound = "1"
  }

  if(proButton && !proButton.dataset.bound){
    proButton.addEventListener("click", () => {
      if(typeof runPremiumAction === "function"){
        runPremiumAction("premium-toy-generation", generateToyPro)
      }
    })
    proButton.dataset.bound = "1"
  }
}

window.generateToyTest = generateToyTest
window.generateToyPro = generateToyPro
window.generateToy = generateToyTest

document.addEventListener("DOMContentLoaded", bindToyModeActions)
