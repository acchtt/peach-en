/**
 * IVE RADAR — decorative Three.js comic hero.
 * The existing CSS, headline and chart UI remain functional without WebGL.
 */
const host = document.querySelector('.hero-right');
const canvas = document.querySelector('#hero-three-canvas');
const toggle = document.querySelector('#hero-motion-toggle');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

if (host && canvas && toggle && !reduceMotion.matches) {
  let available = false;
  try {
    available = Boolean(document.createElement('canvas').getContext('webgl2'));
  } catch { /* keep CSS fallback */ }
  if (available) {
    try {
      const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js');
      mountScene(THREE);
    } catch (error) {
      console.info('IVE RADAR: 3D unavailable; using static hero.', error);
    }
  }
}

function mountScene(THREE) {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: window.devicePixelRatio <= 1.6,
      powerPreference: 'low-power'
    });
  } catch (error) {
    console.info('IVE RADAR: WebGL renderer unavailable.', error);
    return;
  }

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-6, 6, 4, -4, 0.1, 40);
  camera.position.set(0, 0, 16);

  const whole = new THREE.Group();
  scene.add(whole);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x796099, 2.1));
  const key = new THREE.DirectionalLight(0xffffff, 2);
  key.position.set(-4, 7, 12);
  scene.add(key);

  const makeMaterial = color => new THREE.MeshStandardMaterial({
    color, roughness: 0.48, metalness: 0, flatShading: true
  });
  const m = {
    ink: makeMaterial(0x101010),
    yellow: makeMaterial(0xf8ff1b),
    cyan: makeMaterial(0x09d7db),
    pink: makeMaterial(0xffc0eb),
    purple: makeMaterial(0xa28bfd),
    white: makeMaterial(0xffffff)
  };

  const actors = [];
  function place(node, x, y, z, scale, phase) {
    node.position.set(x, y, z);
    node.scale.setScalar(scale);
    whole.add(node);
    actors.push({ node, y, phase });
    return node;
  }

  function starShape(tips, outer, inner) {
    const shape = new THREE.Shape();
    for (let i = 0; i < tips * 2; i++) {
      const angle = Math.PI / 2 + i * Math.PI / tips;
      const radius = i % 2 === 0 ? outer : inner;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      if (!i) shape.moveTo(x, y);
      else shape.lineTo(x, y);
    }
    shape.closePath();
    return shape;
  }

  function star(color, tips = 5) {
    const node = new THREE.Group();
    const geo = new THREE.ExtrudeGeometry(starShape(tips, 0.87, 0.39), {
      depth: 0.24, steps: 1, bevelEnabled: true,
      bevelSegments: 1, bevelSize: 0.065, bevelThickness: 0.065,
      curveSegments: 2
    });
    const border = new THREE.Mesh(geo, m.ink);
    border.scale.set(1.17, 1.17, 1.06);
    border.position.z = -0.16;
    node.add(border);
    const face = new THREE.Mesh(geo, m[color]);
    face.position.z = 0.04;
    node.add(face);
    return node;
  }

  function token(color) {
    const node = new THREE.Group();
    const back = new THREE.Mesh(
      new THREE.CylinderGeometry(1.03, 1.03, 0.34, 28), m.ink);
    back.rotation.x = Math.PI / 2;
    back.position.z = -0.04;
    const front = new THREE.Mesh(
      new THREE.CylinderGeometry(0.89, 0.89, 0.35, 28), m[color]);
    front.rotation.x = Math.PI / 2;
    front.position.z = 0.16;
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(0.58, 0.065, 8, 32), m.ink);
    ring.position.z = 0.37;
    const center = new THREE.Mesh(new THREE.OctahedronGeometry(0.3), m.ink);
    center.position.z = 0.49;
    center.rotation.z = Math.PI / 4;
    node.add(back, front, ring, center);
    return node;
  }

  function bolt(color) {
    const node = new THREE.Group();
    const shape = new THREE.Shape();
    const points = [[-0.18, 1], [0.53, 0.19], [0.1, 0.19],
      [0.4, -0.93], [-0.63, 0.05], [-0.13, 0.05]];
    for (const [i, point] of points.entries()) {
      if (!i) shape.moveTo(...point);
      else shape.lineTo(...point);
    }
    shape.closePath();
    const geo = new THREE.ExtrudeGeometry(shape, {
      depth: 0.16, steps: 1, bevelEnabled: false
    });
    const shadow = new THREE.Mesh(geo, m.ink);
    shadow.scale.set(1.22, 1.2, 1);
    shadow.position.z = -0.12;
    const front = new THREE.Mesh(geo, m[color]);
    front.position.z = 0.07;
    node.add(shadow, front);
    return node;
  }

  function hoop(color) {
    const node = new THREE.Group();
    const back = new THREE.Mesh(new THREE.TorusGeometry(0.77, 0.25, 8, 30), m.ink);
    const front = new THREE.Mesh(new THREE.TorusGeometry(0.77, 0.17, 8, 30), m[color]);
    front.position.z = 0.16;
    node.add(back, front);
    return node;
  }

  place(star('yellow', 8), -4.65, 2.05, 1.1, 1.04, 0).rotation.z = -0.16;
  place(token('cyan'), -4.37, -1.47, -0.2, 0.82, 1.5).rotation.y = 0.25;
  place(hoop('white'), -3.4, 0.23, -1.4, 0.67, 2.5).rotation.y = -0.38;
  place(star('pink'), 4.75, -1.87, 1.15, 1.2, 3.1).rotation.z = 0.35;
  place(token('yellow'), 4.39, 1.74, -0.3, 0.82, 4.2).rotation.y = -0.2;
  place(hoop('cyan'), 3.59, 0.18, -1.6, 0.67, 5.1).rotation.x = 0.23;
  place(bolt('cyan'), -2.68, 2.13, -1.4, 0.62, 2.1).rotation.z = -0.42;
  place(bolt('yellow'), 2.76, -2.38, -1.3, 0.75, 5.6).rotation.z = 0.18;
  place(star('purple', 4), -5.68, 0.13, -1.7, 0.34, 1.1);
  place(star('white', 4), 5.62, 0.18, -1.7, 0.41, 4.1);
  place(star('cyan', 5), 2.87, 2.5, -1.9, 0.35, 2.8);

  const dots = [
    [-2.55, 1.35, 0.12, 'yellow'], [-3.12, -1.45, 0.09, 'white'],
    [2.65, 1.43, 0.11, 'white'], [3, -1.13, 0.14, 'pink'],
    [-5.6, -2.5, 0.1, 'cyan'], [5.6, 2.45, 0.11, 'yellow'],
    [3.3, 2.57, 0.08, 'purple'], [-3.5, 2.65, 0.08, 'pink']
  ];
  for (const [x, y, radius, color] of dots) {
    place(new THREE.Mesh(new THREE.IcosahedronGeometry(radius), m[color]),
      x, y, -1.8, 1, x + y);
  }

  let visible = true;
  let paused = false;
  let frame = 0;
  let previous = 0;
  const pointer = new THREE.Vector2();
  const clock = new THREE.Clock();

  function resize() {
    const rect = host.getBoundingClientRect();
    const w = Math.max(rect.width, 1);
    const h = Math.max(rect.height, 1);
    camera.left = -6;
    camera.right = 6;
    camera.top = (6 * h) / w;
    camera.bottom = -camera.top;
    camera.updateProjectionMatrix();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    renderer.setSize(w, h, false);
    renderer.render(scene, camera);
  }

  function animate(now) {
    frame = requestAnimationFrame(animate);
    if (now - previous < 1000 / 30) return;
    previous = now;
    const time = clock.getElapsedTime();
    whole.rotation.y += (pointer.x * 0.12 - whole.rotation.y) * 0.045;
    whole.rotation.x += (-pointer.y * 0.08 - whole.rotation.x) * 0.045;
    actors.forEach(({ node, y, phase }, i) => {
      node.position.y = y + Math.sin(time * 0.8 + phase) * 0.12;
      node.rotation.z += Math.sin(time + i) * 0.0005;
    });
    renderer.render(scene, camera);
  }
  function stop() {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
  }
  function sync() {
    const run = visible && !paused && !document.hidden && !reduceMotion.matches;
    if (run && !frame) {
      previous = 0;
      clock.start();
      frame = requestAnimationFrame(animate);
    } else if (!run) {
      stop();
      renderer.render(scene, camera);
    }
  }

  host.addEventListener('pointermove', (event) => {
    if (event.pointerType === 'touch') return;
    const r = host.getBoundingClientRect();
    pointer.x = ((event.clientX - r.left) / r.width - 0.5) * 2;
    pointer.y = ((event.clientY - r.top) / r.height - 0.5) * 2;
  }, { passive: true });
  host.addEventListener('pointerleave', () => pointer.set(0, 0));

  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    sync();
  }, { threshold: 0.05 }).observe(host);
  new ResizeObserver(resize).observe(host);
  document.addEventListener('visibilitychange', sync);

  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    paused = !paused;
    toggle.textContent = paused ? '▶ PLAY 3D' : 'Ⅱ PAUSE 3D';
    toggle.setAttribute('aria-pressed', String(!paused));
    toggle.setAttribute('aria-label',
      paused ? 'Play 3D animation' : 'Pause 3D animation');
    sync();
  });
  reduceMotion.addEventListener('change', () => {
    if (reduceMotion.matches) {
      paused = true;
      stop();
      toggle.hidden = true;
    } else {
      paused = false;
      toggle.hidden = false;
      sync();
    }
  });
  canvas.addEventListener('webglcontextlost', event => {
    event.preventDefault();
    stop();
    canvas.style.opacity = '0';
    toggle.hidden = true;
  });
  resize();
  canvas.classList.add('is-ready');
  sync();
}
