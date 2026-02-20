export async function getInvestments({ token, userId = null } = {}) {
  let url = "http://127.0.0.1:8000/investments/user";

  if (userId) {
    url = `http://127.0.0.1:8000/investments/user/${userId}`;
  }

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch investments");
  }

  return response.json();
}
