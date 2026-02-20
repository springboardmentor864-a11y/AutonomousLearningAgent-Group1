const downloadReport = async () => {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    "http://localhost:8000/reports/wealth/pdf",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "wealth_report.pdf";
  a.click();
};
