// src/App.jsx

import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  // Base URL for API Gateway
  const API_BASE = "http://localhost:8000";

  // State variables
  const [signupData, setSignupData] = useState({
    user_name: "",
    password: "",
    status: "new",
  });
  const [loginData, setLoginData] = useState({ user_name: "", password: "" });
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [user, setUser] = useState(null);
  const [quests, setQuests] = useState([]);
  const [assignQuestData, setAssignQuestData] = useState({ quest_id: "" });
  const [userQuests, setUserQuests] = useState([]);

  // Axios instance with Authorization header
  const axiosInstance = axios.create({
    baseURL: API_BASE,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  // Fetch user details after login/signup
  useEffect(() => {
    if (token) {
      // Decode token to get user_id (assuming JWT)
      const decodeToken = (token) => {
        try {
          const payload = token.split(".")[1];
          return JSON.parse(atob(payload));
        } catch (e) {
          return null;
        }
      };
      const decoded = decodeToken(token);
      if (decoded && decoded.user_id) {
        fetchUser(decoded.user_id);
      }
    }
  }, [token]);

  const fetchUser = async (user_id) => {
    try {
      const response = await axios.get(`${API_BASE}/users/${user_id}`);
      setUser(response.data);
    } catch (error) {
      console.error(
        "Error fetching user:",
        error.response?.data || error.message
      );
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE}/signup`, signupData);
      setToken(response.data.access_token);
      localStorage.setItem("token", response.data.access_token);
      alert("Signup successful!");
    } catch (error) {
      console.error("Signup error:", error.response?.data || error.message);
      alert(`Signup failed: ${error.response?.data.detail || error.message}`);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE}/login`, loginData);
      setToken(response.data.access_token);
      localStorage.setItem("token", response.data.access_token);
      alert("Login successful!");
    } catch (error) {
      console.error("Login error:", error.response?.data || error.message);
      alert(`Login failed: ${error.response?.data.detail || error.message}`);
    }
  };

  const fetchQuests = async () => {
    try {
      const response = await axiosInstance.get("/quests/");
      setQuests(response.data);
    } catch (error) {
      console.error(
        "Error fetching quests:",
        error.response?.data || error.message
      );
    }
  };

  const assignQuest = async (e) => {
    e.preventDefault();
    if (!user) {
      alert("Please log in first.");
      return;
    }
    try {
      const payload = {
        user_id: user.user_id,
        quest_id: parseInt(assignQuestData.quest_id),
      };
      await axiosInstance.post("/assign-quest/", payload);
      alert("Quest assigned successfully!");
      fetchUserQuests();
    } catch (error) {
      console.error(
        "Error assigning quest:",
        error.response?.data || error.message
      );
      alert(
        `Assign quest failed: ${error.response?.data.detail || error.message}`
      );
    }
  };

  const fetchUserQuests = async () => {
    if (!user) {
      alert("Please log in first.");
      return;
    }
    try {
      const response = await axiosInstance.get(`/user-quests/${user.user_id}/`);
      setUserQuests(response.data);
    } catch (error) {
      console.error(
        "Error fetching user quests:",
        error.response?.data || error.message
      );
    }
  };

  const completeQuest = async (quest_id) => {
    if (!user) {
      alert("Please log in first.");
      return;
    }
    try {
      const payload = {
        user_id: user.user_id,
        quest_id: quest_id,
      };
      await axiosInstance.post("/complete-quest/", payload);
      alert("Quest completed successfully!");
      fetchUserQuests();
    } catch (error) {
      console.error(
        "Error completing quest:",
        error.response?.data || error.message
      );
      alert(
        `Complete quest failed: ${error.response?.data.detail || error.message}`
      );
    }
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("token");
    setUser(null);
    setUserQuests([]);
    alert("Logged out successfully!");
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-6">
          Gamification Platform Test
        </h1>

        {/* Signup and Login Forms */}
        {!token ? (
          <div className="flex flex-col md:flex-row justify-between mb-8">
            {/* Signup Form */}
            <form
              onSubmit={handleSignup}
              className="bg-white p-6 rounded shadow-md mb-4 md:mb-0 md:mr-4 w-full"
            >
              <h2 className="text-xl font-semibold mb-4">Sign Up</h2>
              <div className="mb-3">
                <label className="block mb-1">Username</label>
                <input
                  type="text"
                  required
                  value={signupData.user_name}
                  onChange={(e) =>
                    setSignupData({ ...signupData, user_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded"
                />
              </div>
              <div className="mb-3">
                <label className="block mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={signupData.password}
                  onChange={(e) =>
                    setSignupData({ ...signupData, password: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded"
                />
              </div>
              <div className="mb-3">
                <label className="block mb-1">Status</label>
                <select
                  value={signupData.status}
                  onChange={(e) =>
                    setSignupData({ ...signupData, status: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded"
                >
                  <option value="new">New</option>
                  <option value="not_new">Not New</option>
                  <option value="banned">Banned</option>
                </select>
              </div>
              <button
                type="submit"
                className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
              >
                Sign Up
              </button>
            </form>

            {/* Login Form */}
            <form
              onSubmit={handleLogin}
              className="bg-white p-6 rounded shadow-md w-full"
            >
              <h2 className="text-xl font-semibold mb-4">Log In</h2>
              <div className="mb-3">
                <label className="block mb-1">Username</label>
                <input
                  type="text"
                  required
                  value={loginData.user_name}
                  onChange={(e) =>
                    setLoginData({ ...loginData, user_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded"
                />
              </div>
              <div className="mb-3">
                <label className="block mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={loginData.password}
                  onChange={(e) =>
                    setLoginData({ ...loginData, password: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-green-500 text-white py-2 rounded hover:bg-green-600"
              >
                Log In
              </button>
            </form>
          </div>
        ) : (
          <div className="mb-8 flex justify-between items-center bg-white p-6 rounded shadow-md">
            <div>
              <h2 className="text-xl font-semibold">
                Welcome, {user?.user_name}!
              </h2>
              <p>
                Gold: {user?.gold} | Diamonds: {user?.diamond} | Status:{" "}
                {user?.status}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Log Out
            </button>
          </div>
        )}

        {/* Quests Section */}
        {token && (
          <div className="bg-white p-6 rounded shadow-md mb-8">
            <h2 className="text-2xl font-semibold mb-4">Available Quests</h2>
            <button
              onClick={fetchQuests}
              className="mb-4 bg-indigo-500 text-white px-4 py-2 rounded hover:bg-indigo-600"
            >
              Fetch Quests
            </button>
            {quests.length > 0 ? (
              <table className="w-full table-auto">
                <thead>
                  <tr className="bg-gray-200">
                    <th className="px-4 py-2">ID</th>
                    <th className="px-4 py-2">Name</th>
                    <th className="px-4 py-2">Description</th>
                    <th className="px-4 py-2">Reward</th>
                  </tr>
                </thead>
                <tbody>
                  {quests.map((quest) => (
                    <tr key={quest.quest_id} className="border-t">
                      <td className="px-4 py-2">{quest.quest_id}</td>
                      <td className="px-4 py-2">{quest.name}</td>
                      <td className="px-4 py-2">{quest.description}</td>
                      <td className="px-4 py-2">
                        {quest.reward_name} - {quest.reward_qty}{" "}
                        {quest.reward_item}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>No quests available. Click "Fetch Quests" to load quests.</p>
            )}
          </div>
        )}

        {/* Assign Quest Section */}
        {token && quests.length > 0 && (
          <div className="bg-white p-6 rounded shadow-md mb-8">
            <h2 className="text-2xl font-semibold mb-4">Assign Quest</h2>
            <form
              onSubmit={assignQuest}
              className="flex flex-col md:flex-row items-center"
            >
              <div className="mb-4 md:mb-0 md:mr-4">
                <label className="block mb-1">Select Quest</label>
                <select
                  required
                  value={assignQuestData.quest_id}
                  onChange={(e) =>
                    setAssignQuestData({
                      ...assignQuestData,
                      quest_id: e.target.value,
                    })
                  }
                  className="px-3 py-2 border rounded w-full"
                >
                  <option value="">-- Select a Quest --</option>
                  {quests.map((quest) => (
                    <option key={quest.quest_id} value={quest.quest_id}>
                      {quest.name}
                    </option>
                  ))}
                </select>
              </div>
              <button
                type="submit"
                className="mt-4 md:mt-0 bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600"
              >
                Assign Quest
              </button>
            </form>
          </div>
        )}

        {/* User Quests Section */}
        {token && (
          <div className="bg-white p-6 rounded shadow-md mb-8">
            <h2 className="text-2xl font-semibold mb-4">Your Quests</h2>
            <button
              onClick={fetchUserQuests}
              className="mb-4 bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
            >
              Fetch Your Quests
            </button>
            {userQuests.length > 0 ? (
              <table className="w-full table-auto">
                <thead>
                  <tr className="bg-gray-200">
                    <th className="px-4 py-2">Quest ID</th>
                    <th className="px-4 py-2">Quest Name</th>
                    <th className="px-4 py-2">Status</th>
                    <th className="px-4 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {userQuests.map((uq) => (
                    <tr
                      key={`${uq.quest_id}-${uq.user_id}`}
                      className="border-t"
                    >
                      <td className="px-4 py-2">{uq.quest_id}</td>
                      <td className="px-4 py-2">{uq.quest_name}</td>
                      <td className="px-4 py-2">{uq.status}</td>
                      <td className="px-4 py-2">
                        {uq.status !== "claimed" && (
                          <button
                            onClick={() => completeQuest(uq.quest_id)}
                            className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600"
                          >
                            Complete Quest
                          </button>
                        )}
                        {uq.status === "claimed" && (
                          <span className="text-green-700 font-semibold">
                            Completed
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>You have no assigned quests. Assign a quest to get started!</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
