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
renderer.setSize(
  viewerContainer.clientWidth,
  viewerContainer.clientHeight
)

document.getElementById("viewer").appendChild(renderer.domElement)
renderer.domElement.style.position = "absolute"
renderer.domElement.style.top = "0"
renderer.domElement.style.left = "0"
renderer.domElement.style.zIndex = "1"

const light = new THREE.DirectionalLight(0xffffff, 1)
light.position.set(2, 2, 2)
scene.add(light)

camera.position.z = 3

const controls = new THREE.OrbitControls(camera, renderer.domElement)

function loadModel(url){
  loadGLB(url, "model.glb")
}

function animate(){
  requestAnimationFrame(animate)
  renderer.render(scene, camera)
}

animate()

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
      metalness: 0.3,
      roughness: 0.4
    })

    const mesh = new THREE.Mesh(geometry, material)
    window.currentModel = mesh

    geometry.center()
    scene.add(light)
    scene.add(mesh)
    geometry.center()

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

    scene.add(light)

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

  scene.add(light)
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
