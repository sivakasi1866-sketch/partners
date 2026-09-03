import React, { useRef, useEffect } from 'react';

export interface DitherProps {
  waveColor?: [number, number, number];
  disableAnimation?: boolean;
  enableMouseInteraction?: boolean;
  mouseRadius?: number;
  colorNum?: number;
  pixelSize?: number;
  waveAmplitude?: number;
  waveFrequency?: number;
  waveSpeed?: number;
}

export const Dither: React.FC<DitherProps> = ({
  waveColor = [0.32, 0.15, 1],
  disableAnimation = false,
  enableMouseInteraction = true,
  mouseRadius = 1,
  colorNum = 4,
  pixelSize = 2,
  waveAmplitude = 0.3,
  waveFrequency = 3,
  waveSpeed = 0.05,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) return;

    // Compile Shader Function
    const compileShader = (type: number, source: string) => {
      const shader = (gl as WebGLRenderingContext).createShader(type);
      if (!shader) return null;
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error('Shader compile error:', gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
      }
      return shader;
    };

    const vsSource = `
      attribute vec2 position;
      void main() {
        gl_Position = vec4(position, 0.0, 1.0);
      }
    `;

    const fsSource = `
      precision mediump float;
      uniform vec2 uResolution;
      uniform float uTime;
      uniform vec3 uWaveColor;
      uniform float uColorNum;
      uniform float uPixelSize;
      uniform float uWaveAmplitude;
      uniform float uWaveFrequency;
      uniform vec2 uMouse;
      uniform float uEnableMouse;
      uniform float uMouseRadius;

      float random(vec2 st) {
          return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
      }

      void main() {
          vec2 coord = gl_FragCoord.xy;
          // Apply pixel size
          vec2 pixelated = floor(coord / max(1.0, uPixelSize)) * max(1.0, uPixelSize);
          vec2 uv = pixelated / uResolution;

          // Background color (very dark blue/slate)
          vec3 bgColor = vec3(0.02, 0.04, 0.08);

          // Wave function
          float waveX = sin(uv.x * uWaveFrequency + uTime) * 0.5;
          float waveY = cos(uv.y * uWaveFrequency + uTime * 0.8) * 0.5;
          float wave = (waveX + waveY) * uWaveAmplitude;
          
          if (uEnableMouse > 0.5) {
              float dist = distance(uv, uMouse);
              if (dist < uMouseRadius) {
                  float intensity = (uMouseRadius - dist) / uMouseRadius;
                  wave += intensity * 0.5;
              }
          }

          // Mix colors based on wave
          vec3 color = mix(bgColor, uWaveColor, max(0.0, wave));

          // Dither noise
          float noise = (random(pixelated) - 0.5) * 0.15;
          color += noise;

          // Color quantization (dither bands)
          color = floor(color * uColorNum) / max(1.0, (uColorNum - 1.0));

          gl_FragColor = vec4(color, 1.0);
      }
    `;

    const vertexShader = compileShader(gl.VERTEX_SHADER, vsSource);
    const fragmentShader = compileShader(gl.FRAGMENT_SHADER, fsSource);
    if (!vertexShader || !fragmentShader) return;

    const program = gl.createProgram();
    if (!program) return;
    
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Program link error:', gl.getProgramInfoLog(program));
      return;
    }
    
    gl.useProgram(program);

    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    const positions = new Float32Array([
      -1.0, -1.0,
       1.0, -1.0,
      -1.0,  1.0,
      -1.0,  1.0,
       1.0, -1.0,
       1.0,  1.0,
    ]);
    gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

    const positionLocation = gl.getAttribLocation(program, 'position');
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

    const locResolution = gl.getUniformLocation(program, 'uResolution');
    const locTime = gl.getUniformLocation(program, 'uTime');
    const locWaveColor = gl.getUniformLocation(program, 'uWaveColor');
    const locColorNum = gl.getUniformLocation(program, 'uColorNum');
    const locPixelSize = gl.getUniformLocation(program, 'uPixelSize');
    const locWaveAmplitude = gl.getUniformLocation(program, 'uWaveAmplitude');
    const locWaveFrequency = gl.getUniformLocation(program, 'uWaveFrequency');
    const locMouse = gl.getUniformLocation(program, 'uMouse');
    const locEnableMouse = gl.getUniformLocation(program, 'uEnableMouse');
    const locMouseRadius = gl.getUniformLocation(program, 'uMouseRadius');

    let mouse = { x: 0.5, y: 0.5 };
    
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = (e.clientX - rect.left) / rect.width;
      mouse.y = 1.0 - ((e.clientY - rect.top) / rect.height);
    };

    if (enableMouseInteraction) {
      window.addEventListener('mousemove', handleMouseMove);
    }

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      gl.viewport(0, 0, canvas.width, canvas.height);
    };

    window.addEventListener('resize', resize);
    resize();

    let animationFrame: number;
    let time = 0;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const isMobile = window.innerWidth <= 768;
    const finalWaveSpeed = (prefersReducedMotion || disableAnimation) ? 0 : (isMobile ? waveSpeed * 0.5 : waveSpeed);

    const render = () => {
      time += finalWaveSpeed;

      gl.useProgram(program);
      gl.uniform2f(locResolution, canvas.width, canvas.height);
      gl.uniform1f(locTime, time);
      gl.uniform3fv(locWaveColor, waveColor);
      gl.uniform1f(locColorNum, colorNum);
      gl.uniform1f(locPixelSize, pixelSize);
      gl.uniform1f(locWaveAmplitude, waveAmplitude);
      gl.uniform1f(locWaveFrequency, waveFrequency);
      gl.uniform2f(locMouse, mouse.x, mouse.y);
      gl.uniform1f(locEnableMouse, enableMouseInteraction && !isMobile ? 1.0 : 0.0);
      gl.uniform1f(locMouseRadius, mouseRadius);

      gl.drawArrays(gl.TRIANGLES, 0, 6);

      if (!disableAnimation && !prefersReducedMotion) {
        animationFrame = requestAnimationFrame(render);
      }
    };

    render();

    return () => {
      window.removeEventListener('resize', resize);
      if (enableMouseInteraction) {
        window.removeEventListener('mousemove', handleMouseMove);
      }
      if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, [
    waveColor, disableAnimation, enableMouseInteraction, mouseRadius,
    colorNum, pixelSize, waveAmplitude, waveFrequency, waveSpeed
  ]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none -z-10"
      style={{ opacity: 0.8 }}
    />
  );
};
