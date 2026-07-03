import React, { useState } from "react";
// Removed react-markdown as we are now rendering structured JSON natively

function JobDescriptionAnalysis({ form, setForm, analysis, setAnalysis }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("http://localhost:8000/extract-job-insights", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_description: form.jobDescription,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to analyze job description");
      }

      const data = await res.json();
      console.log(data);
      setAnalysis(data);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  // Helper to cleanly render arrays (like languages, tools) as Bootstrap badges
  const renderBadges = (items) => {
    if (!items || items.length === 0 || items[0] === "Not Specified") {
      return <span className="text-muted fst-italic">Not Specified</span>;
    }
    return items.map((item, index) => (
      <span key={index} className="badge bg-secondary me-1 mb-1">
        {item}
      </span>
    ));
  };

  return (
   <div className="container-fluid py-4">
  {/* Title */}
  <h2 className="mb-4 text-center text-body">
    Job Description Intelligence Extractor
  </h2>

  <div className="row g-4">
    {/* LEFT PANEL */}
    <div className="col-lg-5">
      <div className="card shadow-sm h-100 bg-body">
        <div className="card-body">
          <textarea
            className="form-control mb-3"
            placeholder="Paste job description here..."
            value={form.jobDescription || ""}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                jobDescription: e.target.value,
              }))
            }
            style={{
              minHeight: "650px",
              resize: "none",
              backgroundColor: "var(--bs-body-bg)",
              color: "var(--bs-body-color)",
            }}
          />

          <button
            className="btn btn-primary w-100 py-2 fw-bold"
            onClick={handleAnalyze}
            disabled={loading || !form.jobDescription?.trim()}
          >
            {loading && (
              <span className="spinner-border spinner-border-sm me-2" />
            )}
            {loading ? "Analyzing Context..." : "Analyze Description"}
          </button>

          {error && (
            <div className="alert alert-danger mt-3 mb-0" role="alert">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>

    {/* RIGHT PANEL */}
    <div className="col-lg-7">
      <div className="card shadow-sm h-100 bg-body">
        <div
          className="card-body"
          style={{ overflowY: "auto", maxHeight: "800px" }}
        >
          {/* EMPTY STATE */}
          {!analysis && !loading && (
            <div className="text-center text-body-secondary py-5 mt-5">
              <i className="bi bi-file-earmark-text display-4 mb-3 d-block"></i>
              <h5 className="text-body">No analysis yet</h5>
              <p className="mb-0">
                Paste a job description and click analyze.
              </p>
            </div>
          )}

          {/* LOADING STATE */}
          {loading && (
            <div className="text-center py-5 mt-5">
              <div
                className="spinner-border text-primary"
                role="status"
                style={{ width: "3rem", height: "3rem" }}
              >
                <span className="visually-hidden">Loading...</span>
              </div>
              <div className="mt-3 fw-medium text-body-secondary">
                Extracting intelligence...
              </div>
            </div>
          )}

          {/* ANALYSIS RESULT */}
          {analysis && !loading && analysis.analysis && (
            <div>
              {/* Header */}
              <div className="mb-4 pb-3 border-bottom">
                <h3 className="mb-1 text-primary">
                  {analysis.job_title || "Unknown Role"}
                </h3>
                <h5 className="text-body-secondary">
                  {analysis.company_name || "Unknown Company"}
                </h5>
              </div>

              <div className="d-flex flex-column gap-4">
                {/* Section 1 */}
                <section>
                  <h5 className="text-uppercase text-body-secondary fw-bold mb-3">
                    1. Gatekeepers
                  </h5>

                  <div className="row g-3 bg-body-tertiary p-3 rounded">
                    <div className="col-md-6">
                      <strong className="d-block mb-1">
                        Core Paradigms:
                      </strong>
                      <div>
                        {renderBadges(
                          analysis.analysis.gatekeepers.core_paradigms
                        )}
                      </div>
                    </div>

                    <div className="col-md-6">
                      <strong className="d-block mb-1">
                        Programming Languages:
                      </strong>
                      <div>
                        {renderBadges(
                          analysis.analysis.gatekeepers.programming_languages
                        )}
                      </div>
                    </div>

                    <div className="col-md-6">
                      <strong className="d-block mb-1">
                        Infrastructure & Tools:
                      </strong>
                      <div>
                        {renderBadges(
                          analysis.analysis.gatekeepers
                            .infrastructure_and_tools
                        )}
                      </div>
                    </div>

                    <div className="col-md-6">
                      <strong className="d-block mb-1">Languages:</strong>
                      <div>
                        {renderBadges(
                          analysis.analysis.gatekeepers.languages
                        )}
                      </div>
                    </div>

                    <div className="col-12 mt-3 pt-3 border-top">
                      <strong>Education Tier:</strong>
                      <span className="ms-2 text-body">
                        {analysis.analysis.gatekeepers.education_tier}
                      </span>
                    </div>
                  </div>
                </section>

                {/* Section 2 */}
                <section>
                  <h5 className="text-uppercase text-body-secondary fw-bold mb-3">
                    2. The Essence
                  </h5>

                  <div className="card border-0 bg-body-tertiary mb-2">
                    <div className="card-body py-2 px-3">
                      <h6 className="fw-bold mb-1 text-body">
                        Ultimate Product Goal
                      </h6>
                      <p className="mb-0 text-body-secondary">
                        {analysis.analysis.the_essence.ultimate_product_goal}
                      </p>
                    </div>
                  </div>

                  <div className="card border-0 bg-body-tertiary mb-2">
                    <div className="card-body py-2 px-3">
                      <h6 className="fw-bold mb-1 text-body">
                        Technical Bottleneck
                      </h6>
                      <p className="mb-0 text-body-secondary">
                        {analysis.analysis.the_essence.technical_bottleneck}
                      </p>
                    </div>
                  </div>

                  <div className="card border-0 bg-body-tertiary">
                    <div className="card-body py-2 px-3">
                      <h6 className="fw-bold mb-1 text-body">
                        Applied vs Theoretical Divide
                      </h6>
                      <p className="mb-0 text-body-secondary">
                        {analysis.analysis.the_essence.applied_vs_theoretical_divide}
                      </p>
                    </div>
                  </div>
                </section>

                {/* Section 3 */}
                <section>
                  <h5 className="text-uppercase text-body-secondary fw-bold mb-3">
                    3. High-Priority Missions (80/20)
                  </h5>

                  <ol className="list-group list-group-numbered">
                    {[1, 2, 3].map((i) => (
                      <li
                        key={i}
                        className="list-group-item d-flex justify-content-between align-items-start border-0 bg-body-tertiary mb-2 rounded"
                      >
                        <div className="ms-2 me-auto">
                          <div className="fw-bold">
                            Priority {i}
                          </div>
                          <span className="text-body-secondary">
                            {
                              analysis.analysis.high_priority_missions[
                                `priority_${i}`
                              ]
                            }
                          </span>
                        </div>
                      </li>
                    ))}
                  </ol>
                </section>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  </div>
</div>
  );
}

export default JobDescriptionAnalysis;