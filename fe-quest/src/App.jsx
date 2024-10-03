import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [users, setUsers] = useState([]);
  const [quests, setQuests] = useState([]);
  const [userName, setUserName] = useState("");
  const [userStatus, setUserStatus] = useState("");
  const [questName, setQuestName] = useState("");
  const [questDescription, setQuestDescription] = useState("");
  const [rewardId, setRewardId] = useState("");
  const [autoClaim, setAutoClaim] = useState(false);
  const [streak, setStreak] = useState(0);
  const [duplication, setDuplication] = useState(0);

  // Fetch users and quests when component mounts
  useEffect(() => {
    fetchUsers();
    fetchQuests();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get("/users"); // Update with your API endpoint URL
      setUsers(response.data);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  const fetchQuests = async () => {
    try {
      const response = await axios.get("/quests"); // Update with your API endpoint URL
      setQuests(response.data);
    } catch (error) {
      console.error("Error fetching quests:", error);
    }
  };

  const addUser = async () => {
    try {
      await axios.post("/users", {
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
      await axios.post("/quests", {
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
        <ul className="list-disc pl-5">
          {users.map((user) => (
            <li key={user.user_id} className="mb-1">
              {user.user_name} (Status: {user.status})
            </li>
          ))}
        </ul>
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
        <ul className="list-disc pl-5">
          {quests.map((quest) => (
            <li key={quest.quest_id} className="mb-1">
              {quest.name} (Description: {quest.description})
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default App;
