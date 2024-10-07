import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  // State variables
  const [users, setUsers] = useState([]);
  const [quests, setQuests] = useState([]);
  const [rewards, setRewards] = useState([]);
  const [userName, setUserName] = useState("");
  const [userStatus, setUserStatus] = useState("");
  const [questName, setQuestName] = useState("");
  const [questDescription, setQuestDescription] = useState("");
  const [rewardName, setRewardName] = useState("");
  const [rewardItem, setRewardItem] = useState("");
  const [rewardQty, setRewardQty] = useState(1);
  const [selectedRewardId, setSelectedRewardId] = useState("");
  const [autoClaim, setAutoClaim] = useState(false);
  const [streak, setStreak] = useState(0);
  const [duplication, setDuplication] = useState(0);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [selectedQuestId, setSelectedQuestId] = useState("");
  const [usersWithQuests, setUsersWithQuests] = useState([]);
  const [signupUsername, setSignupUsername] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [authToken, setAuthToken] = useState(null);
  const [loggedInUser, setLoggedInUser] = useState(null);

  // Create Axios instance with interceptors to include auth token
  const axiosInstance = axios.create({
    baseURL: "http://localhost:8000", // Corrected API Gateway's base URL
  });

  axiosInstance.interceptors.request.use(
    (config) => {
      if (authToken) {
        config.headers["Authorization"] = `Bearer ${authToken}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Fetch data on component mount
  useEffect(() => {
    if (authToken) {
      fetchCurrentUser(authToken);
    }
    fetchUsers();
    fetchQuests();
    fetchRewards();
    fetchUsersWithQuests();
  }, [authToken]); // Re-fetch data when authToken changes

  // Fetch functions
  const fetchUsers = async () => {
    try {
      const response = await axiosInstance.get("/users/");
      setUsers(response.data);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  const fetchQuests = async () => {
    try {
      const response = await axiosInstance.get("/quests/");
      setQuests(response.data);
    } catch (error) {
      console.error("Error fetching quests:", error);
    }
  };

  const fetchRewards = async () => {
    try {
      const response = await axiosInstance.get("/rewards/");
      setRewards(response.data);
    } catch (error) {
      console.error("Error fetching rewards:", error);
    }
  };

  const fetchUsersWithQuests = async () => {
    try {
      const response = await axiosInstance.get("/users-with-quests");
      setUsersWithQuests(response.data);
    } catch (error) {
      console.error("Error fetching users with quests:", error);
    }
  };

  // Signup function
  const signupUser = async () => {
    try {
      const response = await axiosInstance.post("/register/", {
        username: signupUsername,
        password: signupPassword,
        status: 1, // Default status; adjust as needed
      });
      setSignupUsername("");
      setSignupPassword("");
      console.log("User signed up:", response.data);
      alert("Signup successful! Please log in.");
    } catch (error) {
      console.error("Error signing up user:", error);
      alert("Signup failed: " + error.response?.data?.detail || error.message);
    }
  };

  // Login function
  const loginUser = async () => {
    try {
      const response = await axiosInstance.post("/token", {
        username: loginUsername,
        password: loginPassword,
      });
      setLoginUsername("");
      setLoginPassword("");
      setAuthToken(response.data.access_token);
      console.log("User logged in:", response.data);
      alert("Login successful!");
    } catch (error) {
      console.error("Error logging in user:", error);
      alert("Login failed: " + error.response?.data?.detail || error.message);
    }
  };

  // Fetch current user info
  const fetchCurrentUser = async (token) => {
    try {
      const response = await axiosInstance.get("/users/me/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setLoggedInUser(response.data);
    } catch (error) {
      console.error("Error fetching current user:", error);
    }
  };

  // Add User function
  const addUser = async () => {
    try {
      await axiosInstance.post("/users/", {
        user_name: userName,
        status: parseInt(userStatus),
      });
      setUserName("");
      setUserStatus("");
      fetchUsers();
    } catch (error) {
      console.error("Error adding user:", error);
      alert(
        "Add user failed: " + error.response?.data?.detail || error.message
      );
    }
  };

  // Add Quest function
  const addQuest = async () => {
    try {
      await axiosInstance.post("/quests/", {
        reward_id: selectedRewardId ? parseInt(selectedRewardId) : null,
        auto_claim: autoClaim,
        streak: parseInt(streak),
        duplication: parseInt(duplication),
        name: questName,
        description: questDescription,
      });
      setQuestName("");
      setQuestDescription("");
      setSelectedRewardId("");
      setAutoClaim(false);
      setStreak(0);
      setDuplication(0);
      fetchQuests();
    } catch (error) {
      console.error("Error adding quest:", error);
      alert(
        "Add quest failed: " + error.response?.data?.detail || error.message
      );
    }
  };

  // Add Reward function
  const addReward = async () => {
    try {
      await axiosInstance.post("/rewards/", {
        reward_name: rewardName,
        reward_item: rewardItem,
        reward_qty: parseInt(rewardQty),
      });
      setRewardName("");
      setRewardItem("");
      setRewardQty(1);
      fetchRewards();
    } catch (error) {
      console.error("Error adding reward:", error);
      alert(
        "Add reward failed: " + error.response?.data?.detail || error.message
      );
    }
  };

  // Assign Quest to User function
  const assignQuestToUser = async () => {
    try {
      await axiosInstance.post("/assign-quest/", {
        user_id: parseInt(selectedUserId),
        quest_id: parseInt(selectedQuestId),
        status: "assigned",
      });
      setSelectedUserId("");
      setSelectedQuestId("");
      console.log("Quest assigned successfully");
      alert("Quest assigned successfully!");
      fetchUsersWithQuests();
    } catch (error) {
      console.error("Error assigning quest:", error);
      alert(
        "Assign quest failed: " + error.response?.data?.detail || error.message
      );
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">
        User, Reward, Quest, Signup, and Login Management
      </h1>

      {/* Signup Section */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Signup</h2>
        <input
          type="text"
          value={signupUsername}
          onChange={(e) => setSignupUsername(e.target.value)}
          placeholder="Username"
          className="border rounded-md p-2 mr-2"
        />
        <input
          type="password"
          value={signupPassword}
          onChange={(e) => setSignupPassword(e.target.value)}
          placeholder="Password"
          className="border rounded-md p-2 mr-2"
        />
        <button
          onClick={signupUser}
          className="bg-blue-500 text-white p-2 rounded-md"
        >
          Sign Up
        </button>
      </div>

      {/* Login Section */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Login</h2>
        <input
          type="text"
          value={loginUsername}
          onChange={(e) => setLoginUsername(e.target.value)}
          placeholder="Username"
          className="border rounded-md p-2 mr-2"
        />
        <input
          type="password"
          value={loginPassword}
          onChange={(e) => setLoginPassword(e.target.value)}
          placeholder="Password"
          className="border rounded-md p-2 mr-2"
        />
        <button
          onClick={loginUser}
          className="bg-green-500 text-white p-2 rounded-md"
        >
          Log In
        </button>
      </div>

      {/* User Management Section */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Add User</h2>
        <input
          type="text"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          placeholder="User Name"
          className="border rounded-md p-2 mr-2"
        />
        <input
          type="number"
          value={userStatus}
          onChange={(e) => setUserStatus(e.target.value)}
          placeholder="User Status"
          className="border rounded-md p-2 mr-2"
        />
        <button
          onClick={addUser}
          className="bg-purple-500 text-white p-2 rounded-md"
        >
          Add User
        </button>
      </div>

      {/* Quest Management Section */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Add Quest</h2>
        <input
          type="text"
          value={questName}
          onChange={(e) => setQuestName(e.target.value)}
          placeholder="Quest Name"
          className="border rounded-md p-2 mr-2"
        />
        <input
          type="text"
          value={questDescription}
          onChange={(e) => setQuestDescription(e.target.value)}
          placeholder="Quest Description"
          className="border rounded-md p-2 mr-2"
        />
        <select
          value={selectedRewardId}
          onChange={(e) => setSelectedRewardId(e.target.value)}
          className="border rounded-md p-2 mr-2"
        >
          <option value="">Select Reward</option>
          {rewards.map((reward) => (
            <option key={reward.id} value={reward.id}>
              {reward.reward_name}
            </option>
          ))}
        </select>
        <label className="mr-2">
          Auto Claim:
          <input
            type="checkbox"
            checked={autoClaim}
            onChange={(e) => setAutoClaim(e.target.checked)}
          />
        </label>
        <input
          type="number"
          value={streak}
          onChange={(e) => setStreak(e.target.value)}
          placeholder="Streak"
          className="border rounded-md p-2 mr-2"
        />
        <input
          type="number"
          value={duplication}
          onChange={(e) => setDuplication(e.target.value)}
          placeholder="Duplication"
          className="border rounded-md p-2 mr-2"
        />
        <button
          onClick={addQuest}
          className="bg-blue-500 text-white p-2 rounded-md"
        >
          Add Quest
        </button>
      </div>

      {/* Reward Management Section */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Add Reward</h2>
        <input
          type="text"
          value={rewardName}
          onChange={(e) => setRewardName(e.target.value)}
          placeholder="Reward Name"
          className="border rounded-md p-2 mr-2"
        />
        <input
          type="text"
          value={rewardItem}
          onChange={(e) => setRewardItem(e.target.value)}
          placeholder="Reward Item"
          className="border rounded-md p-2 mr-2"
        />
        <input
          type="number"
          value={rewardQty}
          onChange={(e) => setRewardQty(e.target.value)}
          placeholder="Reward Quantity"
          className="border rounded-md p-2 mr-2"
        />
        <button
          onClick={addReward}
          className="bg-purple-500 text-white p-2 rounded-md"
        >
          Add Reward
        </button>
      </div>

      {/* Assign Quest to User Section */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Assign Quest to User</h2>
        <select
          value={selectedUserId}
          onChange={(e) => setSelectedUserId(e.target.value)}
          className="border rounded-md p-2 mr-2"
        >
          <option value="">Select User</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.user_name}
            </option>
          ))}
        </select>
        <select
          value={selectedQuestId}
          onChange={(e) => setSelectedQuestId(e.target.value)}
          className="border rounded-md p-2 mr-2"
        >
          <option value="">Select Quest</option>
          {quests.map((quest) => (
            <option key={quest.id} value={quest.id}>
              {quest.name}
            </option>
          ))}
        </select>
        <button
          onClick={assignQuestToUser}
          className="bg-green-500 text-white p-2 rounded-md"
        >
          Assign Quest
        </button>
      </div>

      {/* Users with Quests Display Section */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Users with Quests</h2>
        <ul>
          {usersWithQuests.map((userQuest) => (
            <li key={userQuest.user_id}>
              User: {userQuest.user_name} - Quest: {userQuest.quest_name} -
              Status: {userQuest.status}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default App;
