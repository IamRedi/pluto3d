function getToyPromptCategory(prompt){
  const query = prompt.toLowerCase()

  if(query.includes("car") || query.includes("race") || query.includes("vehicle")){
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

async function generateToy(){
  const mode = document.getElementById("toyMode").value

  if(mode === "test"){
    const prompt = document.getElementById("toyPrompt").value.toLowerCase()
    const status = document.getElementById("toyStatus")

    status.innerHTML = "Loading local model..."

    const promptCategory = getToyPromptCategory(prompt)

    if(promptCategory === "car"){
      loadGLB(window.PLUTO_TEST_MODELS.car.url, window.PLUTO_TEST_MODELS.car.filename)
      showViewerDownload(window.PLUTO_TEST_MODELS.car.url, window.PLUTO_TEST_MODELS.car.filename)
      status.innerHTML = "Car test model loaded."
      return
    }

    if(promptCategory === "robot"){
      loadGLB(window.PLUTO_TEST_MODELS.default.url, window.PLUTO_TEST_MODELS.default.filename)
      showViewerDownload(window.PLUTO_TEST_MODELS.default.url, window.PLUTO_TEST_MODELS.default.filename)
      status.innerHTML = "Robot test model loaded."
      return
    }

    loadGLB(window.PLUTO_TEST_MODELS.default.url, window.PLUTO_TEST_MODELS.default.filename)
    showViewerDownload(window.PLUTO_TEST_MODELS.default.url, window.PLUTO_TEST_MODELS.default.filename)
    status.innerHTML = "Default robot test model loaded."
    return
  }

  const prompt = document.getElementById("toyPrompt").value
  const template = document.getElementById("toyTemplate").value
  const size = document.getElementById("toySize").value
  const status = document.getElementById("toyStatus")

  if(!prompt){
    alert("Write prompt first")
    return
  }

  status.innerHTML = "Generating toy..."

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
      status.innerHTML = "Failed"
      return
    }

    status.innerHTML = "Toy Ready 🎯"

    if(data.glb_url){
      const glbUrl = data.glb_url.startsWith("http")
        ? data.glb_url
        : window.PLUTO_API_BASE + data.glb_url

      loadGLB(glbUrl, "toy.glb")
      showViewerDownload(glbUrl, "toy.glb")
      return
    }

    if(data.stl_url){
      const stlUrl = window.PLUTO_API_BASE + data.stl_url

      loadSTL(stlUrl, "toy.stl")
      showViewerDownload(stlUrl, "toy.stl")
      return
    }

    status.innerHTML = "No model returned"
  }catch(err){
    console.log(err)
    status.innerHTML = "Error"
  }
}
