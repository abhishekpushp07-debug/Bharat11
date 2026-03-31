/**
 * CelebrationSounds — Procedural Sound Effects via Web Audio API
 * No external audio files needed — pure synthesized cricket stadium sounds
 * 
 * SIX: Massive crowd roar + bass hit + reverb
 * FOUR: Sharp bat crack + crowd cheer
 * WICKET: Stumps crash + crowd gasp  
 * PRIZE: Victory fanfare + crowd eruption
 */

let audioCtx = null;

function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

// Create white noise buffer (crowd sounds base)
function createNoiseBuffer(ctx, duration = 1) {
  const sampleRate = ctx.sampleRate;
  const length = sampleRate * duration;
  const buffer = ctx.createBuffer(1, length, sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < length; i++) {
    data[i] = Math.random() * 2 - 1;
  }
  return buffer;
}

// Bass impact hit
function playBassHit(ctx, time, gain = 0.6) {
  const osc = ctx.createOscillator();
  const g = ctx.createGain();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(150, time);
  osc.frequency.exponentialRampToValueAtTime(30, time + 0.3);
  g.gain.setValueAtTime(gain, time);
  g.gain.exponentialRampToValueAtTime(0.001, time + 0.4);
  osc.connect(g).connect(ctx.destination);
  osc.start(time);
  osc.stop(time + 0.4);
}

// Crack sound (bat hitting ball)
function playCrack(ctx, time, gain = 0.4) {
  const noise = ctx.createBufferSource();
  noise.buffer = createNoiseBuffer(ctx, 0.1);
  const filter = ctx.createBiquadFilter();
  filter.type = 'highpass';
  filter.frequency.value = 2000;
  const g = ctx.createGain();
  g.gain.setValueAtTime(gain, time);
  g.gain.exponentialRampToValueAtTime(0.001, time + 0.08);
  noise.connect(filter).connect(g).connect(ctx.destination);
  noise.start(time);
  noise.stop(time + 0.1);
}

// Crowd roar (filtered noise with envelope)
function playCrowdRoar(ctx, time, duration = 2, gain = 0.25) {
  const noise = ctx.createBufferSource();
  noise.buffer = createNoiseBuffer(ctx, duration + 0.5);
  const filter = ctx.createBiquadFilter();
  filter.type = 'bandpass';
  filter.frequency.value = 800;
  filter.Q.value = 0.5;
  const g = ctx.createGain();
  g.gain.setValueAtTime(0, time);
  g.gain.linearRampToValueAtTime(gain, time + 0.3);
  g.gain.setValueAtTime(gain, time + duration * 0.6);
  g.gain.exponentialRampToValueAtTime(0.001, time + duration);
  noise.connect(filter).connect(g).connect(ctx.destination);
  noise.start(time);
  noise.stop(time + duration + 0.5);
}

// Stump crash (low thud + high crack)
function playStumpCrash(ctx, time) {
  // Low thud
  const osc = ctx.createOscillator();
  const g1 = ctx.createGain();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(100, time);
  osc.frequency.exponentialRampToValueAtTime(20, time + 0.3);
  g1.gain.setValueAtTime(0.5, time);
  g1.gain.exponentialRampToValueAtTime(0.001, time + 0.3);
  osc.connect(g1).connect(ctx.destination);
  osc.start(time);
  osc.stop(time + 0.3);

  // Wood crack
  const noise = ctx.createBufferSource();
  noise.buffer = createNoiseBuffer(ctx, 0.15);
  const filter = ctx.createBiquadFilter();
  filter.type = 'bandpass';
  filter.frequency.value = 3000;
  filter.Q.value = 2;
  const g2 = ctx.createGain();
  g2.gain.setValueAtTime(0.35, time);
  g2.gain.exponentialRampToValueAtTime(0.001, time + 0.12);
  noise.connect(filter).connect(g2).connect(ctx.destination);
  noise.start(time);
  noise.stop(time + 0.15);

  // Scatter tinkle (bails)
  setTimeout(() => {
    const n2 = ctx.createBufferSource();
    n2.buffer = createNoiseBuffer(ctx, 0.2);
    const f2 = ctx.createBiquadFilter();
    f2.type = 'highpass';
    f2.frequency.value = 5000;
    const g3 = ctx.createGain();
    const t = ctx.currentTime;
    g3.gain.setValueAtTime(0.15, t);
    g3.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
    n2.connect(f2).connect(g3).connect(ctx.destination);
    n2.start(t);
    n2.stop(t + 0.2);
  }, 80);
}

// Victory fanfare (ascending notes)
function playFanfare(ctx, time) {
  const notes = [523, 659, 784, 1047]; // C5, E5, G5, C6
  notes.forEach((freq, i) => {
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.value = freq;
    const t = time + i * 0.15;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(0.2, t + 0.05);
    g.gain.setValueAtTime(0.2, t + 0.12);
    g.gain.exponentialRampToValueAtTime(0.001, t + 0.4);
    osc.connect(g).connect(ctx.destination);
    osc.start(t);
    osc.stop(t + 0.5);
  });
}

// Shimmer/sparkle (for prize)
function playSparkle(ctx, time) {
  for (let i = 0; i < 6; i++) {
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.value = 2000 + Math.random() * 4000;
    const t = time + i * 0.08;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(0.06, t + 0.02);
    g.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
    osc.connect(g).connect(ctx.destination);
    osc.start(t);
    osc.stop(t + 0.2);
  }
}

// ============ PUBLIC API ============

export function playSixSound() {
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;
    playBassHit(ctx, now, 0.7);
    playCrack(ctx, now + 0.02, 0.5);
    playCrowdRoar(ctx, now + 0.1, 2.5, 0.3);
  } catch (e) {
    // Silently fail — sounds are enhancement, not critical
  }
}

export function playFourSound() {
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;
    playCrack(ctx, now, 0.45);
    playBassHit(ctx, now + 0.01, 0.3);
    playCrowdRoar(ctx, now + 0.1, 1.8, 0.2);
  } catch (e) {}
}

export function playWicketSound() {
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;
    playStumpCrash(ctx, now);
    // Crowd gasp — short, sharp noise burst
    const noise = ctx.createBufferSource();
    noise.buffer = createNoiseBuffer(ctx, 0.5);
    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = 600;
    filter.Q.value = 0.3;
    const g = ctx.createGain();
    g.gain.setValueAtTime(0, now + 0.15);
    g.gain.linearRampToValueAtTime(0.2, now + 0.25);
    g.gain.exponentialRampToValueAtTime(0.001, now + 0.8);
    noise.connect(filter).connect(g).connect(ctx.destination);
    noise.start(now + 0.15);
    noise.stop(now + 1);
  } catch (e) {}
}

export function playPrizeSound() {
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;
    playFanfare(ctx, now);
    playSparkle(ctx, now + 0.6);
    playCrowdRoar(ctx, now + 0.5, 3, 0.3);
    // Second sparkle wave
    setTimeout(() => {
      playSparkle(ctx, ctx.currentTime);
    }, 1200);
  } catch (e) {}
}

export function playCelebrationSound(type) {
  switch (type) {
    case 'six': return playSixSound();
    case 'four': return playFourSound();
    case 'wicket': return playWicketSound();
    case 'prize': return playPrizeSound();
    default: return;
  }
}
