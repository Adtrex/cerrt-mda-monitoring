// frontendLibrariesHandler.js

// Utility: risk badge color (consistent with your other handlers)
function getRiskBadge(risk) {
    let badgeClass = "badge bg-secondary";
    if (risk === "Low") badgeClass = "badge bg-success";
    else if (risk === "Medium") badgeClass = "badge bg-warning text-dark";
    else if (risk === "High") badgeClass = "badge bg-danger";
    return `<span class="${badgeClass}">${risk}</span>`;
}

// Helper function to populate both mobile and desktop layouts
function populateLibrariesData(entries) {
    const mobileContainer = $('#mobile-cards-container');
    const tableBody = $('#table-body');
    
    if (entries.length === 0) {
        // Show no data message
        mobileContainer.html(`
            <div class="col-12">
                <div class="alert alert-info text-center">
                    <i class="fas fa-info-circle me-2"></i>
                    No libraries detected in this scan.
                </div>
            </div>
        `);
        tableBody.html(`
            <tr>
                <td colspan="8" class="text-center text-muted">No libraries detected in this scan.</td>
            </tr>
        `);
        return;
    }

    // Clear containers
    mobileContainer.empty();
    tableBody.empty();

    entries.forEach(raw => {
        const r = normalizeLibEntry(raw);
        
        // Status class mapping
        let statusClass = "text-muted";
        const statusLower = (r.status || "").toLowerCase();
        if (statusLower === "up-to-date" || statusLower === "up_to_date" || statusLower === "up_to-date" || statusLower === "up_to_date" || statusLower === "up-to-date" || statusLower === "up_to_date") {
            statusClass = "text-success fw-semibold";
        } else if (statusLower === "outdated") {
            statusClass = "text-danger fw-semibold";
        } else if (statusLower === "no-version") {
            statusClass = "text-warning text-dark fw-semibold";
        } else if (statusLower === "unknown") {
            statusClass = "text-secondary";
        }

        const displayName = String(r.name || "-");
        const displayCanonical = r.canonical || "-";
        const detected = r.detected_version || "-";
        const latest = r.latest_version || "-";
        const riskTag = getRiskBadge(r.risk || "Unknown");
        const status = (r.status || "unknown").toString().toUpperCase();
        const recommendation = r.recommendation || "-";

        // Build sources HTML
        let sourcesHtml = "-";
        if (Array.isArray(r.src_urls) && r.src_urls.length > 0) {
            const first = r.src_urls[0];
            const rest = r.src_urls.slice(1);
            sourcesHtml = `<div class="small"><code title="${first}">${first.length > 60 ? first.slice(0, 57) + "..." : first}</code></div>`;
            if (rest.length > 0) {
                sourcesHtml += `<details class="mt-1"><summary class="small text-muted">+ ${rest.length} more</summary><ul class="mb-1">`;
                rest.forEach(u => {
                    sourcesHtml += `<li class="small"><code title="${u}">${u.length > 100 ? u.slice(0, 97) + "..." : u}</code></li>`;
                });
                sourcesHtml += `</ul></details>`;
            }
        }

        // Create mobile card
        const mobileCard = `
            <div class="col-12">
                <div class="card border-start border-3 ${statusLower === 'up-to-date' || statusLower === 'up_to_date' ? 'border-success' : statusLower === 'outdated' ? 'border-danger' : 'border-warning'}">
                    <div class="card-body p-3">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0 fw-bold">${displayName}</h6>
                            <div class="d-flex gap-2">
                                ${riskTag}
                                <span class="badge ${statusClass.includes('success') ? 'bg-success' : statusClass.includes('danger') ? 'bg-danger' : statusClass.includes('warning') ? 'bg-warning text-dark' : 'bg-secondary'} text-uppercase">${status}</span>
                            </div>
                        </div>
                        
                        <div class="row g-2 small">
                            <div class="col-6">
                                <strong>Detected:</strong> <code>${detected}</code>
                            </div>
                            <div class="col-6">
                                <strong>Latest:</strong> <code>${latest}</code>
                            </div>
                        </div>
                        
                        <div class="mt-2 small">
                            <strong>Recommendation:</strong> ${recommendation}
                        </div>
                        
                        ${r.src_urls && r.src_urls.length > 0 ? `
                            <div class="mt-2">
                                <strong class="small">Sources:</strong>
                                <div class="mt-1">${sourcesHtml}</div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        // Create table row
        const tableRow = `
            <tr>
                <td title="${displayName}">${displayName}</td>
                <td class="canonical-col">${displayCanonical}</td>
                <td>${detected}</td>
                <td>${latest}</td>
                <td class="${statusClass}">${status}</td>
                <td>${riskTag}</td>
                <td>${recommendation}</td>
                <td class="sources-col">${sourcesHtml}</td>
            </tr>
        `;
        
        mobileContainer.append(mobileCard);
        tableBody.append(tableRow);
    });
}

// Helper function to setup column toggle functionality
function setupColumnToggles() {
    $('#toggle-canonical').on('change', function() {
        if (this.checked) {
            $('.canonical-col').show();
        } else {
            $('.canonical-col').hide();
        }
    });
    
    $('#toggle-sources').on('change', function() {
        if (this.checked) {
            $('.sources-col').show();
        } else {
            $('.sources-col').hide();
        }
    });
}

/**
 * Normalize library entry fields to a consistent shape for rendering.
 * Accepts variations in key names coming from different implementations.
 */
function normalizeLibEntry(r) {
    return {
        name: r.name || r.library || r.detected_name || (Array.isArray(r.src_urls) && r.src_urls[0]) || "-",
        canonical: r.canonical || r.canonical_name || null,
        detected_version: r.detected_version || r.version_detected || r.version || null,
        latest_version: r.latest_version || r.stable_version || r.latest || null,
        status: (r.status || "").toString(),
        risk: r.risk || "Unknown",
        overview: r.overview || (Array.isArray(r.notes) ? r.notes.join(", ") : "") || (r.detection_methods ? r.detection_methods.join(", ") : "") || "-",
        recommendation: r.recommendation || "-",
        src_urls: Array.isArray(r.src_urls) ? r.src_urls : (r.src ? [r.src] : [])
    };
}

// Main renderer (exported)
export function renderFrontendLibraries(response, timeTaken) {
    // Accept both { result: {...}} and direct payload {...}
    const payload = (response && response.result) ? response.result : response;

    if (!payload || typeof payload !== "object") {
        $('#result-container').append(
            `<div class="text-danger">No response received for Frontend Libraries scan.</div><hr>`
        );
        return;
    }

    const summary = payload.summary || {};
    // Normalize summary fields from possible variants
    const totalScripts = summary.total_scripts ?? summary.totalScripts ?? 0;
    const uniqueLibraries = summary.unique_libraries ?? summary.uniqueLibraries ?? summary.total_libraries ?? (Array.isArray(payload.results) ? payload.results.length : 0);
    const withDetected = summary.with_detected_version ?? summary.withDetectedVersion ?? summary.with_detected_version ?? 0;
    const withoutDetected = summary.without_detected_version ?? summary.withoutDetectedVersion ?? 0;
    const upToDate = (summary.up_to_date ?? summary.upToDate ?? summary.up_to_date_count ?? summary.upToDateCount) || 0;
    const outdated = summary.outdated ?? 0;
    const score = summary.score ?? 0;
    const riskLevel = summary.risk_level ?? summary.riskLevel ?? "Unknown";

    // Build header / summary block with centered structure
    let html = `
    <div class="container section-title" data-aos="fade-up">
      <h3>Frontend Libraries Check (Time: ${timeTaken || "N/A"}s)</h3>
    </div>
    
    <div class="container" data-aos="fade-up" data-aos-delay="100">
      <div class="mb-4">
        <p>
          <strong>Total scripts:</strong> ${totalScripts} &nbsp;|&nbsp;
          <strong>Unique libraries:</strong> ${uniqueLibraries} &nbsp;|&nbsp;
          <strong>With version:</strong> ${withDetected} &nbsp;|&nbsp;
          <strong>Without version:</strong> ${withoutDetected}
        </p>
        <p>
          <strong>Up-to-date:</strong> <span class="text-success">${upToDate}</span> &nbsp;|&nbsp;
          <strong>Outdated:</strong> <span class="text-danger">${outdated}</span> &nbsp;|&nbsp;
          <strong>Score:</strong> ${score}% &nbsp;|&nbsp;
          <strong>Risk:</strong> ${getRiskBadge(riskLevel)}
        </p>
        <p><strong>General Recommendation:</strong> ${payload.general_recommendation || "-"}</p>
      </div>

    <!-- Column Toggle Controls for Tablet/Desktop -->
    <div class="d-none d-md-block mb-3">
      <small class="text-muted">Toggle columns:</small>
      <div class="btn-group btn-group-sm ms-2" role="group">
        <input type="checkbox" class="btn-check" id="toggle-canonical" checked>
        <label class="btn btn-outline-secondary" for="toggle-canonical">Canonical</label>
        
        <input type="checkbox" class="btn-check" id="toggle-sources" checked>
        <label class="btn btn-outline-secondary" for="toggle-sources">Sources</label>
      </div>
    </div>

    <!-- Mobile Card Layout -->
    <div class="d-md-none frontend-libs-mobile">
      <div class="row g-3" id="mobile-cards-container">
        <!-- Mobile cards will be inserted here -->
      </div>
    </div>

    <!-- Desktop/Tablet Table Layout -->
    <div class="d-none d-md-block">
      <div class="table-responsive">
        <table class="table table-bordered table-striped align-middle text-sm" id="frontend-libs-table">
          <thead class="table-light">
            <tr>
              <th style="min-width:150px">Name</th>
              <th class="canonical-col">Canonical</th>
              <th>Detected</th>
              <th>Latest</th>
              <th>Status</th>
              <th>Risk</th>
              <th style="min-width:200px">Recommendation</th>
              <th class="sources-col" style="min-width:160px">Sources</th>
            </tr>
          </thead>
          <tbody id="table-body">
            <!-- Table rows will be inserted here -->
          </tbody>
        </table>
      </div>
      </div>
    </div>
    `;

    const entries = Array.isArray(payload.results) ? payload.results : [];

    // Add the HTML structure first
    $('#result-container').append(html);

    // Now populate both mobile cards and desktop table
    populateLibrariesData(entries);

    // Add column toggle functionality
    setupColumnToggles();

    // Add final separator
    $('#result-container').append('<hr>');
}
