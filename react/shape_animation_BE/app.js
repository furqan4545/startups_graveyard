const { createCanvas } = require('canvas');
const fs = require('fs');
const { execSync } = require('child_process');

const canvas = createCanvas(1000, 1000); //optional height and width of canvas
const ctx = canvas.getContext('2d');

ctx.fillStyle = '#000000';
ctx.fillRect(0, 0, 1000, 1000);
ctx.fillStyle = '#ffffff';
ctx.font = '200px Impact';
ctx.fillText('Hello World!', 50, 500, 900); // text, x, y, max width
ctx.strokeStyle = '#ffffff';
// text color to yellow 
ctx.fillStyle = '#ffff00';

const buffer = canvas.toBuffer('image/png');
fs.writeFileSync('./test.png', buffer);

// Generate the video using FFmpeg
execSync('ffmpeg -loop 1 -i test.png -c:v libx264 -t 10 -pix_fmt yuv420p output.mp4');

// Clean up the temporary image file
fs.unlinkSync('./test.png');
