const fs = require('fs');
const content = fs.readFileSync('deploy_output.txt', 'utf8');
const match = content.match(/C[A-Z0-9]{55}/);
if (match) {
    console.log(match[0]);
} else {
    console.log("No ID found");
}
