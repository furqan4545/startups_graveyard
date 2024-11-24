// const { execSync } = require('child_process');
// const fs = require('fs');
// const path = require('path');

// function createVideoWithImages(shapes, inputVideoPath, outputVideoPath) {
//     // Temp directory for intermediate files
//     const tempDir = path.join(__dirname, 'temp');
//     if (!fs.existsSync(tempDir)) {
//         fs.mkdirSync(tempDir);
//     }

//     let currentVideoPath = inputVideoPath;
//     shapes.forEach((shape, index) => {
//         // Decode the base64 image blob to a file
//         const imageData = shape.imgBlob.split(',')[1];
//         const imageBuffer = Buffer.from(imageData, 'base64');
//         const imagePath = path.join(tempDir, `image_${shape.id}.png`);
//         fs.writeFileSync(imagePath, imageBuffer);

//         // Calculate duration
//         const duration = shape.end - shape.start;

//         // Prepare the ffmpeg command
//         const filter = `overlay=${shape.x}:${shape.y}:enable='between(t,${shape.start},${shape.end})'`;
//         const intermediateOutput = path.join(tempDir, `output_${index}.mp4`);
//         const command = `ffmpeg -i ${currentVideoPath} -i ${imagePath} -filter_complex "${filter}" -pix_fmt yuv420p -c:a copy ${intermediateOutput}`;

//         // Execute the ffmpeg command
//         execSync(command);

//         // Update the current video path for the next iteration
//         currentVideoPath = intermediateOutput;
//     });

//     // Move the final video to the desired output path
//     fs.renameSync(currentVideoPath, outputVideoPath);

//     // Clean up temp directory
//     fs.rmdirSync(tempDir, { recursive: true });
// }

// // Example usage
/*// const shapes = [
    // { id: 1, start: 10, end: 15, text: 'Surprise Surprise', x: 10, y: 70, width: 100, height: 100, fill: 'white', imgBlob: "data:image/png;base64,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" },
//     { id: 2, start: 16, end: 22, text: 'Hello Kalia', x: 100, y: 70, width: 100, height: 100, fill: 'white', imgBlob: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABpCAYAAADMfIaKAAAAAXNSR0IArs4c6QAABNhJREFUeF7tnG9I1GcAx7+6iqYbM7SZQ9xVUF4YLW3khisX+CJmTKRYAy1OQdM3WxZEvekP2ZuYmujCC0QY0WCScyLUoSEcNWmJVx2jjc3MP2uNGVPBMv/c+D3jDq+uXY51fdm+vzfHcc/9ns/v+7nv8zyvLgq6qBKIoqIRDCSE7EcgIRJClgAZTpTP5/ORMf2vcSSETL+ESAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4EW2IDz5EvYB/83hR8/4T1xET0tHXgeJvinHn0zsBzl0tu2CLs+HY+8dCsld3V+PmvZtYm7jWvDZ+2Bj2GYtai5D0ahIqt1Sasdb7Cz9dQO+eXiTGJj7xff8cGW9k4MrgFZzNPxt2juc5gFpI1bdV8P7mRdrraeZ1PkKObzkOx9cOdN7uxLWSayFlWMH656jdWouH0w+REJPwPPMOe++IC+n7pC8AtbtlN1YsWWEaUne1DvXf1WN6dhqlGaXY/+7+QFhzhVS6K+HscWLRS4vgeMuBQ+8dCnpIqxHLXlmG4fFhdPV3GRlLY5bCWrZ2Nu9E91A37j+4j8zkTFwsuIia7hoje7NtM3p+6cGpradCjouOig4b5r8xIKJCcr7IQfzL8QHu0clRHMw6iPK3y5Fal4qhiiHzmb3ejstFl9H8fXNQQyreqUBWYxYGKwbNXmSrscFd5IY9wR64pyXknPeceb86frURsiB6Afr/6McJ9wk0bGvAyMQIkj5Lgrfci/Yf280c/iXLWupCjbPuFYkrokKetoekvJaCsvayQLCzvlkcyT6CgdGBICGpCalwD7jR9nGbyWbHVzuQnpRupPovS8it32/BVehChjMD2bZsNOQ2YGxyDIUthfD86jGNuX7vOnpLe+H62RUk5PQHp0OOs1oaiYtCSHF6MdI+T8PdfXcRszAGjlYH9mbuxaXbl4KEWMvTBucGDO8bNg1JqU5BU14TclflBgnxb+qW0JW1K+Hc5sSjmUeov1qPG2U3zHKWXJUMzx4POvs6g4RsenNTyHHrEtdFwgciKqSkrQRz9xDrlLV8yXIczT6Kw12HcabnjHnojckbcf6j82Z9f/yUdaDjAJo8TZiYmkC+Pd8ImXuUfvyU1fpDK/K+zIOrwIWClgLELY4zc4xPjsPayAfHBs0c/iXrZM5JrG9Y/8S47Wu2/7eEPMvTzPhmzEkndmHs3w6fmp3C1MyUadN8r5EHI0H72NO+/6zj5jt/uPERa0g4EH3+VwISQvZLkBAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAyIX8C36M/B7c2nMoAAAAASUVORK5CYII=" },
//     // { id: 3, start: 30, end: 40, text: 'Donkey', x: 100, y: 70, width: 100, height: 100, fill: 'red' },
// ]; */


// createVideoWithImages(shapes, './input_video/tate.mp4', './output_video/output.mp4');


const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function createVideoWithImages(shapes, inputVideoPath, outputVideoPath) {
    
    // Check if output file already exists and delete it
    if (fs.existsSync(outputVideoPath)) {
        fs.unlinkSync(outputVideoPath);
    }
    // Temp directory for intermediate files
    const tempDir = path.join(__dirname, 'temp');
    if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir);
    }

    let currentVideoPath = inputVideoPath;
    shapes.forEach((shape, index) => {
        // Decode the base64 image blob to a file
        const imageData = shape.imgBlob.split(',')[1];
        const imageBuffer = Buffer.from(imageData, 'base64');
        const imagePath = path.join(tempDir, `image_${shape.id}.png`);
        fs.writeFileSync(imagePath, imageBuffer);

        // Calculate duration
        const duration = shape.end - shape.start;

        // Prepare the ffmpeg command
        const filter = `overlay=${shape.x}:${shape.y}:enable='between(t,${shape.start},${shape.end})'`;
        const intermediateOutput = path.join(tempDir, `output_${index}.mp4`);
        const command = `ffmpeg -i ${currentVideoPath} -i ${imagePath} -filter_complex "${filter}" -pix_fmt yuv420p -c:a copy ${intermediateOutput}`;

        // Execute the ffmpeg command
        execSync(command);

        // Update the current video path for the next iteration
        currentVideoPath = intermediateOutput;
    });

    // Move the final video to the desired output path
    fs.renameSync(currentVideoPath, outputVideoPath);

    // Clean up temp directory
    fs.rmdirSync(tempDir, { recursive: true });
}


process.on('message', (message) => {
    // Assuming message contains shapes, inputVideoPath, and outputVideoPath
    const { shapes, inputVideoPath, outputVideoPath } = message;

    try {
        createVideoWithImages(shapes, inputVideoPath, outputVideoPath);
        process.send({ success: true, message: 'Video rendered successfully' });
    } catch (error) {
        process.send({ success: false, message: 'Error in rendering video', error: error.message });
    }
});


/*[
    { id: 1, start: 10, end: 15, text: 'Surprise Surprise', x: 10, y: 70, width: 100, height: 100, fill: 'white', imgBlob: "data:image/png;base64,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" },
    { id: 2, start: 16, end: 22, text: 'Hello Kalia', x: 100, y: 70, width: 100, height: 100, fill: 'white', imgBlob: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABpCAYAAADMfIaKAAAAAXNSR0IArs4c6QAABNhJREFUeF7tnG9I1GcAx7+6iqYbM7SZQ9xVUF4YLW3khisX+CJmTKRYAy1OQdM3WxZEvekP2ZuYmujCC0QY0WCScyLUoSEcNWmJVx2jjc3MP2uNGVPBMv/c+D3jDq+uXY51fdm+vzfHcc/9ns/v+7nv8zyvLgq6qBKIoqIRDCSE7EcgIRJClgAZTpTP5/ORMf2vcSSETL+ESAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4aoiEkCVAhqOGSAhZAmQ4EW2IDz5EvYB/83hR8/4T1xET0tHXgeJvinHn0zsBzl0tu2CLs+HY+8dCsld3V+PmvZtYm7jWvDZ+2Bj2GYtai5D0ahIqt1Sasdb7Cz9dQO+eXiTGJj7xff8cGW9k4MrgFZzNPxt2juc5gFpI1bdV8P7mRdrraeZ1PkKObzkOx9cOdN7uxLWSayFlWMH656jdWouH0w+REJPwPPMOe++IC+n7pC8AtbtlN1YsWWEaUne1DvXf1WN6dhqlGaXY/+7+QFhzhVS6K+HscWLRS4vgeMuBQ+8dCnpIqxHLXlmG4fFhdPV3GRlLY5bCWrZ2Nu9E91A37j+4j8zkTFwsuIia7hoje7NtM3p+6cGpradCjouOig4b5r8xIKJCcr7IQfzL8QHu0clRHMw6iPK3y5Fal4qhiiHzmb3ejstFl9H8fXNQQyreqUBWYxYGKwbNXmSrscFd5IY9wR64pyXknPeceb86frURsiB6Afr/6McJ9wk0bGvAyMQIkj5Lgrfci/Yf280c/iXLWupCjbPuFYkrokKetoekvJaCsvayQLCzvlkcyT6CgdGBICGpCalwD7jR9nGbyWbHVzuQnpRupPovS8it32/BVehChjMD2bZsNOQ2YGxyDIUthfD86jGNuX7vOnpLe+H62RUk5PQHp0OOs1oaiYtCSHF6MdI+T8PdfXcRszAGjlYH9mbuxaXbl4KEWMvTBucGDO8bNg1JqU5BU14TclflBgnxb+qW0JW1K+Hc5sSjmUeov1qPG2U3zHKWXJUMzx4POvs6g4RsenNTyHHrEtdFwgciKqSkrQRz9xDrlLV8yXIczT6Kw12HcabnjHnojckbcf6j82Z9f/yUdaDjAJo8TZiYmkC+Pd8ImXuUfvyU1fpDK/K+zIOrwIWClgLELY4zc4xPjsPayAfHBs0c/iXrZM5JrG9Y/8S47Wu2/7eEPMvTzPhmzEkndmHs3w6fmp3C1MyUadN8r5EHI0H72NO+/6zj5jt/uPERa0g4EH3+VwISQvZLkBAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAJIUuADEcNkRCyBMhw1BAyIX8C36M/B7c2nMoAAAAASUVORK5CYII=" },
]; */
