import axios from "axios";

const token = localStorage.getItem("token");

useEffect(() => {
  axios.get("http://127.0.0.1:8000/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}, []);
