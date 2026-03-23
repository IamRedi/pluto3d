window.toyStudioState = null

function getToyStudioControls(){
  return {
    head: document.getElementById("headScaleControl"),
    body: document.getElementById("bodyScaleControl"),
    chunky: document.getElementById("chunkyControl"),
    tilt: document.getElementById("tiltControl")
  }
}

function updateToyStudioValueLabels(){
  const controls = getToyStudioControls()
  const headValue = document.getElementById("headScaleValue")
  const bodyValue = document.getElementById("bodyScaleValue")
  const chunkyValue = document.getElementById("chunkyValue")
  const tiltValue = document.getElementById("tiltValue")

  if(controls.head && headValue){
    headValue.textContent = `${Number(controls.head.value).toFixed(2)}x`
  }

  if(controls.body && bodyValue){
    bodyValue.textContent = `${Number(controls.body.value).toFixed(2)}x`
  }

  if(controls.chunky && chunkyValue){
    chunkyValue.textContent = `${Number(controls.chunky.value).toFixed(2)}x`
  }

  if(controls.tilt && tiltValue){
    tiltValue.textContent = `${Number(controls.tilt.value).toFixed(0)}°`
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
    simpleMode: entries.length < 2,
    meshCount: entries.length
  }
}

function updateToyStudioMeta(state){
  const meshCount = document.getElementById("toyStudioMeshCount")
  const editMode = document.getElementById("toyStudioEditMode")

  if(meshCount){
    meshCount.textContent = state ? String(state.meshCount) : "0"
  }

  if(editMode){
    if(!state){
      editMode.textContent = "Idle"
    }else if(state.simpleMode){
      editMode.textContent = "Whole Model"
    }else{
      editMode.textContent = "Part Aware"
    }
  }
}

function ensureToyStudioState(){
  if(!window.currentModel){
    updateToyStudioMeta(null)
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

  updateToyStudioMeta(window.toyStudioState)

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
  const tilt = Number(controls.tilt?.value || 0)

  restoreToyStudioBaseState()

  if(state.simpleMode){
    const uniform = (headScale + bodyScale) / 2

    state.entries.forEach((entry) => {
      applyEntryScale(entry, uniform * chunky, uniform, uniform * chunky)
      entry.mesh.rotation.z = entry.baseRotation.z + THREE.MathUtils.degToRad(tilt * 0.6)
    })

    return
  }

  state.headEntries.forEach((entry) => {
    applyEntryScale(entry, headScale * chunky, headScale, headScale * chunky)
    entry.mesh.rotation.z = entry.baseRotation.z + THREE.MathUtils.degToRad(tilt * 0.8)
  })

  state.bodyEntries.forEach((entry) => {
    applyEntryScale(entry, bodyScale * chunky, bodyScale, bodyScale * chunky)
    entry.mesh.rotation.z = entry.baseRotation.z + THREE.MathUtils.degToRad(tilt * 0.35)
  })
}

function resetToyStudioStyle(){
  const controls = getToyStudioControls()

  if(controls.head) controls.head.value = "1"
  if(controls.body) controls.body.value = "1"
  if(controls.chunky) controls.chunky.value = "1"
  if(controls.tilt) controls.tilt.value = "0"

  updateToyStudioValueLabels()
  restoreToyStudioBaseState()
}

function applyToyStudioPreset(preset){
  const controls = getToyStudioControls()

  if(!controls.head || !controls.body || !controls.chunky){
    return
  }

  const presets = {
    hero: { head: 1.05, body: 1.1, chunky: 1.08, tilt: 3 },
    chibi: { head: 1.45, body: 0.88, chunky: 1.18, tilt: 0 },
    collector: { head: 1.1, body: 1.02, chunky: 1.0, tilt: -2 },
    mini: { head: 1.18, body: 0.92, chunky: 1.22, tilt: 4 }
  }

  const values = presets[preset]

  if(!values){
    return
  }

  controls.head.value = String(values.head)
  controls.body.value = String(values.body)
  controls.chunky.value = String(values.chunky)
  if(controls.tilt) controls.tilt.value = String(values.tilt)

  updateToyStudioValueLabels()
  applyToyStudioControls()
}

function refreshToyStudioState(){
  window.toyStudioState = null
  updateToyStudioValueLabels()
  updateToyStudioMeta(ensureToyStudioState())
}

document.addEventListener("DOMContentLoaded", () => {
  const controls = getToyStudioControls()

  Object.values(controls).forEach((control) => {
    if(!control){
      return
    }

    control.addEventListener("input", () => {
      updateToyStudioValueLabels()
      if(window.toyStudioState || window.currentModel){
        applyToyStudioControls()
      }
    })
  })

  updateToyStudioValueLabels()
  updateToyStudioMeta(null)
})
