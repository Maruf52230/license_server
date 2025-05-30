async function createLicense() {
    const expiresIn = document.getElementById('expiresIn').value;
    const createResult = document.getElementById('createResult');
    createResult.textContent = "Creating...";
    createResult.style.color = "#333";
    let payload = {};
    if (expiresIn) {
        payload.expires_in_days = parseInt(expiresIn);
    }
    try {
        const response = await fetch('http://127.0.0.1:5000/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (response.ok) {
            createResult.textContent = `✅ License created: ${data.license_key} (Expires: ${data.expiresAt})`;
            createResult.style.color = "green";
        } else {
            createResult.textContent = `❌ ${data.error || 'Error creating license.'}`;
            createResult.style.color = "red";
        }
    } catch (err) {
        createResult.textContent = "Error connecting to server.";
        createResult.style.color = "red";
    }
}

async function checkLicense() {
    const key = document.getElementById('licenseKeyCheck').value.trim();
    const resultDiv = document.getElementById('checkResult');
    resultDiv.textContent = "Checking...";
    resultDiv.style.color = "#333";
    if (!key) {
        resultDiv.textContent = "Please enter a license key.";
        resultDiv.style.color = "red";
        return;
    }
    try {
        const response = await fetch(`http://127.0.0.1:5000/check/${key}`);
        const data = await response.json();
        if (response.ok) {
            resultDiv.textContent = `✅ ${data.message} (Expires: ${data.expiresAt})`;
            resultDiv.style.color = "green";
        } else {
            resultDiv.textContent = `❌ ${data.message || data.error}`;
            resultDiv.style.color = "red";
        }
    } catch (err) {
        resultDiv.textContent = "Error connecting to server.";
        resultDiv.style.color = "red";
    }
}

async function deleteLicense() {
    const key = document.getElementById('licenseKeyDelete').value.trim();
    const deleteResult = document.getElementById('deleteResult');
    deleteResult.textContent = "Deleting...";
    deleteResult.style.color = "#333";
    if (!key) {
        deleteResult.textContent = "Please enter a license key.";
        deleteResult.style.color = "red";
        return;
    }
    try {
        const response = await fetch(`http://127.0.0.1:5000/delete/${key}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        if (response.ok) {
            deleteResult.textContent = `✅ ${data.message}`;
            deleteResult.style.color = "green";
        } else {
            deleteResult.textContent = `❌ ${data.error || 'Error deleting license.'}`;
            deleteResult.style.color = "red";
        }
    } catch (err) {
        deleteResult.textContent = "Error connecting to server.";
        deleteResult.style.color = "red";
    }
}