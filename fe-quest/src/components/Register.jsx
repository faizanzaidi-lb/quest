import React, { useState } from "react";
import axios from "axios";

const Register = ({ onUserAdded }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8001/register", {
        username,
        password,
      });
      alert(response.data.message);
      setUsername("");
      setPassword("");
      onUserAdded(); // Call the prop function to refresh user list
    } catch (error) {
      alert(error.response.data.detail);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-6 rounded-lg shadow-md mt-6"
    >
      <h2 className="text-2xl font-semibold mb-4">Register</h2>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
        required
        className="border border-gray-300 p-2 rounded-lg mb-4 w-full focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
        className="border border-gray-300 p-2 rounded-lg mb-4 w-full focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
      <button
        type="submit"
        className="bg-blue-500 text-white p-2 rounded-lg w-full hover:bg-blue-600 transition"
      >
        Register
      </button>
    </form>
  );
};

export default Register;
