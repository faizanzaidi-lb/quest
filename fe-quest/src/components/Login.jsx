import React, { useState } from "react";
import axios from "axios";

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8001/login", {
        username,
        password,
      });
      alert(response.data.message);
      setUsername("");
      setPassword("");

      if (response.data.user_id) {
        onLogin(response.data.user_id);
      } else {
        alert("Login successful, but user ID is not available.");
      }
    } catch (error) {
      alert(error.response.data.detail);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2 className="text-xl font-semibold">Login</h2>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
        required
        className="border border-gray-300 p-2 rounded-lg mb-4 w-full"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
        className="border border-gray-300 p-2 rounded-lg mb-4 w-full"
      />
      <button
        type="submit"
        className="bg-blue-500 text-white p-2 rounded-lg w-full hover:bg-blue-600 transition"
      >
        Login
      </button>
    </form>
  );
};

export default Login;
