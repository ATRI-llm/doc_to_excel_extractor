// JavaScript logic for DocuExcel

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file-input");
    const progressContainer = document.getElementById("progress-container");
    const uploadFilename = document.getElementById("upload-filename");
    const progressBar = document.getElementById("progress-bar");
    const progressPercentage = document.getElementById("progress-percentage");
    const statusMsg = document.getElementById("status-msg");
    const latestResultPanel = document.getElementById("latest-result-panel");
    
    // Result panels
    const resDocType = document.getElementById("res-doc-type");
    const resSummary = document.getElementById("res-summary");
    const resEntities = document.getElementById("res-entities");
    const resDates = document.getElementById("res-dates");
    const resNumbers = document.getElementById("res-numbers");

    // Table elements
    const tableHeaders = document.getElementById("table-headers");
    const tableBody = document.getElementById("table-body");
    const rowsCount = document.getElementById("rows-count");
    
    // Buttons
    const btnClear = document.getElementById("btn-clear");
    const btnDownload = document.getElementById("btn-download");

    // Global state
    let excelData = [];

    // Initialize application
    init();

    function init() {
        // Load initial excel data
        fetchData();

        // Drag & Drop event listeners
        ["dragenter", "dragover"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add("dragover");
            }, false);
        });

        ["dragleave", "drop"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove("dragover");
            }, false);
        });

        dropzone.addEventListener("drop", (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });

        fileInput.addEventListener("change", (e) => {
            if (fileInput.files.length > 0) {
                handleFileUpload(fileInput.files[0]);
            }
        });

        // Button Event Listeners
        btnClear.addEventListener("click", clearExcelData);
        btnDownload.addEventListener("click", downloadExcel);
    }

    // Toast Notification helper
    function showToast(message, type = "success") {
        const container = document.getElementById("toast-container");
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        
        let icon = "fa-circle-check";
        if (type === "error") icon = "fa-circle-exclamation";
        if (type === "warning") icon = "fa-triangle-exclamation";

        toast.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Trigger entrance animation
        setTimeout(() => toast.classList.add("show"), 10);

        // Remove after 4s
        setTimeout(() => {
            toast.classList.remove("show");
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // Fetch all current Excel rows
    async function fetchData() {
        try {
            const res = await fetch("/api/data");
            if (!res.ok) throw new Error("Failed to load Excel data.");
            excelData = await res.json();
            renderTable();
        } catch (error) {
            console.error(error);
            showToast(error.message, "error");
        }
    }

    // Render columns and rows dynamically
    function renderTable() {
        if (!excelData || excelData.length === 0) {
            // Render empty state
            tableHeaders.innerHTML = `
                <th>Filename</th>
                <th>Document Type</th>
                <th>Summary</th>
                <th>Important Dates</th>
                <th>Important Numbers</th>
            `;
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-state">
                        <div class="empty-state-icon">
                            <i class="fa-solid fa-folder-open"></i>
                        </div>
                        <h3>No records found</h3>
                        <p>Upload a document on the left to start extracting and building your Excel sheet.</p>
                    </td>
                </tr>
            `;
            rowsCount.textContent = "0 records";
            return;
        }

        // Determine all unique column headers across all objects in array
        const standardHeaders = ["Filename", "Document Type", "Summary", "Important Dates", "Important Numbers"];
        const entityHeadersSet = new Set();

        excelData.forEach(row => {
            Object.keys(row).forEach(key => {
                if (!standardHeaders.includes(key) && key.startsWith("Entity: ")) {
                    entityHeadersSet.add(key);
                }
            });
        });

        // Sort entity headers alphabetically
        const entityHeaders = Array.from(entityHeadersSet).sort();
        const allHeaders = [...standardHeaders, ...entityHeaders];

        // Render headers
        tableHeaders.innerHTML = allHeaders.map(header => `<th>${header}</th>`).join("");

        // Render rows
        tableBody.innerHTML = excelData.map(row => {
            return `
                <tr>
                    ${allHeaders.map(header => {
                        const val = row[header];
                        const displayVal = val === null || val === undefined ? "" : val;
                        
                        // Style Entity values slightly differently
                        if (header.startsWith("Entity: ") && displayVal !== "") {
                            return `<td title="${displayVal}"><span class="badge" style="background-color:rgba(139,92,246,0.06); border:1px solid rgba(139,92,246,0.15); color:#c084fc; font-family:var(--font-mono); font-size:0.75rem;">${displayVal}</span></td>`;
                        }
                        
                        return `<td title="${displayVal}">${displayVal}</td>`;
                    }).join("")}
                </tr>
            `;
        }).join("");

        rowsCount.textContent = `${excelData.length} record${excelData.length === 1 ? "" : "s"}`;
    }

    // Handle asynchronous document upload and parsing
    async function handleFileUpload(file) {
        // Reset and show progress state
        progressContainer.classList.remove("hidden");
        latestResultPanel.classList.add("hidden");
        uploadFilename.textContent = file.name;
        progressBar.style.width = "10%";
        progressPercentage.textContent = "10%";
        statusMsg.innerHTML = `<i class="fa-solid fa-cloud-arrow-up fa-bounce"></i> Uploading document files...`;

        // Create FormData
        const formData = new FormData();
        formData.append("file", file);

        // Animate progress simulation
        let currentProgress = 10;
        const progressInterval = setInterval(() => {
            if (currentProgress < 75) {
                currentProgress += 5;
                progressBar.style.width = `${currentProgress}%`;
                progressPercentage.textContent = `${currentProgress}%`;

                if (currentProgress === 35) {
                    statusMsg.innerHTML = `<i class="fa-solid fa-gears fa-spin"></i> Extracting text data from document...`;
                } else if (currentProgress === 55) {
                    statusMsg.innerHTML = `<i class="fa-solid fa-brain fa-fade"></i> Running AI models to analyze content...`;
                }
            }
        }, 300);

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            clearInterval(progressInterval);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Upload or parsing failed.");
            }

            const result = await response.json();

            // Set progress to 100%
            progressBar.style.width = "100%";
            progressPercentage.textContent = "100%";
            statusMsg.innerHTML = `<i class="fa-solid fa-check text-success"></i> Done!`;

            // Display latest result details
            displayLatestResult(result.data);
            showToast("Document parsed and Excel updated successfully!");

            // Refresh table list
            fetchData();
        } catch (error) {
            clearInterval(progressInterval);
            progressBar.style.width = "0%";
            progressPercentage.textContent = "0%";
            statusMsg.innerHTML = `<i class="fa-solid fa-circle-exclamation text-error"></i> Error.`;
            showToast(error.message, "error");
        } finally {
            setTimeout(() => {
                progressContainer.classList.add("hidden");
            }, 2500);
        }
    }

    // Populate Left side details card
    function displayLatestResult(data) {
        latestResultPanel.classList.remove("hidden");
        
        // Document type badge
        resDocType.textContent = data.document_type || "Unknown Document";
        
        // Summary text
        resSummary.textContent = data.summary || "No summary provided by the model.";

        // Entities key-value rows
        const entities = data.entities || {};
        const entityKeys = Object.keys(entities);
        if (entityKeys.length > 0) {
            resEntities.innerHTML = entityKeys.map(key => {
                const cleanKey = key.replace(/_/g, " ");
                return `
                    <div class="metadata-row">
                        <span class="metadata-key">${cleanKey}</span>
                        <span class="metadata-val" title="${entities[key]}">${entities[key]}</span>
                    </div>
                `;
            }).join("");
        } else {
            resEntities.innerHTML = `<div class="metadata-row" style="justify-content:center; color:var(--text-muted);">No key metadata extracted</div>`;
        }

        // Dates list
        const dates = data.important_dates || [];
        if (dates.length > 0) {
            resDates.innerHTML = dates.map(d => `<li>${d}</li>`).join("");
        } else {
            resDates.innerHTML = `<li style="font-family:var(--font-sans); color:var(--text-muted); background:transparent; border:none; padding:0;">None</li>`;
        }

        // Numbers list
        const numbers = data.important_numbers || [];
        if (numbers.length > 0) {
            resNumbers.innerHTML = numbers.map(n => `<li>${n}</li>`).join("");
        } else {
            resNumbers.innerHTML = `<li style="font-family:var(--font-sans); color:var(--text-muted); background:transparent; border:none; padding:0;">None</li>`;
        }
    }

    // Clear excel spreadsheet on server
    async function clearExcelData() {
        if (!confirm("Are you sure you want to clear the Excel spreadsheet and delete all uploaded documents? This cannot be undone.")) {
            return;
        }

        try {
            const res = await fetch("/api/clear", { method: "POST" });
            if (!res.ok) throw new Error("Failed to clear Excel data.");
            
            showToast("Spreadsheet cleared successfully.");
            latestResultPanel.classList.add("hidden");
            
            // Reload table
            fetchData();
        } catch (error) {
            console.error(error);
            showToast(error.message, "error");
        }
    }

    // Redirect to download Excel file
    function downloadExcel() {
        if (!excelData || excelData.length === 0) {
            showToast("Spreadsheet is empty. Upload some files first.", "warning");
            return;
        }
        window.location.href = "/api/download";
    }
});
