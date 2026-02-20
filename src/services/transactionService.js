import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// attach token automatically
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getTransactions = () => {
  return API.get("/transactions/");
};

export const createTransaction = async (
  amount,
  category,
  transactionType,
  description
) => {
  return await api.post("/transactions/", data,{
    amount: Number(amount),
    category: category,
    transaction_type: transactionType,
    description: description,
  });
};
