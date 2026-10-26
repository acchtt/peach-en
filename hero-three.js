/**
 * IVE RADAR — restrained Three.js hero experiment.
 * Decorative only. The full HTML hero remains useful if this module cannot run.
 */
const host = document.querySelector('.hero-right');
const canvas = document.querySelector('#hero-three-canvas');
const motionButton = document.querySelector('#hero-motion-toggle');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

if (host && canvas && motionButton && !reduceMotion.matches) {
  let supported = false;
  try {
    supported = Boolean(document.createElement('canvas').getContext('webgl2'));
  } catch {
    // Non-WebGL browsers keep the original static section.
  }
  if (supported) {
    try {
      const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js');
      createHero(THREE);
    } catch (error) {
      console.info('IVE RADAR: 3D unavailable; static hero retained.', error);
    }
  }
}

function createHero(THREE) {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas, alpha: true, antialias: true, powerPreference: 'default'
    });
  } catch (error) {
    console.info('IVE RADAR: WebGL unavailable.', error);
    return;
  }
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-5, 5, 3, -3, 0.1, 30);
  camera.position.set(0, 0, 13);
  const objects = new THREE.Group();
  scene.add(objects);
  scene.add(new THREE.AmbientLight(0xffffff, 2.4));
  const light = new THREE.DirectionalLight(0xffffff, 2.1);
  light.position.set(-3, 5, 9);
  scene.add(light);

  const mat = hex => new THREE.MeshStandardMaterial({
    color: hex, roughness: 0.56, metalness: 0, flatShading: true
  });
  const colors = {
    ink: mat(0x131015),
    pink: mat(0xee2db7),
    yellow: mat(0xffec59),
    cyan: mat(0x55dae2),
    lilac: mat(0xc8b2f2)
  };
  const actors = [];
  const add = (node, x, y, scale, phase) => {
    objects.add(node);
    node.position.set(x, y, 0);
    node.scale.setScalar(scale);
    actors.push({ node, startY: y, phase });
    return node;
  };

  function extruded(shape, material) {
    return new THREE.Mesh(new THREE.ExtrudeGeometry(shape, {
      depth: 0.14, bevelEnabled: true, bevelThickness: 0.035,
      bevelSize: 0.035, bevelSegments: 1, steps: 1,
      curveSegments: 1
    }), material);
  }

  function star() {
    const shape = new THREE.Shape();
    for (let i = 0; i < 10; i++) {
      const angle = Math.PI / 2 + i * Math.PI / 5;
      const radius = i % 2 === 0 ? 0.95 : 0.43;
      const point = [Math.cos(angle) * radius, Math.sin(angle) * radius];
      if (i === 0) shape.moveTo(...point);
      else shape.lineTo(...point);
    }
    shape.closePath();
    const node = new THREE.Group();
    const edge = extruded(shape, colors.ink);
    edge.scale.set(1.09, 1.09, 1);
    edge.position.z = -0.065;
    const face = extruded(shape, colors.yellow);
    face.position.z = 0.05;
    node.add(edge, face);
    return node;
  }

  function disc() {
    const node = new THREE.Group();
    const edge = new THREE.Mesh(new THREE.CylinderGeometry(0.85, 0.85, 0.2, 48), colors.ink);
    edge.rotation.x = Math.PI / 2;
    const face = new THREE.Mesh(new THREE.CylinderGeometry(0.79, 0.79, 0.20, 48), colors.cyan);
    face.rotation.x = Math.PI / 2;
    face.position.z = 0.09;
    const groove = new THREE.Mesh(new THREE.TorusGeometry(0.48, 0.033, 10, 48), colors.ink);
    groove.position.z = 0.225;
    const middle = new THREE.Mesh(new THREE.CylinderGeometry(0.19, 0.19, 0.25, 24), colors.pink);
    middle.rotation.x = Math.PI / 2;
    middle.position.z = 0.12;
    node.add(edge, face, groove, middle);
    return node;
  }

  function bolt() {
    const shape = new THREE.Shape();
    const points = [[-0.19, 0.84], [0.37, 0.14], [0.06, 0.14],
      [0.30, -0.89], [-0.52, 0.00], [-0.16, 0.00]];
    points.forEach(([x, y], i) => i ? shape.lineTo(x, y) : shape.moveTo(x, y));
    shape.closePath();
    const node = new THREE.Group();
    const edge = extruded(shape, colors.ink);
    edge.scale.set(1.12, 1.12, 1);
    edge.position.z = -0.05;
    const face = extruded(shape, colors.lilac);
    face.position.z = 0.045;
    node.add(edge, face);
    return node;
  }

  add(star(), -3.42, 1.06, 0.88, 0).rotation.z = 0.17;
  add(disc(), 3.29, 0.68, 0.77, 2.1).rotation.y = -0.2;
  add(bolt(), -3.03, -1.12, 0.58, 4.1).rotation.z = -0.22;

  let frameId = 0;
  let lastFrame = 0;
  let paused = false;
  let visible = true;
  let previousTime = performance.now();
  let elapsed = 0;
  let observer;
  const pointer = new THREE.Vector2();

  function resize() {
    const bounds = host.getBoundingClientRect();
    if (bounds.width < 1 || bounds.height < 1) return;
    const width = bounds.width;
    const height = bounds.height;
    camera.left = -5;
    camera.right = 5;
    camera.top = 5 * height / width;
    camera.bottom = -camera.top;
    camera.updateProjectionMatrix();

    // Render at up to 2x CSS pixels instead of the previous blurry 1.5x.
    // Pixel budget prevents large canvases from exhausting mobile GPUs.
    const pixelBudget = Math.sqrt(2400000 / (width * height));
    renderer.setPixelRatio(Math.max(1, Math.min(window.devicePixelRatio || 1, 2, pixelBudget)));
    renderer.setSize(width, height, false);
    renderer.render(scene, camera);
  }

  function tick(now) {
    frameId = requestAnimationFrame(tick);
    if (now - lastFrame < 1000 / 30) return;
    elapsed += Math.min((now - previousTime) / 1000, 0.08);
    previousTime = now;
    lastFrame = now;

    actors.forEach(({ node, startY, phase }) => {
      node.position.y = startY + 0.055 * Math.sin(elapsed * 0.7 + phase);
      node.rotation.y += ((pointer.x * 0.11) - node.rotation.y) * 0.02;
    });
    renderer.render(scene, camera);
  }

  function stop() {
    if (frameId) cancelAnimationFrame(frameId);
    frameId = 0;
  }

  function syncMotion() {
    const enabled = !paused && visible && !document.hidden && !reduceMotion.matches;
    if (enabled && !frameId) {
      previousTime = performance.now();
      lastFrame = 0;
      frameId = requestAnimationFrame(tick);
    }
    if (!enabled) {
      stop();
      renderer.render(scene, camera);
    }
  }

  host.addEventListener('pointermove', event => {
    if (event.pointerType === 'touch') return;
    const rect = host.getBoundingClientRect();
    pointer.x = (event.clientX - rect.left) / rect.width * 2 - 1;
  }, { passive: true });
  host.addEventListener('pointerleave', () => { pointer.x = 0; });

  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      syncMotion();
    }, { threshold: 0.05 });
    observer.observe(host);
  }
  new ResizeObserver(resize).observe(host);
  document.addEventListener('visibilitychange', syncMotion);

  motionButton.hidden = false;
  motionButton.addEventListener('click', () => {
    paused = !paused;
    motionButton.textContent = paused ? 'Play animation' : 'Pause animation';
    motionButton.setAttribute('aria-pressed', String(!paused));
    motionButton.setAttribute('aria-label', motionButton.textContent);
    syncMotion();
  });

  reduceMotion.addEventListener('change', () => {
    stop();
    if (reduceMotion.matches) {
      canvas.classList.remove('is-ready');
      motionButton.hidden = true;
    } else {
      paused = false;
      canvas.classList.add('is-ready');
      motionButton.hidden = false;
      syncMotion();
    }
  });

  canvas.addEventListener('webglcontextlost', event => {
    event.preventDefault();
    stop();
    canvas.classList.remove('is-ready');
    motionButton.hidden = true;
    observer?.disconnect();
  });

  resize();
  canvas.classList.add('is-ready');
  syncMotion();
}
