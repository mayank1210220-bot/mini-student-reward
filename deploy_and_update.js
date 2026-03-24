const { execSync } = require('child_process');
const fs = require('fs');

try {
    console.log("Running deployment...");
    const output = execSync(`powershell -ExecutionPolicy Bypass -File deploy_cli.ps1`, { encoding: 'utf8' });
    console.log("Output received");
    const match = output.match(/C[A-Z0-9]{55}/);
    if (match) {
        const id = match[0];
        console.log("FOUND_ID:" + id);
        
        // Update app.js
        let appJs = fs.readFileSync('frontend/app.js', 'utf8');
        appJs = appJs.replace(/const CONTRACT_ID = ".*";/, `const CONTRACT_ID = "${id}";`);
        fs.writeFileSync('frontend/app.js', appJs);
        console.log("UPDATED_APP_JS");
    } else {
        console.log("ID_NOT_FOUND");
        console.log(output);
    }
} catch (e) {
    console.error("EXEC_ERROR");
    console.error(e.stdout || e.message);
}
