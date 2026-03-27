// Keep the owned test model library explicit so prompt matching stays predictable.
const TEST_MODEL_ASSET_VERSION = "2026-03-27-registry-2";
const TEST_MODEL_PREVIEW_BASE = "models/models with png foto previewe";

window.PLUTO_TEST_MODEL_LIBRARY = [
  {
    id: "robot",
    label: "Pluto Robot",
    keywords: ["robot", "android", "mech", "cyborg", "figure"],
    url: `models/pluto-robot.glb?v=${TEST_MODEL_ASSET_VERSION}`,
    filename: "pluto-robot-test.glb",
    previewUrl: `${TEST_MODEL_PREVIEW_BASE}/pluto-robot.png?v=${TEST_MODEL_ASSET_VERSION}`,
    previewLabel: "Pluto Robot source",
    randomWeight: 1
  },
  {
    id: "car",
    label: "Car",
    keywords: ["car", "automobile", "coupe", "sedan", "vehicle"],
    url: `${TEST_MODEL_PREVIEW_BASE}/car.glb?v=${TEST_MODEL_ASSET_VERSION}`,
    filename: "car-test.glb",
    previewUrl: `${TEST_MODEL_PREVIEW_BASE}/car.png?v=${TEST_MODEL_ASSET_VERSION}`,
    previewLabel: "Car source",
    randomWeight: 1
  },
  {
    id: "f1car",
    label: "F1 Car",
    keywords: ["f1", "formula", "formula one", "race car", "racing", "sport car", "speed"],
    url: `models/f1car.glb?v=${TEST_MODEL_ASSET_VERSION}`,
    filename: "f1car-test.glb",
    previewUrl: `${TEST_MODEL_PREVIEW_BASE}/f1car.png?v=${TEST_MODEL_ASSET_VERSION}`,
    previewLabel: "F1 Car source",
    randomWeight: 1
  },
  {
    id: "bike",
    label: "Bike",
    keywords: ["bike", "motorbike", "motorcycle", "bicycle", "cycle"],
    url: `${TEST_MODEL_PREVIEW_BASE}/bike.glb?v=${TEST_MODEL_ASSET_VERSION}`,
    filename: "bike-test.glb",
    previewUrl: `${TEST_MODEL_PREVIEW_BASE}/bike.png?v=${TEST_MODEL_ASSET_VERSION}`,
    previewLabel: "Bike source",
    randomWeight: 1
  },
  {
    id: "skenderbeg",
    label: "Skenderbeg",
    keywords: ["skenderbeg", "hero", "warrior", "fighter", "knight", "legend", "toy", "collectible"],
    url: `${TEST_MODEL_PREVIEW_BASE}/Skenderbeg.glb?v=${TEST_MODEL_ASSET_VERSION}`,
    filename: "skenderbeg-test.glb",
    previewUrl: `${TEST_MODEL_PREVIEW_BASE}/Skenderbeg.png?v=${TEST_MODEL_ASSET_VERSION}`,
    previewLabel: "Skenderbeg source",
    randomWeight: 4
  }
];

window.PLUTO_TEST_MODELS = {
  default: window.PLUTO_TEST_MODEL_LIBRARY[0],
  car: window.PLUTO_TEST_MODEL_LIBRARY[1],
  f1: window.PLUTO_TEST_MODEL_LIBRARY[2],
  bike: window.PLUTO_TEST_MODEL_LIBRARY[3],
  hero: window.PLUTO_TEST_MODEL_LIBRARY[4]
};

function getWeightedRandomOwnedTestModel(){
  const weightedPool = window.PLUTO_TEST_MODEL_LIBRARY.flatMap((entry) =>
    Array(Math.max(1, Number(entry.randomWeight || 1))).fill(entry)
  );

  if(!weightedPool.length){
    return null;
  }

  const randomIndex = Math.floor(Math.random() * weightedPool.length);
  return weightedPool[randomIndex];
}

window.resolveOwnedTestModel = function resolveOwnedTestModel(options = {}){
  const prompt = String(options.prompt || "").toLowerCase();
  const activeImage = options.activeImage || null;
  const imageHints = [
    activeImage?.label || "",
    activeImage?.filename || "",
    activeImage?.url || ""
  ].join(" ").toLowerCase();
  const query = `${prompt} ${imageHints}`.trim();

  const directMatch = window.PLUTO_TEST_MODEL_LIBRARY.find((entry) =>
    entry.keywords.some((keyword) => query.includes(keyword))
  );

  if(directMatch){
    return directMatch;
  }

  return getWeightedRandomOwnedTestModel();
};
