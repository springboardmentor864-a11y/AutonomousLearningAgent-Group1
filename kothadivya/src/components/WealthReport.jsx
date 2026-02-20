import React from "react";

const Reports = () => {

  const downloadReport = () => {
    window.open("http://localhost:8000/reports/wealth/pdf", "_blank");
  };

  return (
    <div>
      <h2>Wealth Reports</h2>

      <button onClick={downloadReport}>
        Download Wealth Report (PDF)
      </button>
    </div>
  );
};

export default Reports;
