const { createCanvas } = require('canvas');
const fs = require('fs');
const { execSync, fork } = require('child_process');
const express = require('express');
const bodyParser = require('body-parser');

// Load JSON data from file
const jsonData = JSON.parse(fs.readFileSync('voiceover.json', 'utf8'));
const textSegments = jsonData.segments;

const canvasWidth = 1000; // Target video resolution width
const canvasHeight = 500; // Target video resolution height
const frameRate = 30; // Frames per second
const videoDuration = 35; // Total video duration in seconds
const totalFrames = frameRate * videoDuration; // Total frames for the video

const canvas = createCanvas(canvasWidth, canvasHeight);
const ctx = canvas.getContext('2d');

function presetSlide(frame) {
    const currentTime = frame / frameRate;
    const animationDuration = 1; // Duration for the text to animate completely in seconds
    
    for (const segment of textSegments) {
      if (currentTime >= segment.start && currentTime < segment.start + animationDuration) {
        const progress = (currentTime - segment.start) / animationDuration;
        const currentTextLength = Math.floor(progress * segment.text.length);
        return segment.text.substr(0, currentTextLength);
      } else if (currentTime >= segment.start + animationDuration && currentTime <= segment.end) {
        // Keep the text fully displayed after the animation duration until the end of the segment
        return segment.text;
      }
    }
    return ''; // Return empty string if no text should be displayed
  }

  function cleanupExistingFrames() {
    const frameRegex = /^frame_\d{4}.png$/; // Regex to match frame filenames
    fs.readdirSync('.').forEach(file => {
        if (frameRegex.test(file)) {
            fs.unlinkSync(file);
        }
    });
}


  function presetOneWord(frame) {
    const currentTime = frame / frameRate;
    let currentText = '';
    let fontSizeModifier = 1; // Normal font size
  
    for (const segment of textSegments) {
      if (currentTime >= segment.start && currentTime <= segment.end) {
        for (const wordInfo of segment.words) {
          if (currentTime >= wordInfo.start && currentTime < wordInfo.end) {
            // Create a pop effect by temporarily increasing the font size
            const popDuration = 0.1; // Duration of the pop effect in seconds
            const timeSinceWordStart = currentTime - wordInfo.start;
            if (timeSinceWordStart <= popDuration) {
              // Increase font size for a brief moment
              fontSizeModifier = 1.5; // Increase to 150% of original size
            } else {
              // After pop effect, return to normal size
              fontSizeModifier = 1;
            }
            currentText += wordInfo.word;
          }
        }
        break; // Break after finding the right segment
      }
    }
  
    return { text: currentText, fontSizeModifier };
  }

  function presetSlideWord(frame) {
    const currentTime = frame / frameRate;
    let currentText = '';
  
    for (const segment of textSegments) {
      if (currentTime >= segment.start && currentTime <= segment.end) {
        for (const wordInfo of segment.words) {
          if (currentTime >= wordInfo.start) {
            const wordDuration = wordInfo.end - wordInfo.start;
            const wordProgress = Math.min((currentTime - wordInfo.start) / wordDuration, 1);
            const currentWordLength = Math.floor(wordProgress * wordInfo.word.length);
            currentText += wordInfo.word.substr(0, currentWordLength);
          }
        }
        break; // Break after processing the current segment
      }
    }
  
    return currentText;
  }
  
// function renderFrames() {
//   for (let frame = 0; frame < totalFrames; frame++) {
//     const currentText = presetSlide(frame);

//     ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
//     if (currentText) {
//       const fontSize = 30 * 2; // Adjustable font size
//       ctx.fillStyle = 'white'; // Text color
//       ctx.font = `${fontSize}px Arial`;
//       ctx.textBaseline = 'middle'; // Align text vertically in the middle
//       ctx.textAlign = 'center'; // Align text horizontally in the center
//       ctx.fillText(currentText, canvasWidth / 2, canvasHeight / 2); // Draw the text centered
//     }

//     const buffer = canvas.toBuffer('image/png');
//     fs.writeFileSync(`./frame_${frame.toString().padStart(4, '0')}.png`, buffer);
//   }
// }

function renderFrames() {
//     for (let frame = 0; frame < totalFrames; frame++) {
//       const currentText = presetSlide(frame); // Use the new word-based function
  
//       ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
//       if (currentText) {
//         const fontSize = 30 * 2; // Adjustable font size
//         ctx.fillStyle = 'white'; // Text color
//         ctx.font = `${fontSize}px Arial`;
//         ctx.textBaseline = 'middle'; // Align text vertically in the middle
//         ctx.textAlign = 'center'; // Align text horizontally in the center
//         ctx.fillText(currentText, canvasWidth / 2, canvasHeight / 2); // Draw the text centered
//       }
  
//       const buffer = canvas.toBuffer('image/png');
//       fs.writeFileSync(`./frame_${frame.toString().padStart(4, '0')}.png`, buffer);
//     }
// Inside your render loop
    for (let frame = 0; frame < totalFrames; frame++) {
        const { text: currentText, fontSizeModifier } = presetOneWord(frame);
        
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
        if (currentText) {
        const baseFontSize = 30 * 2; // Base font size
        ctx.fillStyle = 'white'; // Text color
        ctx.font = `${baseFontSize * fontSizeModifier}px Arial`;
        ctx.textBaseline = 'middle'; // Align text vertically in the middle
        ctx.textAlign = 'center'; // Align text horizontally in the center
        ctx.fillText(currentText, canvasWidth / 2, canvasHeight / 2); // Draw the text centered
        }
    
        const buffer = canvas.toBuffer('image/png');
        fs.writeFileSync(`./images/frame_${frame.toString().padStart(4, '0')}.png`, buffer);
    }
}

function deletePreviousOutput() {
    if (fs.existsSync('./images/output.mp4')) {
        fs.unlinkSync('./images/output.mp4');
    }
}

  
function compileVideo() {
    // Compile the frames into a video
    execSync(`ffmpeg -framerate 30 -i ./images/frame_%04d.png -c:v libx264 -pix_fmt yuv420p -y ./images/output.mp4`);

    // Clean up the frame images
    for (let frame = 0; frame < totalFrames; frame++) {
        try {
            fs.unlinkSync(`./images/frame_${frame.toString().padStart(4, '0')}.png`);
        } catch (err) {
            console.error(`Error deleting frame ${frame}:`, err.message);
        }
    }
}

// Run the cleanup before rendering new frames
deletePreviousOutput();
cleanupExistingFrames();
renderFrames();
compileVideo();

