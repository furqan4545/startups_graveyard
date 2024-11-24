
// const fs = require('fs');
// const express = require('express');
// const bodyParser = require('body-parser');
// const { fork } = require('child_process');
// const multer = require('multer');
// const { parse } = require('path');

// const app = express();
// const port = 3200;

// const upload = multer();   

// // For JSON data
// app.use(bodyParser.json());
// app.use(bodyParser.urlencoded({ extended: true }));

// app.post('/render_shapes_video', upload.none(), (req, res) => {
//     let { canvasWidth, canvasHeight, videoDuration, xPos, yPos, preset } = req.body;
//     canvasWidth = parseInt(canvasWidth, 10);
//     canvasHeight = parseInt(canvasHeight, 10);
//     videoDuration = parseFloat(videoDuration);
//     xPos = parseInt(xPos, 10);
//     xPos = parseInt(yPos, 10);
//     preset = parseInt(preset, 10);
//     console.log('Received request:', req.body);

//     // Validate input parameters
//     if (!canvasWidth || !canvasHeight || !videoDuration || xPos === undefined || yPos === undefined) {
//         return res.status(400).send('Missing parameters');
//     }

//     // Spawn a child process for video generation
//     const child = fork('./caption_generator.js');

//     // Send parameters to the child process
//     child.send({ canvasWidth, canvasHeight, videoDuration, xPos, yPos });

//     // Listen for messages from the child process
//     child.on('message', (message) => {
//         console.log('Message from child:', message);
//     });

//     child.on('exit', (code) => {
//         console.log(`Child process exited with code ${code}`);
//     });

//     res.status(200).send('Video generation started');
// });

// app.listen(port, () => {
//     console.log(`Server running on port ${port}`);
// });



const fs = require('fs');
const express = require('express');
const bodyParser = require('body-parser');
const { fork } = require('child_process');
const multer = require('multer');
const { parse } = require('path');

const app = express();
const port = 3200;
const upload = multer();   

// For JSON data
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.post('/render_shapes_video', upload.none(), (req, res) => {
    const { shapes, inputVideoPath, outputVideoPath } = req.body;

    console.log('Received request:', shapes);
    // Validate input parameters
    if (!shapes || !inputVideoPath || !outputVideoPath) {
        return res.status(400).send('Missing parameters');
    }

    // Convert shapes string to object
    let parsedShapes;
    try {
        parsedShapes = JSON.parse(shapes);
    } catch (error) {
        return res.status(400).send('Invalid shapes format');
    }

    // Spawn a child process for video generation
    const child = fork('./render_shapes.js');

    // Send parameters to the child process
    child.send({ shapes: parsedShapes, inputVideoPath, outputVideoPath });

    // Listen for messages from the child process
    child.on('message', (message) => {
        console.log('Message from child:', message);
    });

    child.on('exit', (code) => {
        console.log(`Child process exited with code ${code}`);
    });

    res.status(200).send('Video generation started');
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});


