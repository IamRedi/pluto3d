window.toyStudioState = null

function getToyStudioControls(){
  return {
    head: document.getElementById("headScaleControl"),
    body: document.getElementById("bodyScaleControl"),
    chunky: document.getElementById("chunkyControl")
  }
}

function updateToyStudioValueLabels(){
  const controls = getToyStudioControls()
  const headValue = document.getElementById("headScaleValue")
  const bodyValue = document.getElementById("bodyScaleValue")
  const chunkyValue = document.getElementById("chunkyValue")

  if(controls.head && headValue){
    headValue.textContent = `${Number(controls.head.value).toFixed(2)}x`
  }

  if(controls.body && bodyValue){
    bodyValue.textContent = `${Number(controls.body.value).toFixed(2)}x`
  }

  if(controls.chunky && chunkyValue){
    chunkyValue.textContent = `${Number(controls.chunky.value).toFixed(2)}x`
  }
}

function getToyStudioMeshes(){
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

function buildToyStudioState(){
  const meshes = getToyStudioMeshes()

  if(!window.currentModel || meshes.length === 0){
    return null
  }

  const overallBox = new THREE.Box3().setFromObject(window.currentModel)
  const overallHeight = Math.max(overallBox.max.y - overallBox.min.y, 0.001)
  const headThreshold = overallBox.min.y + overallHeight * 0.62

  const entries = meshes.map((mesh) => {
    const meshBox = new THREE.Box3().setFromObject(mesh)
    const center = meshBox.getCenter(new THREE.Vector3())

    return {
      mesh,
      basePosition: mesh.position.clone(),
      baseScale: mesh.scale.clone(),
      baseRotation: mesh.rotation.clone(),
      centerY: center.y
    }
  })

  const headEntries = entries.filter((entry) => entry.centerY >= headThreshold)
  const bodyEntries = entries.filter((entry) => entry.centerY < headThreshold)

  return {
    entries,
    headEntries: headEntries.length ? headEntries : entries,
    bodyEntries: bodyEntries.length ? bodyEntries : entries,
    simpleMode: entries.length < 2
  }
}

function ensureToyStudioState(){
  if(!window.currentModel){
    return null
  }

  if(!window.toyStudioState || window.toyStudioState.model !== window.currentModel){
    const state = buildToyStudioState()

    if(!state){
      return null
    }

    state.model = window.currentModel
    window.toyStudioState = state
  }

  return window.toyStudioState
}

function restoreToyStudioBaseState(){
  const state = ensureToyStudioState()

  if(!state){
    return false
  }

  state.entries.forEach((entry) => {
    entry.mesh.position.copy(entry.basePosition)
    entry.mesh.scale.copy(entry.baseScale)
    entry.mesh.rotation.copy(entry.baseRotation)
  })

  return true
}

function applyEntryScale(entry, factorX, factorY, factorZ){
  entry.mesh.scale.set(
    entry.baseScale.x * factorX,
    entry.baseScale.y * factorY,
    entry.baseScale.z * factorZ
  )
}

function applyToyStudioControls(){
  const state = ensureToyStudioState()

  if(!state){
    alert("Load a 3D toy model first")
    return
  }

  const controls = getToyStudioControls()
  const headScale = Number(controls.head?.value || 1)
  const bodyScale = Number(controls.body?.value || 1)
  const chunky = Number(controls.chunky?.value || 1)

  restoreToyStudioBaseState()

  if(state.simpleMode){
    const uniform = (headScale + bodyScale) / 2

    state.entries.forEach((entry) => {
      applyEntryScale(entry, uniform * chunky, uniform, uniform * chunky)
    })

    return
  }

  state.headEntries.forEach((entry) => {
    applyEntryScale(entry, headScale * chunky, headScale, headScale * chunky)
  })

  state.bodyEntries.forEach((entry) => {
    applyEntryScale(entry, bodyScale * chunky, bodyScale, bodyScale * chunky)
  })
}

function resetToyStudioStyle(){
  const controls = getToyStudioControls()

  if(controls.head) controls.head.value = "1"
  if(controls.body) controls.body.value = "1"
  if(controls.chunky) controls.chunky.value = "1"

  updateToyStudioValueLabels()
  restoreToyStudioBaseState()
}

function applyToyStudioPreset(preset){
  const controls = getToyStudioControls()

  if(!controls.head || !controls.body || !controls.chunky){
    return
  }

  const presets = {
    hero: { head: 1.05, body: 1.1, chunky: 1.08 },
    chibi: { head: 1.45, body: 0.88, chunky: 1.18 },
    collector: { head: 1.1, body: 1.02, chunky: 1.0 },
    mini: { head: 1.18, body: 0.92, chunky: 1.22 }
  }

  const values = presets[preset]

  if(!values){
    return
  }

  controls.head.value = String(values.head)
  controls.body.value = String(values.body)
  controls.chunky.value = String(values.chunky)

  updateToyStudioValueLabels()
  applyToyStudioControls()
}

function refreshToyStudioState(){
  window.toyStudioState = null
  updateToyStudioValueLabels()
}

document.addEventListener("DOMContentLoaded", () => {
  const controls = getToyStudioControls()

  Object.values(controls).forEach((control) => {
    if(!control){
      return
    }

    control.addEventListener("input", updateToyStudioValueLabels)
  })

  updateToyStudioValueLabels()
})
