
const { createCanvas } = require('canvas');
const fs = require('fs');
const { execSync } = require('child_process');

const text = "This is a simple string.";
const fontSize = 30 * 2; // Adjustable font size
const padding = 20 * 2; // Adjustable padding

// Prepare a temporary canvas to measure text
const tempCanvas = createCanvas(1000, 500); // Size can be adjusted
const tempCtx = tempCanvas.getContext('2d');
tempCtx.font = `${fontSize}px Arial`;
const textWidth = tempCtx.measureText(text).width;
const textHeight = fontSize;

// Adjust canvas size and ensure it's divisible by 2
const canvasWidth = Math.ceil((textWidth + padding * 2) / 2) * 2;
const canvasHeight = Math.ceil((textHeight + padding * 2) / 2) * 2;
const canvas = createCanvas(canvasWidth, canvasHeight);
const ctx = canvas.getContext('2d');

const frameRate = 25; // Frames per second
const textAnimationDuration = 1; // Duration for the text to render completely in seconds
const videoDuration = 10; // Total video duration in seconds
const totalFrames = frameRate * videoDuration; // Total frames for a 10-second video

for (let frame = 0; frame < totalFrames; frame++) {
  const progress = (frame % (frameRate * textAnimationDuration)) / (frameRate * textAnimationDuration);
  const currentTextLength = Math.floor(progress * text.length);
  const currentText = text.substring(0, currentTextLength);

  ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
  ctx.fillStyle = 'white'; // Text color
  ctx.font = `${fontSize}px Arial`;
  ctx.textBaseline = 'middle'; // Align text vertically in the middle
  ctx.fillText(currentText, padding, canvasHeight / 2); // Draw the text centered

  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(`./frame_${frame.toString().padStart(4, '0')}.png`, buffer);
}

// Compile the frames into a video using FFmpeg without scaling
execSync(`ffmpeg -framerate 25 -i frame_%04d.png -c:v libx264 -t 10 -pix_fmt yuv420p output.mp4`);

// Clean up the frame images
for (let frame = 0; frame < totalFrames; frame++) {
  fs.unlinkSync(`./frame_${frame.toString().padStart(4, '0')}.png`);
}



