// const { createCanvas } = require('canvas');
// const fs = require('fs');
// const { execSync } = require('child_process');

// const canvas = createCanvas(1000, 200); //optional height and width of canvas
// const ctx = canvas.getContext('2d');
// const input_text = "This is a simple string.";
// const shape_duration = 10; // Total video duration in seconds

// // Video file path
// const outputVideoPath = './output_video/output.mp4';
// // Delete the video file if it already exists
// if (fs.existsSync(outputVideoPath)) {
//   fs.unlinkSync(outputVideoPath);
// }

// // Ensure the images directory exists
// const imagesDir = './images/';
// // Ensure the images directory exists
// if (!fs.existsSync(imagesDir)) {
//   fs.mkdirSync(imagesDir);
// }


// ctx.fillStyle = '#000000';
// ctx.fillRect(0, 0, 1000, 200);
// ctx.fillStyle = '#ffffff';
// ctx.font = '100px Impact';
// ctx.fillText(`${input_text}`, 50, 100, 900); // text, x, y, max width
// ctx.strokeStyle = '#ffffff';
// // text color to yellow 
// ctx.fillStyle = '#ffff00';

// const buffer = canvas.toBuffer('image/png');
// fs.writeFileSync(`${imagesDir}frame.png`, buffer);

// // Generate the video using FFmpeg
// execSync(`ffmpeg -loop 1 -i ${imagesDir}frame.png -c:v libx264 -t ${shape_duration} -pix_fmt yuv420p ${outputVideoPath}`);

// // Clean up the temporary image file
// fs.unlinkSync(`${imagesDir}frame.png`);


const { createCanvas } = require('canvas');
const fs = require('fs');
const { execSync } = require('child_process');

// Function to draw text with padding
// function drawText(canvas, text, padding) {
//     const ctx = canvas.getContext('2d');
//     ctx.font = '100px Impact'; // Starting font size
//     let fontSize = parseInt(ctx.font.match(/\d+/), 10);

//     let textWidth;
//     do {
//         // Measure text width with current font size
//         textWidth = ctx.measureText(text).width;
//         if (textWidth + 2 * padding > canvas.width) {
//             // Decrease font size
//             fontSize--;
//             ctx.font = `${fontSize}px Impact`;
//         }
//     } while (textWidth + 2 * padding > canvas.width && fontSize > 10);

//     // Draw the text
//     ctx.fillStyle = '#ffff00'; // Text color
//     ctx.fillText(text, padding, canvas.height / 2 + fontSize / 2, canvas.width - 2 * padding);
// }

function drawText(canvas, text, padding) {
    const ctx = canvas.getContext('2d');
    
    // Set an initial font size
    let fontSize = 100; // Initial guess, you might need to adjust this based on your typical text
    ctx.font = `${fontSize}px Impact`;

    let textWidth, textHeight;
    do {
        // Update font size
        ctx.font = `${fontSize}px Impact`;

        // Measure text
        const textMetrics = ctx.measureText(text);
        textWidth = textMetrics.width;
        textHeight = textMetrics.actualBoundingBoxAscent + textMetrics.actualBoundingBoxDescent;

        // Adjust font size to fit within the canvas, considering padding
        if (textWidth > canvas.width - 2 * padding || textHeight > canvas.height - 2 * padding) {
            fontSize--; // Reduce font size if text is too large
        }
    } while ((textWidth > canvas.width - 2 * padding || textHeight > canvas.height - 2 * padding) && fontSize > 1);

    // Calculate position to center text
    const xPosition = (canvas.width - textWidth) / 2;
    const yPosition = (canvas.height / 2) + (textMetrics.actualBoundingBoxAscent - textMetrics.actualBoundingBoxDescent) / 2;

    // Draw the text
    ctx.fillStyle = '#ffff00'; // Text color
    ctx.fillText(text, xPosition, yPosition);
}

const canvasWidth = 1200;
const canvasHeight = 100*1.5;
const padding = 10; // Padding around text
const canvas = createCanvas(canvasWidth, canvasHeight);
const input_text = "This is a simple string.";
const shape_duration = 10; // Total video duration in seconds

// Video file path and image directory setup
const outputVideoPath = './output_video/output.mp4';
const imagesDir = './images/';

// Delete existing video file
if (fs.existsSync(outputVideoPath)) {
  fs.unlinkSync(outputVideoPath);
}

// Ensure the images directory exists
if (!fs.existsSync(imagesDir)) {
  fs.mkdirSync(imagesDir);
}

// Draw the background and text
const ctx = canvas.getContext('2d');
ctx.fillStyle = '#000000'; // Background color
ctx.fillRect(0, 0, canvasWidth, canvasHeight);
drawText(canvas, input_text, padding);

// Save the canvas as an image
const buffer = canvas.toBuffer('image/png');
fs.writeFileSync(`${imagesDir}frame.png`, buffer);

// Generate the video using FFmpeg
execSync(`ffmpeg -loop 1 -i ${imagesDir}frame.png -c:v libx264 -t ${shape_duration} -pix_fmt yuv420p ${outputVideoPath}`);

// Clean up the temporary image file
fs.unlinkSync(`${imagesDir}frame.png`);

