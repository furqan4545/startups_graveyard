// const { createCanvas } = require('canvas');
// const fs = require('fs');
// const { execSync } = require('child_process');

// const canvas = createCanvas(1000, 500); // Set canvas size
// const ctx = canvas.getContext('2d');

// const text = ["Out", "now"];
// const fontSize = 60; // Equivalent to 3.8em
// const letterSpacing = 60; // Equivalent to 0.5em
// const frameRate = 25; // Frames per second
// const videoDuration = 10; // Total video duration in seconds (loop duration)
// const totalFrames = frameRate * videoDuration; // Total frames for the video

// ctx.font = `${fontSize}px Arial`;
// ctx.textBaseline = 'middle';
// ctx.textAlign = 'center';

// // Reduced duration for each animation phase to increase speed
// const scaleDuration = 10; // Duration of scaling effect
// const fadeOutStart = 50; // Start time of fade out effect
// const fadeOutDuration = 50; // Duration of fade out effect

// function drawFrame(frame) {
//   ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
//   ctx.fillStyle = 'white';

//   text.forEach((word, index) => {
//     // Calculate scale and opacity based on frame
//     const scale = Math.max(14 - 14 * (frame - scaleDuration * index) / scaleDuration, 1);
//     const opacity = Math.min((frame - scaleDuration * index) / scaleDuration, 1);

//     ctx.save();
//     ctx.globalAlpha = opacity;
//     ctx.translate(canvas.width / 2, canvas.height / 2);
//     ctx.scale(scale, scale);
//     ctx.fillText(word, (fontSize + letterSpacing) * index * (1 / scale), 0);
//     ctx.restore();
//   });

//   if (frame > fadeOutStart) ctx.globalAlpha = Math.max(1 - (frame - fadeOutStart) / fadeOutDuration, 0); // Fade out effect

//   const buffer = canvas.toBuffer('image/png');
//   fs.writeFileSync(`./frame_${frame.toString().padStart(4, '0')}.png`, buffer);
// }

// for (let frame = 0; frame < totalFrames; frame++) {
//   drawFrame(frame);
// }

// // Compile the frames into a video
// execSync('ffmpeg -framerate 25 -i frame_%04d.png -c:v libx264 -t 10 -pix_fmt yuv420p output.mp4');

// // Clean up the frame images
// for (let frame = 0; frame < totalFrames; frame++) {
//   fs.unlinkSync(`./frame_${frame.toString().padStart(4, '0')}.png`);
// }

const { createCanvas } = require('canvas');
const fs = require('fs');
const { execSync } = require('child_process');

const canvas = createCanvas(1000, 500); // Set canvas size
const ctx = canvas.getContext('2d');

const text = ["Out", "now"];
const fontSize = 80; // Equivalent to 3.8em
const letterSpacing = 70; // Equivalent to 0.5em
const frameRate = 25; // Frames per second
const loopDuration = 1; // Duration of each loop in seconds
const totalLoops = 10; // Number of loops for a 10-second video
const totalFrames = frameRate * loopDuration * totalLoops; // Total frames for the video

ctx.font = `${fontSize}px Arial`;
ctx.textBaseline = 'middle';
ctx.textAlign = 'center';

// Animation parameters
const scaleDuration = frameRate * 0.09; // Duration of scaling effect (in frames)
const fadeOutStart = frameRate * 1; // Start time of fade out effect (in frames)
const fadeOutDuration = frameRate * 1; // Duration of fade out effect (in frames)

function drawFrame(frame) {
  // Calculate the frame number within the current loop
  const loopFrame = frame % (frameRate * loopDuration);

  ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
  ctx.fillStyle = 'white';

  text.forEach((word, index) => {
    // Calculate scale and opacity based on loopFrame
    const scale = Math.max(14 - 14 * (loopFrame - scaleDuration * index) / scaleDuration, 1);
    const opacity = Math.min((loopFrame - scaleDuration * index) / scaleDuration, 1);

    ctx.save();
    ctx.globalAlpha = opacity;
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.scale(scale, scale);
    ctx.fillText(word, (fontSize + letterSpacing) * index * (1 / scale), 0);
    ctx.restore();
  });

  if (loopFrame > fadeOutStart) ctx.globalAlpha = Math.max(1 - (loopFrame - fadeOutStart) / fadeOutDuration, 0); // Fade out effect

  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(`./frame_${frame.toString().padStart(4, '0')}.png`, buffer);
}

for (let frame = 0; frame < totalFrames; frame++) {
  drawFrame(frame);
}

// Compile the frames into a video using H.265 codec
execSync('ffmpeg -framerate 25 -i frame_%04d.png -c:v libx265 -t 10 -pix_fmt yuv420p output.mp4');

// Clean up the frame images
for (let frame = 0; frame < totalFrames; frame++) {
  fs.unlinkSync(`./frame_${frame.toString().padStart(4, '0')}.png`);
}


