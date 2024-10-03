import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [users, setUsers] = useState([]);
  const [quests, setQuests] = useState([]);
  const [questsWithRewards, setQuestsWithRewards] = useState([]); // New state for quests with rewards
  const [userName, setUserName] = useState("");
  const [userStatus, setUserStatus] = useState("");
  const [questName, setQuestName] = useState("");
  const [questDescription, setQuestDescription] = useState("");
  const [rewardId, setRewardId] = useState("");
  const [autoClaim, setAutoClaim] = useState(false);
  const [streak, setStreak] = useState(0);
  const [duplication, setDuplication] = useState(0);

  // Fetch users, quests, and quests with rewards when component mounts
  useEffect(() => {
    fetchUsers();
    fetchQuests();
    fetchQuestsWithRewards(); // Fetch quests with rewards
  }, []);

  const axiosInstance = axios.create({
    baseURL: "http://localhost:8000", // Update with your FastAPI server's base URL
  });

  const fetchUsers = async () => {
    try {
      const response = await axiosInstance.get("/users");
      if (Array.isArray(response.data)) {
        setUsers(response.data);
      } else {
        console.error("Unexpected response format:", response.data);
      }
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  const fetchQuests = async () => {
    try {
      const response = await axiosInstance.get("/quests");
      if (Array.isArray(response.data)) {
        setQuests(response.data);
      } else {
        console.error("Unexpected response format:", response.data);
      }
    } catch (error) {
      console.error("Error fetching quests:", error);
    }
  };

  const fetchQuestsWithRewards = async () => {
    try {
      const response = await axiosInstance.get("/quests-with-rewards"); // Fetch quests with rewards
      if (Array.isArray(response.data)) {
        setQuestsWithRewards(response.data);
      } else {
        console.error("Unexpected response format:", response.data);
      }
    } catch (error) {
      console.error("Error fetching quests with rewards:", error);
    }
  };

  const addUser = async () => {
    try {
      await axiosInstance.post("/users", {
        user_name: userName,
        status: parseInt(userStatus),
      });
      setUserName("");
      setUserStatus("");
      fetchUsers();
    } catch (error) {
      console.error("Error adding user:", error);
    }
  };

  const addQuest = async () => {
    try {
      await axiosInstance.post("/quests", {
        reward_id: parseInt(rewardId),
        auto_claim: autoClaim,
        streak: parseInt(streak),
        duplication: parseInt(duplication),
        name: questName,
        description: questDescription,
      });
      setQuestName("");
      setQuestDescription("");
      setRewardId("");
      setAutoClaim(false);
      setStreak(0);
      setDuplication(0);
      fetchQuests();
      fetchQuestsWithRewards(); // Re-fetch quests with rewards after adding a new quest
    } catch (error) {
      console.error("Error adding quest:", error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">User and Quest Management</h1>

      {/* Users Section */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Users</h2>
        <div className="mb-4">
          <input
            type="text"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            placeholder="User Name"
            className="border rounded-md p-2 mr-2"
          />
          <input
            type="text"
            value={userStatus}
            onChange={(e) => setUserStatus(e.target.value)}
            placeholder="User Status"
            className="border rounded-md p-2 mr-2"
          />
          <button
            onClick={addUser}
            className="bg-blue-500 text-white p-2 rounded-md"
          >
            Add User
          </button>
        </div>
        {users.length > 0 ? (
          <ul className="list-disc pl-5">
            {users.map((user) => (
              <li key={user.user_id} className="mb-1">
                {user.user_name} (Status: {user.status})
              </li>
            ))}
          </ul>
        ) : (
          <p>No users found.</p>
        )}
      </div>

      {/* Quests Section */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Quests</h2>
        <div className="mb-4">
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
          <input
            type="text"
            value={rewardId}
            onChange={(e) => setRewardId(e.target.value)}
            placeholder="Reward ID"
            className="border rounded-md p-2 mr-2"
          />
          <input
            type="checkbox"
            checked={autoClaim}
            onChange={(e) => setAutoClaim(e.target.checked)}
            className="mr-2"
          />
          <label className="mr-4">Auto Claim</label>
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
            className="bg-green-500 text-white p-2 rounded-md"
          >
            Add Quest
          </button>
        </div>
        {quests.length > 0 ? (
          <ul className="list-disc pl-5">
            {quests.map((quest) => (
              <li key={quest.quest_id} className="mb-1">
                {quest.name} (Description: {quest.description})
              </li>
            ))}
          </ul>
        ) : (
          <p>No quests found.</p>
        )}
      </div>

      {/* Quests with Rewards Section */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Quests with Rewards</h2>
        {questsWithRewards.length > 0 ? (
          <table className="min-w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-2">Quest Name</th>
                <th className="border border-gray-300 p-2">Description</th>
                <th className="border border-gray-300 p-2">Reward Name</th>
                <th className="border border-gray-300 p-2">Reward Item</th>
                <th className="border border-gray-300 p-2">Reward Quantity</th>
              </tr>
            </thead>
            <tbody>
              {questsWithRewards.map((quest) => (
                <tr key={quest.quest_id}>
                  <td className="border border-gray-300 p-2">{quest.name}</td>
                  <td className="border border-gray-300 p-2">
                    {quest.description}
                  </td>
                  <td className="border border-gray-300 p-2">
                    {quest.reward_name}
                  </td>
                  <td className="border border-gray-300 p-2">
                    {quest.reward_item}
                  </td>
                  <td className="border border-gray-300 p-2">
                    {quest.reward_qty}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No quests with rewards found.</p>
        )}
      </div>
    </div>
  );
};

export default App;
