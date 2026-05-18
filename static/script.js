const fileInput = document.getElementById("pdfFile");
const browseBtn = document.getElementById("browseBtn");
const uploadForm = document.getElementById("uploadForm");
const fileInfo = document.getElementById("fileInfo");
const result = document.getElementById("result");
const statusDiv = document.getElementById("status");
const progressBar = document.getElementById("progressBar");
const clearBtn = document.getElementById("clearBtn");

// ============================
// SINGLE FILE PICKER FIX
// ============================

browseBtn.addEventListener("click", () => {
  fileInput.click();
});

// ============================
// SHOW FILE INFO
// ============================

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];

    fileInfo.innerHTML = `
            <h3>${file.name}</h3>

            <p>
                ${(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
        `;
  }
});

// ============================
// CONVERT
// ============================

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (fileInput.files.length === 0) {
    alert("Please select PDF");

    return;
  }

  const formData = new FormData();

  formData.append("pdf_file", fileInput.files[0]);

  progressBar.style.width = "20%";

  statusDiv.innerHTML = "Uploading PDF...";

  result.innerHTML = "";

  try {
    const response = await fetch("/convert", {
      method: "POST",
      body: formData,
    });

    progressBar.style.width = "80%";

    const data = await response.json();

    progressBar.style.width = "100%";

    if (data.success) {
      statusDiv.innerHTML = `
                Conversion Completed
            `;

      result.innerHTML = `
                <h3>${data.filename}</h3>

                <p>
                    Pages:
                    ${data.pages}
                </p>

                <a href="${data.download_url}"
                   class="download-btn">
                   Download DOCX
                </a>
            `;
    } else {
      statusDiv.innerHTML = `
                ${data.error}
            `;
    }
  } catch (error) {
    statusDiv.innerHTML = `
            Conversion Failed
        `;
  }
});

// ============================
// CLEAR
// ============================

clearBtn.addEventListener("click", async () => {
  fileInput.value = "";

  fileInfo.innerHTML = "";

  result.innerHTML = "";

  statusDiv.innerHTML = "";

  progressBar.style.width = "0%";

  await fetch("/clear", {
    method: "POST",
  });
});

// ============================
// OPEN POPUP
// ============================

function openPopup(id){

    document.getElementById(id).style.display = "flex";
}


// ============================
// CLOSE POPUP
// ============================

function closePopup(id){

    document.getElementById(id).style.display = "none";
}


// ============================
// CLOSE ON OUTSIDE CLICK
// ============================

window.addEventListener("click", (e) => {

    document.querySelectorAll(".popup-overlay")
    .forEach((popup) => {

        if(e.target === popup){

            popup.style.display = "none";
        }
    });
});