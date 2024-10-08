// src/App.jsx

import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const API_BASE = "http://localhost:8000";
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

  const axiosInstance = axios.create({
    baseURL: API_BASE,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  useEffect(() => {
    if (token) {
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
    <div>
      <h1>Gamification Platform Test</h1>

      {!token ? (
        <div>
          <form onSubmit={handleSignup}>
            <h2>Sign Up</h2>
            <input
              type="text"
              required
              value={signupData.user_name}
              onChange={(e) =>
                setSignupData({ ...signupData, user_name: e.target.value })
              }
              placeholder="Username"
            />
            <input
              type="password"
              required
              value={signupData.password}
              onChange={(e) =>
                setSignupData({ ...signupData, password: e.target.value })
              }
              placeholder="Password"
            />
            <select
              value={signupData.status}
              onChange={(e) =>
                setSignupData({ ...signupData, status: e.target.value })
              }
            >
              <option value="new">New</option>
              <option value="not_new">Not New</option>
              <option value="banned">Banned</option>
            </select>
            <button type="submit">Sign Up</button>
          </form>

          <form onSubmit={handleLogin}>
            <h2>Log In</h2>
            <input
              type="text"
              required
              value={loginData.user_name}
              onChange={(e) =>
                setLoginData({ ...loginData, user_name: e.target.value })
              }
              placeholder="Username"
            />
            <input
              type="password"
              required
              value={loginData.password}
              onChange={(e) =>
                setLoginData({ ...loginData, password: e.target.value })
              }
              placeholder="Password"
            />
            <button type="submit">Log In</button>
          </form>
        </div>
      ) : (
        <div>
          <h2>Welcome, {user?.user_name}!</h2>
          <p>
            Gold: {user?.gold} | Diamonds: {user?.diamond} | Status:{" "}
            {user?.status}
          </p>
          <button onClick={handleLogout}>Log Out</button>
        </div>
      )}

      {token && (
        <div>
          <h2>Available Quests</h2>
          <button onClick={fetchQuests}>Fetch Quests</button>
          {quests.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Reward</th>
                </tr>
              </thead>
              <tbody>
                {quests.map((quest) => (
                  <tr key={quest.quest_id}>
                    <td>{quest.quest_id}</td>
                    <td>{quest.name}</td>
                    <td>{quest.description}</td>
                    <td>
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

      {token && quests.length > 0 && (
        <div>
          <h2>Assign Quest</h2>
          <form onSubmit={assignQuest}>
            <select
              required
              value={assignQuestData.quest_id}
              onChange={(e) =>
                setAssignQuestData({
                  ...assignQuestData,
                  quest_id: e.target.value,
                })
              }
            >
              <option value="">-- Select a Quest --</option>
              {quests.map((quest) => (
                <option key={quest.quest_id} value={quest.quest_id}>
                  {quest.name}
                </option>
              ))}
            </select>
            <button type="submit">Assign Quest</button>
          </form>
        </div>
      )}

      {token && (
        <div>
          <h2>Your Quests</h2>
          <button onClick={fetchUserQuests}>Fetch Your Quests</button>
          {userQuests.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Quest ID</th>
                  <th>Quest Name</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {userQuests.map((uq) => (
                  <tr key={`${uq.quest_id}-${uq.user_id}`}>
                    <td>{uq.quest_id}</td>
                    <td>{uq.quest_name}</td>
                    <td>{uq.status}</td>
                    <td>
                      {uq.status !== "claimed" && (
                        <button onClick={() => completeQuest(uq.quest_id)}>
                          Complete Quest
                        </button>
                      )}
                      {uq.status === "claimed" && <span>Completed</span>}
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
  );
}

export default App;
