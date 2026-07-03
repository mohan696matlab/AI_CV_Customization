import PropTypes from "prop-types";

function SummarySection({
  summary = "",
  handleSummaryChange,
}) {
return (
  <div className="mb-4">
    {/* Header */}
    <div className="mb-2">
      <h4 className="mb-0">Summary</h4>
    </div>

    {/* Textarea */}
    <div className="mb-3">
      <textarea
        className="form-control"
        rows={5}
        value={summary}
        onChange={(e) => handleSummaryChange(e.target.value)}
        placeholder="Write your summary..."
      />
    </div>
  </div>
);
}

export default SummarySection


/* -------- PROP TYPES VALIDATION -------- */
SummarySection.propTypes = {
  summary: PropTypes.string,
  handleSummaryChange: PropTypes.func.isRequired,
};

