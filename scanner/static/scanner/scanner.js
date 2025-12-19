// scanner.js
import { renderSecurityHeaders } from './securityHeadersHandler.js';
import { renderDMARC, renderSPF, renderDKIM, renderEmailSecurity } from './emailSecurityHandlers.js';
import { renderFrontendLibraries } from './frontendLibrariesHandler.js';

// Global variable to store the current URL being scanned
let currentScanUrl = '';
$(document).ready(function () {
    $('#scan-form').on('submit', function (e) {
        e.preventDefault();

        const url = $('#url').val();
        currentScanUrl = url;
        
        // Define the list of actions we want to run
        const actions = [
            { id: "security_headers", name: "Security Headers", icon: "shield-check" },
            { id: "email_security", name: "Email Security", icon: "envelope-check" },
            { id: "frontend_libraries", name: "Frontend Libraries", icon: "code-square" },
            // { id: "open_ports", name: "Open Ports", icon: "network-wired" }
        ];
        
        // Initialize the progress interface
        initializeProgressInterface(actions);
        

        // Recursive function to run actions sequentially
        function runNextAction(index) {
            if (index >= actions.length) {
                completeScan();
                return;
            }

            const action = actions[index];
            updateScanProgress(action.id, 'running');

            const startTime = Date.now();
            const isLastAction = index === actions.length - 1;

            $.ajax({
                url: '/run-scan/',
                type: 'POST',
                data: {
                    url: url,
                    action: action.id,
                    last_action: isLastAction,  // boolean
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                },
                dataType: 'json',
                success: function (response) {
                    const endTime = Date.now();
                    const timeTaken = ((endTime - startTime) / 1000).toFixed(2);

                    // Update progress and dispatch to handler
                    updateScanProgress(action.id, 'completed', timeTaken);
                    handleScanResult(action.id, response, timeTaken);
                    
                    // Update overall progress
                    updateOverallProgress(index + 1, actions.length);
                    
                    if (isLastAction) addDownloadReportButton();
                    runNextAction(index + 1);
                },
                error: function (xhr) {
                    updateScanProgress(action.id, 'failed');
                    $('#result-container').append(
                        `<div class="alert alert-danger mt-3">❌ Error running ${action.name}: ${xhr.responseText}</div>`
                    );
                    runNextAction(index + 1);
                }
            });
        }

        // Start scanning with the first action
        runNextAction(0);
    });
});


// Dispatcher function: decides which handler to call
function handleScanResult(action, response, timeTaken) {
    switch (action) {
        case "security_headers":
            renderSecurityHeaders(response.result, timeTaken);
            break;
        case "email_security":
            renderEmailSecurity(response, timeTaken);
            break;
        case "frontend_libraries":
            renderFrontendLibraries(response, timeTaken);
            break;
        case "dmarc":
            renderDMARC(response, timeTaken);
            break;
        case "spf":
            renderSPF(response, timeTaken);
            break;
        case "dkim":
            renderDKIM(response, timeTaken);
            break;
        case "open_ports":
            renderOpenPorts(response, timeTaken);
            break;
        default:
            console.warn(`No handler defined for ${action}`);
            $('#result-container').append(
                `<div>Result for ${action}: <pre>${JSON.stringify(response, null, 2)}</pre></div>`
            );
    }
}

// Function to add download report button
function addDownloadReportButton() {
    // Remove any existing download buttons
    $('.download-report-btn').remove();
    
    // Create the download button
    const downloadBtn = `
        <div class="text-center mt-4 mb-4">
            <a href="/download-report/?url=${encodeURIComponent(currentScanUrl)}" 
               class="btn btn-success download-report-btn">
                <i class="bi bi-file-earmark-pdf"></i> Download Security Report (PDF)
            </a>
        </div>
    `;
    
    // Add the button to the result container
    $('#result-container').append(downloadBtn);
}

// Progress Interface Functions
function initializeProgressInterface(actions) {
    const progressHtml = `
        <div class="scan-progress-container mb-4">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="bi bi-search"></i> Website Security Scan in Progress</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="fw-semibold">Overall Progress</span>
                            <span id="progress-text">0 of ${actions.length} completed</span>
                        </div>
                        <div class="progress" style="height: 8px;">
                            <div id="overall-progress" class="progress-bar bg-success" role="progressbar" style="width: 0%"></div>
                        </div>
                    </div>
                    <div class="row g-3" id="scan-status-cards">
                        ${actions.map(action => createStatusCard(action)).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    $('#result-container').html(progressHtml);
}

function createStatusCard(action) {
    return `
        <div class="col-md-4">
            <div class="card scan-status-card" id="card-${action.id}">
                <div class="card-body text-center">
                    <div class="status-icon mb-2" id="icon-${action.id}">
                        <i class="bi bi-${action.icon} text-muted" style="font-size: 1.5rem;"></i>
                    </div>
                    <h6 class="card-title">${action.name}</h6>
                    <div class="status-badge" id="status-${action.id}">
                        <span class="badge bg-secondary">Pending</span>
                    </div>
                    <div class="scan-time mt-2" id="time-${action.id}" style="display: none;">
                        <small class="text-muted">Time: <span class="time-value">0s</span></small>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function updateScanProgress(actionId, status, timeTaken = null) {
    const card = $(`#card-${actionId}`);
    const icon = $(`#icon-${actionId} i`);
    const statusBadge = $(`#status-${actionId}`);
    const timeElement = $(`#time-${actionId}`);
    
    // Remove previous status classes
    card.removeClass('border-warning border-success border-danger');
    
    switch(status) {
        case 'running':
            card.addClass('border-warning');
            icon.removeClass('text-muted text-success text-danger').addClass('text-warning');
            statusBadge.html('<span class="badge bg-warning"><i class="bi bi-arrow-clockwise spin"></i> Running</span>');
            break;
        case 'completed':
            card.addClass('border-success');
            icon.removeClass('text-muted text-warning text-danger').addClass('text-success');
            statusBadge.html('<span class="badge bg-success"><i class="bi bi-check-circle"></i> Completed</span>');
            if (timeTaken) {
                timeElement.find('.time-value').text(`${timeTaken}s`);
                timeElement.show();
            }
            break;
        case 'failed':
            card.addClass('border-danger');
            icon.removeClass('text-muted text-warning text-success').addClass('text-danger');
            statusBadge.html('<span class="badge bg-danger"><i class="bi bi-x-circle"></i> Failed</span>');
            break;
    }
}

function updateOverallProgress(completed, total) {
    const percentage = Math.round((completed / total) * 100);
    $('#overall-progress').css('width', `${percentage}%`);
    $('#progress-text').text(`${completed} of ${total} completed`);
}

function completeScan() {
    // Update the header to show completion
    $('.card-header').removeClass('bg-primary').addClass('bg-success');
    $('.card-header h5').html('<i class="bi bi-check-circle"></i> <span style="color: white;">Website Security Scan Completed</span>');
    
    // Add completion message
    $('#result-container').append(`
        <div class="alert alert-success mt-3">
            <i class="bi bi-check-circle-fill"></i> 
            <strong>Scan Complete!</strong> All security checks have been performed successfully.
        </div>
    `);
}

// Add CSS for spinning animation
$('<style>').text(`
    .spin {
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .scan-status-card {
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    .scan-status-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
`).appendTo('head');

