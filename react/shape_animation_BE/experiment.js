// const jsdom = require("jsdom");
// const htmlToImage = require('html-to-image');
// const fs = require('fs');
// const { execSync } = require('child_process');

// const { JSDOM } = jsdom;

// // Your HTML
// const html = `
// <html>
//   <body>
//     <h1 class="ml6">
//       <span class="text-wrapper">
//         <span class="letters">Beautiful Questions</span>
//       </span>
//     </h1>
//   </body>
// </html>
// `;

// // Your CSS
// const css = `
// .ml6 {
//   position: relative;
//   font-weight: 900;
//   font-size: 3.3em;
// }
// .ml6 .text-wrapper {
//   position: relative;
//   display: inline-block;
//   padding-top: 0.2em;
//   padding-right: 0.05em;
//   padding-bottom: 0.1em;
//   overflow: hidden;
// }
// .ml6 .letter {
//   display: inline-block;
//   line-height: 1em;
// }
// `;

// // Create the DOM
// const dom = new JSDOM(html, { runScripts: "outside-only" });

// // Apply the CSS (this won't render it but adds it to the DOM)
// const styleEl = dom.window.document.createElement("style");
// styleEl.textContent = css;
// dom.window.document.head.appendChild(styleEl);

// // Load and run the anime.js script
// const scriptEl = dom.window.document.createElement("script");
// scriptEl.src = "https://cdnjs.cloudflare.com/ajax/libs/animejs/2.0.2/anime.min.js";
// dom.window.document.head.appendChild(scriptEl);

// // Your JavaScript
// scriptEl.onload = () => {
//   // Anime.js is now loaded and can be used
//   const anime = dom.window.anime;

//   // Your animation logic here
//   var textWrapper = dom.window.document.querySelector('.ml6 .letters');
//   textWrapper.innerHTML = textWrapper.textContent.replace(/\S/g, "<span class='letter'>$&</span>");

//   anime.timeline({ loop: true })
//     .add({
//       targets: '.ml6 .letter',
//       translateY: ["1.1em", 0],
//       translateZ: 0,
//       duration: 750,
//       delay: (el, i) => 50 * i
//     }).add({
//       targets: '.ml6',
//       opacity: 0,
//       duration: 1000,
//       easing: "easeOutExpo",
//       delay: 1000
//     });
// };

// ///////////////////////////////

// // Assuming `dom` is your JSDOM object from the previous setup
// const mainDiv = dom.window.document.querySelector('.ml6');
// const fps = 30;

// async function captureFrame() {
//     const dataUrl = await htmlToImage.toPng(mainDiv);
//     // Convert DataURL to Buffer
//     const buffer = Buffer.from(dataUrl.split(",")[1], 'base64');
//     return buffer;
// }

// async function createFrames() {
//     for (let i = 0; i < 60 * fps; i++) { // fps is the frames per second you want
//         const frame = await captureFrame();
//         fs.writeFileSync(`./images/frame_${i}.png`, frame);
//         // You need to wait here for the next frame of the animation
//     }
// }

// function compileVideo() {
//     const command = ffmpeg();

//     for (let i = 0; i < 60 * fps; i++) {
//         command.input(`./images/frame_${i}.png`);
//     }

//     command.on('end', function() {
//         console.log('Video created');
//     })
//     .on('error', function(err) {
//         console.error('Error:', err);
//     })
//     .save('./output_video/output.mp4');
// }

// async function createAnimationVideo() {
//     await createFrames();
//     compileVideo();
// }

// createAnimationVideo();


////////////////////////////////////////

const { JSDOM } = require("jsdom");
const { createCanvas, Image } = require('canvas');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// HTML content
const html = `
<html>
  <body>
    <h1 class="ml6">
      <span class="text-wrapper">
        <span class="letters">Beautiful Questions</span>
      </span>
    </h1>
  </body>
</html>
`;

// CSS
const css = `
.ml6 {
  position: relative;
  font-weight: 900;
  font-size: 3.3em;
}
.ml6 .text-wrapper {
  position: relative;
  display: inline-block;
  padding-top: 0.2em;
  padding-right: 0.05em;
  padding-bottom: 0.1em;
  overflow: hidden;
}
.ml6 .letter {
  display: inline-block;
  line-height: 1em;
}
`;

// JSDOM setup
const dom = new JSDOM(html);
const document = dom.window.document;
const styleEl = document.createElement("style");
styleEl.textContent = css;
document.head.appendChild(styleEl);

// Create Canvas and Context
const width = 800;  // Set your desired width
const height = 600; // Set your desired height
const canvas = createCanvas(width, height);
const ctx = canvas.getContext('2d');

// Render HTML/CSS to Canvas
function renderToCanvas() {
    // Render your HTML/CSS here. This is a simplified example.
    // You might need to use node-canvas methods to replicate your HTML/CSS design.
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = 'black';
    ctx.font = '48px serif';
    ctx.fillText('Beautiful Questions', 50, 300);
}

// Save frames
function saveFrame(frameNumber) {
    renderToCanvas(); // Call render function
    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync(`./images/frame_${frameNumber}.png`, buffer);
}

// Create frames and compile video
async function createAnimationVideo() {
    const fps = 30; // Frames per second
    const duration = 10; // Duration in seconds

    for (let i = 0; i < duration * fps; i++) {
        saveFrame(i);
    }

    // Compile frames into a video using ffmpeg
    execSync(`ffmpeg -r ${fps} -i ./images/frame_%d.png -c:v libx264 -vf fps=${fps} -pix_fmt yuv420p ./output_video/output.mp4`);
    console.log('Video created');
}

createAnimationVideo();




