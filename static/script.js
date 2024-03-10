var uploadedFiles = new Set(); // Stores names of uploaded files to prevent duplicates

function switchForm(formId) {
    var forms = document.querySelectorAll('.form');
    forms.forEach(function (form) {
        form.style.display = 'none';
    });
    document.getElementById(formId).style.display = 'block';
}

function loginUser() {
    var username = document.getElementById("loginUsername").value;
    var password = document.getElementById("loginPassword").value;

    console.log("Attempting to login user:", username); // Debugging line

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Login failed: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Redirect to dashboard page after successful login
            window.location.href = '/dashboard';
        } else {
            alert("Invalid username or password. Please try again.");
        }
    })
    .catch((error) => {
        console.error('Login error:', error);
        alert("An error occurred. Please try again.");
    });

    return false; // Prevent form submission
}

function signupUser() {
    var username = document.getElementById("signupUsername").value;
    var password = document.getElementById("signupPassword").value;

    console.log("Attempting to signup user:", username); // Debugging line

    fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Signup failed: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Instead of redirecting, show a success message
            alert("Signup successful. You can now log in with your new credentials.");
            // Optionally, clear the signup form here to allow for new signups or other actions
            document.getElementById("signupUsername").value = '';
            document.getElementById("signupPassword").value = '';
            // You could also implement logic to switch to the login form here if you have a single-page application
            // switchForm('loginForm'); // Uncomment if you wish to automatically switch to the login form
        } else {
            alert(data.message); // Show the server-provided error message
        }
    })
    .catch((error) => {
        console.error('Signup error:', error);
        alert("An error occurred during signup. Please try again.");
    });

    return false; // Prevent form submission
}

function uploadFile() {
    var fileInput = document.getElementById("fileInput");
    var formData = new FormData();
    formData.append('file', fileInput.files[0]);

    console.log("Uploading file:", fileInput.files[0].name); // Debugging line

    var uploadButton = document.getElementById("uploadButton");
    uploadButton.disabled = true;

    var progressBarContainer = document.getElementById("progressBarContainer");
    progressBarContainer.style.display = "block";

    var progressBar = document.getElementById("progressBar");
    progressBar.style.width = "0%";

    fetch('/upload', {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert("File uploaded successfully");
            displayFileDetails(data.filename);
        } else {
            alert(data.message);
        }
    })
    .catch((error) => {
        console.error('Upload error:', error);
        alert("An error occurred. Please try again.");
    })
    .finally(() => {
        progressBarContainer.style.display = "none";
        uploadButton.disabled = false;
    });

    return false; // Prevent form submission
}

function displayFileDetails(filename) {
    // Selecting the parent div where file details should be appended
    var fileTable = document.querySelector(".file-table");

    // Check if fileTable exists to avoid null reference errors
    if (fileTable) {
        // Creating a new div to represent the file row
        var fileRow = document.createElement("div");
        fileRow.className = "file-row";

        // Populating the fileRow with file details and action buttons
        fileRow.innerHTML = `
            <div class="file-cell">${filename}</div>
            <div class="file-cell">Type</div> <!-- Placeholder for file type, adjust as necessary -->
            <div class="file-cell">Created</div> <!-- Placeholder for created time, adjust as necessary -->
            <div class="file-cell">Modified</div> <!-- Placeholder for modified time, adjust as necessary -->
            <div class="file-cell">
                <button onclick="editFile('${filename}')">Edit</button>
                <button onclick="deleteFile('${filename}')">Delete</button>
            </div>
        `;

        // Appending the new fileRow to the fileTable
        fileTable.appendChild(fileRow);
    } else {
        console.error("File table element not found.");
        alert("File uploaded successfully, but unable to display file details on the page.");
    }
}


function editFile(filename) {
    var newFilename = prompt("Enter a new name for the file:", filename);
    if (newFilename !== null) {
        console.log(`Renaming file: ${filename} to ${newFilename}`); // Debugging line

        fetch('/update_file/' + filename, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ newFilename: newFilename })
        })
        .then(response => {
            if (response.ok) {
                alert("File renamed successfully");
            } else {
                throw new Error('Failed to rename file');
            }
        })
        .catch(error => {
            console.error('Rename error:', error);
            alert("An error occurred while renaming the file. Please try again.");
        });
    }
}

function deleteFile(filename) {
    console.log("Attempting to delete file:", filename); // Debugging line
    // Implement delete functionality here
    alert('Delete file: ' + filename);
}

function logout() {
    console.log("Logging out user"); // Debugging line

    fetch('/logout', {
        method: 'POST',
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/';
        } else {
            throw new Error('Failed to logout');
        }
    })
    .catch(error => {
        console.error('Logout error:', error);
        alert("An error occurred while logging out. Please try again.");
    });
}
