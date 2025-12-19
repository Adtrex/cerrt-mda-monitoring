function getStatusBadge(status) {
    if (!status) return '<span class="badge bg-secondary">Unknown</span>';
    const statusLower = status.toLowerCase();
    if (statusLower === "pass" || statusLower === "success") return '<span class="badge bg-success">Pass</span>';
    if (statusLower === "fail" || statusLower === "failure") return '<span class="badge bg-danger">Fail</span>';
    if (statusLower === "warning") return '<span class="badge bg-warning text-dark">Warning</span>';
    return '<span class="badge bg-secondary">Unknown</span>';
}

function populateSSLData(checks, $root) {
    const mobileContainer = $root.find('#ssl-mobile-cards-container');
    const tableBody = $root.find('#ssl-table-body');

    if (!checks || checks.length === 0) {
        const noDataMessage = `
            <div class="col-12">
                <div class="alert alert-info text-center">
                    <i class="fas fa-info-circle me-2"></i>
                    No SSL checks completed.
                </div>
            </div>
        `;
        mobileContainer.append(noDataMessage);
        tableBody.append(`
            <tr>
                <td colspan="4" class="text-center text-muted">No SSL checks completed.</td>
            </tr>
        `);
        return;
    }

    const mobileScanWrapper = $('<div class="scan-wrapper row g-3"></div>');
    const tableScanWrapper = $('<tbody class="scan-wrapper"></tbody>');

    checks.forEach((check) => {
        const statusBadge = getStatusBadge(check.status);
        const overview = check.overview || "-";
        const details = check.details || "-";
        const recommendation = check.recommendation || "-";

        let borderClass = "border-secondary";
        const statusLower = (check.status || "").toLowerCase();
        if (statusLower === "pass" || statusLower === "success") borderClass = "border-success";
        else if (statusLower === "fail" || statusLower === "failure") borderClass = "border-danger";
        else if (statusLower === "warning") borderClass = "border-warning";

        const mobileCard = `
            <div class="col-12">
                <div class="card border-start border-3 ${borderClass}">
                    <div class="card-body p-3">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0 fw-bold">${overview}</h6>
                            ${statusBadge}
                        </div>
                        <div class="mt-2"><strong class="small">Details:</strong>
                            <div class="text-muted small mt-1">${details}</div>
                        </div>
                        <div class="mt-2"><strong class="small">Recommendation:</strong>
                            <div class="small mt-1">${recommendation}</div>
                        </div>
                        ${check.supported_protocols ? `
                        <div class="mt-2">
                            <strong class="small">Supported Protocols:</strong>
                            <div class="small mt-1">
                                ${check.supported_protocols.map(p => `<span class="badge bg-info text-dark me-1">${p}</span>`).join('')}
                            </div>
                        </div>` : ''}
                    </div>
                </div>
            </div>
        `;
        mobileScanWrapper.append(mobileCard);

        const protocolsDisplay = check.supported_protocols 
            ? check.supported_protocols.map(p => `<span class="badge bg-info text-dark me-1">${p}</span>`).join('')
            : '-';

        const tableRow = `
            <tr>
                <td>${overview}</td>
                <td>${statusBadge}</td>
                <td class="details-col">
                    <div class="small">${details}</div>
                    ${check.supported_protocols ? `<div class="mt-2"><strong>Protocols:</strong> ${protocolsDisplay}</div>` : ''}
                </td>
                <td class="recommendation-col">${recommendation}</td>
            </tr>
        `;
        tableScanWrapper.append(tableRow);
    });

    mobileContainer.append(mobileScanWrapper);
    tableBody.append(tableScanWrapper);
}

function setupSSLColumnToggles($root) {
    $root.find('#ssl-toggle-details').off('change').on('change', function() {
        if (this.checked) {
            $root.find('.details-col').show();
        } else {
            $root.find('.details-col').hide();
        }
    });

    $root.find('#ssl-toggle-recommendation').off('change').on('change', function() {
        if (this.checked) {
            $root.find('.recommendation-col').show();
        } else {
            $root.find('.recommendation-col').hide();
        }
    });
}

function calculateSSLScore(checks) {
    if (!checks || checks.length === 0) return 0;
    const passed = checks.filter(c => {
        const status = (c.status || "").toLowerCase();
        return status === "pass" || status === "success";
    }).length;
    return Math.round((passed / checks.length) * 100);
}

export function renderSSLResults(response, timeTaken, root) {
    const $root = root ? (root instanceof jQuery ? root : $(root)) : $('#result-container');

    let sslInfo = null;
    if (response?.ssl_info) sslInfo = response.ssl_info;
    else if (response?.result?.result) sslInfo = response.result.result;
    else if (response?.result) sslInfo = response.result;
    else sslInfo = response;

    if (!sslInfo || typeof sslInfo !== "object") {
        $root.append(
            `<div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                No SSL information received.
            </div><hr>`
        );
        return;
    }

    const checks = [
        sslInfo.validity || null,
        sslInfo.protocols || null,
        sslInfo.hsts || null
    ].filter(Boolean);

    const overallScore = calculateSSLScore(checks);
    const passedChecks = checks.filter(c => {
        const status = (c.status || "").toLowerCase();
        return status === "pass" || status === "success";
    }).length;
    const failedChecks = checks.length - passedChecks;

    let riskLevel = "Unknown";
    let riskBadgeClass = "bg-secondary";
    if (overallScore >= 80) { riskLevel = "Low"; riskBadgeClass = "bg-success"; }
    else if (overallScore >= 50) { riskLevel = "Medium"; riskBadgeClass = "bg-warning text-dark"; }
    else { riskLevel = "High"; riskBadgeClass = "bg-danger"; }

    const html = `
    <div class="container section-title" data-aos="fade-up">
      <h3>SSL/TLS Security Check (Time: ${timeTaken || "N/A"}s)</h3>
    </div>
    
    <div class="container" data-aos="fade-up" data-aos-delay="100">
      <div class="mb-4">
        <div class="row g-3">
          <div class="col-md-3 col-6">
            <div class="card text-center border-primary">
              <div class="card-body">
                <h2 class="text-primary mb-0">${overallScore}%</h2>
                <small class="text-muted">Security Score</small>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="card text-center border-success">
              <div class="card-body">
                <h2 class="text-success mb-0">${passedChecks}</h2>
                <small class="text-muted">Passed</small>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="card text-center border-danger">
              <div class="card-body">
                <h2 class="text-danger mb-0">${failedChecks}</h2>
                <small class="text-muted">Failed</small>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="card text-center border-${riskBadgeClass === 'bg-success' ? 'success' : riskBadgeClass === 'bg-danger' ? 'danger' : 'warning'}">
              <div class="card-body">
                <span class="badge ${riskBadgeClass} fs-6">${riskLevel}</span>
                <small class="text-muted d-block mt-2">Risk Level</small>
              </div>
            </div>
          </div>
        </div>
        
        <div class="alert alert-info mt-3">
          <i class="bi bi-info-circle me-2"></i>
          <strong>General Recommendation:</strong> 
          ${overallScore >= 80 
            ? 'Your SSL/TLS configuration is strong. Continue monitoring for updates and vulnerabilities.'
            : overallScore >= 50
            ? 'Your SSL/TLS configuration needs improvement. Address the failed checks to enhance security.'
            : 'Your SSL/TLS configuration has critical issues. Immediate action required to secure your site.'}
        </div>
      </div>

      <div class="d-none d-md-block mb-3">
        <small class="text-muted">Toggle columns:</small>
        <div class="btn-group btn-group-sm ms-2" role="group">
          <input type="checkbox" class="btn-check" id="ssl-toggle-details" checked>
          <label class="btn btn-outline-secondary" for="ssl-toggle-details">Details</label>
          
          <input type="checkbox" class="btn-check" id="ssl-toggle-recommendation" checked>
          <label class="btn btn-outline-secondary" for="ssl-toggle-recommendation">Recommendation</label>
        </div>
      </div>

      <div class="d-md-none ssl-mobile">
        <div class="row g-3" id="ssl-mobile-cards-container">
        </div>
      </div>

      <div class="d-none d-md-block">
        <div class="table-responsive">
          <table class="table table-bordered table-striped align-middle" id="ssl-table">
            <thead class="table-light">
              <tr>
                <th style="min-width:200px">Check</th>
                <th style="width:100px">Status</th>
                <th class="details-col" style="min-width:250px">Details</th>
                <th class="recommendation-col" style="min-width:200px">Recommendation</th>
              </tr>
            </thead>
            <tbody id="ssl-table-body"></tbody>
          </table>
        </div>
      </div>
    </div>
    `;

    $root.append(html);

    populateSSLData(checks, $root);
    setupSSLColumnToggles($root);

    $root.append('<hr>');
}
