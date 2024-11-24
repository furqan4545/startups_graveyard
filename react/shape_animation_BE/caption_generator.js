const { createCanvas } = require('canvas');
const fs = require('fs');
const { execSync } = require('child_process');

// Load JSON data from file
const jsonData = JSON.parse(fs.readFileSync('voiceover.json', 'utf8'));
const textSegments = jsonData.segments;
console.log('textSegments', textSegments);

const fontSize = 30 * 2; // Adjustable font size
const padding = 6 * 2; // Adjustable padding
const frameRate = 25; // Frames per second

// Prepare a temporary canvas to measure text
const tempCanvas = createCanvas(1000, 500);
const tempCtx = tempCanvas.getContext('2d');
tempCtx.font = `${fontSize}px Arial`;

let frameIndex = 0;  // Index for each individual frame

// Video file path
const outputVideoPath = './output_video/output.mp4';
// Delete the video file if it already exists
if (fs.existsSync(outputVideoPath)) {
  fs.unlinkSync(outputVideoPath);
}

// Ensure the images directory exists
const imagesDir = './images/';
// Ensure the images directory exists
if (!fs.existsSync(imagesDir)) {
  fs.mkdirSync(imagesDir);
} else {
  // If the directory exists, delete any existing frame files
  const files = fs.readdirSync(imagesDir);
  for (const file of files) {
    if (file.startsWith('frame_')) {
      fs.unlinkSync(`${imagesDir}${file}`);
    }
  }
}

// textSegments.forEach(segment => {
//   const segmentDuration = segment.end - segment.start;
//   const animationDuration = segmentDuration * 0.75; // Complete the animation in 75% of the segment duration
//   const segmentFrames = Math.ceil(segmentDuration * frameRate);
// //   console.log('segmentFrames', segmentFrames);
// //   console.log('segment.text', segment.text);
//   const no_words = segment.text.split(' ').length - 1;
//   const segment_words_list = segment.text.split(' ');
// //   console.log('no_words', no_words);
// //   console.log('segment_words_list', segment_words_list);
//   if (no_words > 3) {
//     const first_line = segment_words_list.slice(0, 4).join(' ');  // 0 index is empty string 
//     const second_line = segment_words_list.slice(4, segment_words_list.length).join(' ');
//     // console.log('first line', first_line);
//     // console.log('second line', second_line);

//     segment.words.forEach((word, index) => {
//         console.log(`Word ${index + 1}:`, word);
//     });
//   }
//   const textWidth = tempCtx.measureText(segment.text).width;
//   const textHeight = fontSize;

//   // Adjust canvas width based on text width
//   const minCanvasWidth = 900; // Set a minimum canvas width
//   const canvasWidth = Math.max(Math.ceil((textWidth + padding * 2) / 2) * 2, minCanvasWidth);
//   const canvasHeight = Math.ceil((textHeight + padding * 2) / 2) * 2;
//   const canvas = createCanvas(canvasWidth, canvasHeight);
//   const ctx = canvas.getContext('2d');

//   for (let frame = 0; frame < segmentFrames; frame++) {
//     const progress = Math.min(1, frame / (animationDuration * frameRate));
//     // const progress = frame / segmentFrames;
//     const currentTextLength = Math.floor(progress * segment.text.length);
//     const currentText = segment.text.substring(0, currentTextLength);

//     ctx.clearRect(0, 0, canvas.width, canvas.height);
//     ctx.fillStyle = 'white';
//     ctx.font = `${fontSize}px Arial`;
//     ctx.textBaseline = 'middle';

//     // Adjust text position based on its width
//     const textXPosition = (canvasWidth - textWidth) / 2;
//     ctx.fillText(currentText, textXPosition, canvasHeight / 2);

//     const buffer = canvas.toBuffer('image/png');
//     fs.writeFileSync(`${imagesDir}frame_${frameIndex.toString().padStart(4, '0')}.png`, buffer);
//     frameIndex++;
//   }
// });



// const lineGap = -16;
// textSegments.forEach(segment => {
//   const segmentDuration = segment.end - segment.start;
//   const animationDuration = segmentDuration * 0.75; // Complete the animation in 75% of the segment duration
//   const segmentFrames = Math.ceil(segmentDuration * frameRate);

//   const words = segment.text.split(' ');
//   const no_words = words.length;
//   let firstLine = segment.text;
//   let secondLine = '';
//   let isDoubleLine = false;

//   if (no_words > 3) {
//     firstLine = words.slice(0, 3).join(' ');
//     secondLine = words.slice(3).join(' ');
//     isDoubleLine = true;
//   }

//   const minCanvasWidth = 900;
//   const canvasWidth = Math.max(minCanvasWidth, tempCtx.measureText(segment.text).width + padding * 2);
//   const lineTextHeight = isDoubleLine ? fontSize / 1.5 : fontSize; // Adjust text height for two lines
//   const canvasHeight = fontSize * 2 + padding * 2 + (isDoubleLine ? lineGap : 0); // Adjust height for gap
//   const canvas = createCanvas(canvasWidth, canvasHeight);
//   const ctx = canvas.getContext('2d');

//   for (let frame = 0; frame < segmentFrames; frame++) {
//     const progress = Math.min(1, frame / (animationDuration * frameRate));
//     const totalLength = firstLine.length + (isDoubleLine ? secondLine.length : 0);
//     let currentTextLength = Math.floor(progress * totalLength);

//     let currentTextFirstLine = firstLine;
//     let currentTextSecondLine = '';

//     if (currentTextLength <= firstLine.length) {
//       currentTextFirstLine = firstLine.substring(0, currentTextLength);
//     } else if (isDoubleLine) {
//       currentTextSecondLine = secondLine.substring(0, currentTextLength - firstLine.length);
//     }

//     ctx.clearRect(0, 0, canvas.width, canvas.height);
//     ctx.fillStyle = 'white';
//     ctx.font = `${lineTextHeight}px Arial`;
//     ctx.textBaseline = 'middle';

//     const textXPosition = padding;
//     const firstLineYPosition = isDoubleLine ? canvasHeight / 4 - lineGap / 2 : canvasHeight / 2;
//     const secondLineYPosition = isDoubleLine ? 3 * canvasHeight / 4 + lineGap / 2 : canvasHeight / 2;
//     // ctx.fillText(currentTextFirstLine, textXPosition, isDoubleLine ? canvasHeight / 4 : canvasHeight / 2);
//     ctx.fillText(currentTextFirstLine, textXPosition, firstLineYPosition);


//     if (isDoubleLine) {
//     //   ctx.fillText(currentTextSecondLine, textXPosition, 3 * canvasHeight / 4);
//         ctx.fillText(currentTextSecondLine, textXPosition, secondLineYPosition);
//     }

//     const buffer = canvas.toBuffer('image/png');
//     fs.writeFileSync(`${imagesDir}frame_${frameIndex.toString().padStart(4, '0')}.png`, buffer);
//     frameIndex++;
//   }
// });



const lineGap = -18;
textSegments.forEach(segment => {
  const segmentDuration = segment.end - segment.start;
  const animationDuration = segmentDuration * 0.75; // Complete the animation in 75% of the segment duration
  const segmentFrames = Math.ceil(segmentDuration * frameRate);

  const words = segment.text.split(' ');
  const no_words = words.length;
  let firstLine = segment.text;
  let secondLine = '';
  let isDoubleLine = false;

  if (no_words > 5) {
    firstLine = words.slice(0, 4).join(' ');
    secondLine = words.slice(3).join(' ');
    isDoubleLine = true;
  }

  const minCanvasWidth = 900;
  const canvasWidth = Math.max(minCanvasWidth, tempCtx.measureText(segment.text).width + padding * 2);
  const lineTextHeight = isDoubleLine ? fontSize / 1.5 : fontSize; // Adjust text height for two lines
  const canvasHeight = fontSize * 2 + padding * 2 + (isDoubleLine ? lineGap : 0); // Adjust height for gap
  const canvas = createCanvas(canvasWidth, canvasHeight);
  const ctx = canvas.getContext('2d');

  for (let frame = 0; frame < segmentFrames; frame++) {
    const progress = Math.min(1, frame / (animationDuration * frameRate));
    const totalLength = firstLine.length + (isDoubleLine ? secondLine.length : 0);
    let currentTextLength = Math.floor(progress * totalLength);

    let currentTextFirstLine = firstLine;
    let currentTextSecondLine = '';

    if (currentTextLength <= firstLine.length) {
      currentTextFirstLine = firstLine.substring(0, currentTextLength);
    } else if (isDoubleLine) {
      currentTextSecondLine = secondLine.substring(0, currentTextLength - firstLine.length);
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'white';
    ctx.font = `${lineTextHeight}px Arial`;
    ctx.textBaseline = 'middle';

    const textXPosition = padding;
    const firstLineYPosition = isDoubleLine ? canvasHeight / 4 - lineGap / 2 : canvasHeight / 2;
    const secondLineYPosition = isDoubleLine ? 3 * canvasHeight / 4 + lineGap / 2 : canvasHeight / 2;
    // ctx.fillText(currentTextFirstLine, textXPosition, isDoubleLine ? canvasHeight / 4 : canvasHeight / 2);
    ctx.fillText(currentTextFirstLine, textXPosition, firstLineYPosition);


    if (isDoubleLine) {
        ctx.fillText(" " + currentTextSecondLine, textXPosition, secondLineYPosition); // add space before second line
    }

    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync(`${imagesDir}frame_${frameIndex.toString().padStart(4, '0')}.png`, buffer);
    frameIndex++;
  }
});



execSync(`ffmpeg -framerate ${frameRate} -i ${imagesDir}frame_%04d.png -c:v libx264 -pix_fmt yuv420p ${outputVideoPath}`);

for (let frame = 0; frame < frameIndex; frame++) {
  fs.unlinkSync(`${imagesDir}frame_${frame.toString().padStart(4, '0')}.png`);
}




// process.on('message', (message) => {
//     const { canvasWidth, canvasHeight, videoDuration, xPos, yPos, preset } = message;
//     const frameRate = 30; // Frames per second
//     const totalFrames = frameRate * videoDuration; // Total frames for the video
//     try {
//         const canvas = createCanvas(canvasWidth, canvasHeight);
//         const ctx = canvas.getContext('2d');

//         deletePreviousOutput();
//         cleanupExistingFrames();
//         renderFrames(ctx, canvas, canvasWidth, canvasHeight, totalFrames, frameRate, preset);
//         compileVideo(totalFrames, frameRate);

//         process.send({ status: 'completed' });
//         process.kill(process.pid);
//         process.exit(0);
//     } catch (err) {
//         console.error('Error creating canvas:', err.message);
//         process.send({ status: 'error', error: err.message });
//         process.kill(process.pid);
//         process.exit(1);
//     }
// });
