import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

interface CameraGizmoProps {
  rotate: number; // 0 - 360
  vertical: number; // -90 to 90
  zoom: number; // 0.1 to 5
}

export default function CameraGizmo({ rotate, vertical, zoom }: CameraGizmoProps) {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    // 1. Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#162129');
    
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(240, 240);
    mountRef.current.appendChild(renderer.domElement);

    // 2. Objects
    // Target Plane (Representing the subject)
    const geometry = new THREE.PlaneGeometry(1, 1);
    const material = new THREE.MeshBasicMaterial({ 
        color: 0x7c3aed, 
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.8
    });
    const plane = new THREE.Mesh(geometry, material);
    scene.add(plane);

    // Grid helper
    const grid = new THREE.GridHelper(4, 10, 0x334155, 0x1e293b);
    grid.rotation.x = Math.PI / 2;
    scene.add(grid);

    // Camera Visualizer (A box that represents the camera)
    const camGeo = new THREE.BoxGeometry(0.3, 0.2, 0.4);
    const camMat = new THREE.MeshBasicMaterial({ color: 0x3b82f6 });
    const camMesh = new THREE.Mesh(camGeo, camMat);
    scene.add(camMesh);

    // Line from cam to target
    const lineMat = new THREE.LineBasicMaterial({ color: 0xfacc15 });
    
    // 3. Update Function
    const updatePosition = () => {
        // Spherical coordinates calculation
        // Radius depends on Zoom
        const radius = 5 / zoom; 
        const phi = THREE.MathUtils.degToRad(90 - vertical); // Vertical elevation
        const theta = THREE.MathUtils.degToRad(rotate); // Horizontal rotation

        camMesh.position.setFromSphericalCoords(radius, phi, theta);
        camMesh.lookAt(0, 0, 0);

        // Update fixed camera for the visualizer view
        camera.position.set(4, 4, 4);
        camera.lookAt(0, 0, 0);
    };

    // 4. Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      updatePosition();
      renderer.render(scene, camera);
    };

    animate();

    // Clean up
    return () => {
      mountRef.current?.removeChild(renderer.domElement);
      renderer.dispose();
    };
  }, [rotate, vertical, zoom]);

  return (
    <div className="relative w-full aspect-square rounded-[32px] overflow-hidden border border-slate-800 bg-[#162129] shadow-inner group">
       <div ref={mountRef} className="w-full h-full" />
       
       <div className="absolute top-4 left-4 flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]" />
            <span className="text-[9px] font-black text-white uppercase tracking-widest">Sovereign Point-of-View</span>
          </div>
          <span className="text-[7px] font-bold text-slate-500 uppercase tracking-tighter">Renderizado Clínica Visual v2.0</span>
       </div>

       <div className="absolute bottom-4 right-4 text-right">
          <p className="text-[8px] font-mono text-slate-400">YAW: {rotate.toFixed(0)}°</p>
          <p className="text-[8px] font-mono text-slate-400">PITCH: {vertical.toFixed(0)}°</p>
          <p className="text-[8px] font-mono text-slate-400">MAG: {zoom.toFixed(1)}x</p>
       </div>
    </div>
  );
}
