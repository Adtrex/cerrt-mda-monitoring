// emailSecurityHandlers.js

// Handler for DMARC results
export function renderDMARC(response, timeTaken) {
    if (!response || !response.result) {
        $('#result-container').append(
            `<div class="text-red-600">⚠️ No response received for DMARC scan.</div><hr>`
        );
        return;
    }

    const result = response.result;
    const statusClass = result.status === "pass" ? "text-green-600" : "text-red-600";
    const statusIcon = result.status === "pass" ? "✅" : "❌";

    let html = `
        <h3>📧 DMARC Check (Time: ${timeTaken || "N/A"}s)</h3>
        <div class="${statusClass}">
            <strong>${statusIcon} Status:</strong> ${result.status.toUpperCase()}
        </div>
        <p><strong>Details:</strong> ${result.details || "No details available."}</p>
        <p><strong>Recommendation:</strong> ${result.recommendation || "No recommendation available."}</p>
    `;

    if (result.raw_record) {
        html += `<p><strong>Raw Record:</strong> <code>${result.raw_record}</code></p>`;
    }

    html += "<hr>";
    $('#result-container').append(html);
}

// Handler for SPF results
export function renderSPF(response, timeTaken) {
    if (!response || !response.result) {
        $('#result-container').append(
            `<div class="text-red-600">⚠️ No response received for SPF scan.</div><hr>`
        );
        return;
    }

    const result = response.result;
    const statusClass = result.status === "pass" ? "text-green-600" : "text-red-600";
    const statusIcon = result.status === "pass" ? "✅" : "❌";

    let html = `
        <h3>📧 SPF Check (Time: ${timeTaken || "N/A"}s)</h3>
        <div class="${statusClass}">
            <strong>${statusIcon} Status:</strong> ${result.status.toUpperCase()}
        </div>
        <p><strong>Details:</strong> ${result.details || "No details available."}</p>
        <p><strong>Recommendation:</strong> ${result.recommendation || "No recommendation available."}</p>
    `;

    if (result.raw_record) {
        html += `<p><strong>Raw Record:</strong> <code>${result.raw_record}</code></p>`;
    }

    html += "<hr>";
    $('#result-container').append(html);
}

// Handler for DKIM results
export function renderDKIM(response, timeTaken) {
    if (!response || !response.result) {
        $('#result-container').append(
            `<div class="text-red-600">⚠️ No response received for DKIM scan.</div><hr>`
        );
        return;
    }

    const result = response.result;
    const statusClass = result.status === "pass" ? "text-green-600" : "text-red-600";
    const statusIcon = result.status === "pass" ? "✅" : "❌";

    let html = `
        <h3>📧 DKIM Check (Time: ${timeTaken || "N/A"}s)</h3>
        <div class="${statusClass}">
            <strong>${statusIcon} Status:</strong> ${result.status.toUpperCase()}
        </div>
        <p><strong>Details:</strong> ${result.details || "No details available."}</p>
        <p><strong>Recommendation:</strong> ${result.recommendation || "No recommendation available."}</p>
    `;

    if (result.selectors && result.selectors.length > 0) {
        html += `<p><strong>Found Selectors:</strong></p><ul>`;
        result.selectors.forEach(selector => {
            html += `<li><strong>${selector.selector}:</strong> <code>${selector.record}</code></li>`;
        });
        html += `</ul>`;
    }

    html += "<hr>";
    $('#result-container').append(html);
}

// Handler for combined email security results
export function renderEmailSecurity(response, timeTaken) {
    if (!response || !response.result) {
        $('#result-container').append(
            `<div class="alert alert-danger mt-3">⚠️ No response received for Email Security scan.</div>`
        );
        return;
    }

    const result = response.result;
    const summary = result.summary || {
        score: 0,
        passed: 0,
        failed: 0,
        total_checks: 0,
        risk_level: "Unknown"
    };

    // Risk badge color
    let riskBadgeClass = "bg-secondary";
    if (summary.risk_level === "Low") riskBadgeClass = "bg-success";
    else if (summary.risk_level === "Medium") riskBadgeClass = "bg-warning text-dark";
    else if (summary.risk_level === "High") riskBadgeClass = "bg-danger";

    // Calculate stroke-dasharray for the SVG circle
    const progress = summary.score || 0;
    const strokeDash = `${progress}, 100`;

    let html = `
       <!-- Section Title -->
      <div class="container section-title" data-aos="fade-up">
        <h2>Email Security</h2>
      </div><!-- End Section Title -->

      <div class="container" data-aos="fade-up" data-aos-delay="100">
    <div class="services-grid">
      <div class="row g-4">

        <!-- Left: Score Circle -->
        <div class="col-lg-4">
          <div class="featured-service-card text-center">
            <div class="service-badge">Score</div>
            <div class="position-relative d-inline-block" style="width:100px; height:100px;">
              <svg class="w-100 h-100" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845
                     a 15.9155 15.9155 0 0 1 0 31.831
                     a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#e6e6e6"
                  stroke-width="2.8"
                />
                <path
                  d="M18 2.0845
                     a 15.9155 15.9155 0 0 1 0 31.831
                     a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#28a745"
                  stroke-width="2.8"
                  stroke-dasharray="${strokeDash}"
                />
              </svg>
              <div class="position-absolute top-50 start-50 translate-middle">
                <span class="fw-bold">${progress}%</span>
              </div>
            </div>
            <h3 class="mt-2">Security Score</h3>
          </div>
        </div>

        <!-- Right: Summary & Recommendation -->
        <div class="col-lg-8">
          <div class="service-card p-3">
            <p class="mb-1 text-muted">
              Passed: <span class="fw-semibold">${summary.passed}</span> / ${summary.total_checks}
            </p>
            <span class="badge ${riskBadgeClass}">Risk: ${summary.risk_level}</span>
            <h4 class="mt-3">Recommendation</h4>
            <p>${result.general_recommendation || "No recommendation available."}</p>
            <small class="text-muted">Scan Time: ${timeTaken || "N/A"}s</small>
          </div>
        </div>

        <!-- Table of Results -->
        <div class="col-lg-12 mt-4">
          <h4>Email Security Details</h4>
          <div class="table-responsive">
            <table class="table table-bordered table-light align-middle">
              <thead class="table-light">
                <tr>
                  <th>Check</th>
                  <th>Status</th>
                  <th>Details</th>
                  <th>Recommendation</th>
                </tr>
              </thead>
              <tbody>
    `;

  if (Array.isArray(result.results) && result.results.length > 0) {
    result.results.forEach(r => {
      const statusClass = r.status === "pass" ? "text-success fw-semibold" : "text-danger fw-semibold";
      html += `
        <tr>
          <td>${r.check || "-"}</td>
          <td class="${statusClass}">${(r.status || "unknown").toUpperCase()}</td>
          <td>${r.details || "No details available."}</td>
          <td>${r.recommendation || "-"}</td>
        </tr>
      `;
    });
  } else {
    html += `
      <tr>
        <td colspan="4" class="text-center text-muted">No results available for this scan.</td>
      </tr>
    `;
  }

  html += `
              </tbody>
            </table>
          </div>
        </div>

      </div>
      </div>
    </div>
  `;

  $('#result-container').append(html);
}