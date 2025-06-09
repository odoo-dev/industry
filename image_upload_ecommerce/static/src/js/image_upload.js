document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('custom_image');
    const fileName = document.getElementById('fileName');
    const maxSizeMB = 2;

    if (fileInput && fileName) {
        fileInput.addEventListener('change', function () {
            if (!fileInput.files.length) {
                return;
            }
            const file = fileInput.files[0];
            if (file) {
                if (!file.type.startsWith('image/')) {
                    showFrontendError("Only image files are allowed.");
                    fileInput.value = '';
                    fileName.value = '';
                    return;
                }

                const fileSizeMB = file.size / (1024 * 1024);
                if (fileSizeMB > maxSizeMB) {
                    showFrontendError(`File size exceeds ${maxSizeMB}MB. Please choose a smaller image.`);
                    fileInput.value = '';
                    fileName.value = '';
                    return;
                }
                fileName.value = file.name;
            }
        });

        fileName.addEventListener('click', function () {
            fileInput.click();
        });
    }
});

function showFrontendError(message) {
    const errorBox = document.getElementById("o_wsale_errors");
    if (errorBox) {
        errorBox.textContent = message;
        errorBox.classList.remove("d-none");
    }
}