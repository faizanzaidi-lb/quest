import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [users, setUsers] = useState([]);
  const [quests, setQuests] = useState([]);
  const [rewards, setRewards] = useState([]);
  const [userName, setUserName] = useState("");
  const [userStatus, setUserStatus] = useState("");
  const [questName, setQuestName] = useState("");
  const [questDescription, setQuestDescription] = useState("");
  const [rewardName, setRewardName] = useState(""); // State for reward name
  const [rewardItem, setRewardItem] = useState(""); // State for reward item
  const [rewardQty, setRewardQty] = useState(1); // State for reward quantity
  const [selectedRewardId, setSelectedRewardId] = useState(""); // To manage selected reward
  const [autoClaim, setAutoClaim] = useState(false);
  const [streak, setStreak] = useState(0);
  const [duplication, setDuplication] = useState(0);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [selectedQuestId, setSelectedQuestId] = useState("");
  const [usersWithQuests, setUsersWithQuests] = useState([]); // State for users with their quests

  // Fetch users, quests, and rewards when component mounts
  useEffect(() => {
    fetchUsers();
    fetchQuests();
    fetchRewards();
    fetchUsersWithQuests();
  }, []);

  const axiosInstance = axios.create({
    baseURL: "http://localhost:8000", // Update with your FastAPI server's base URL
  });

  const fetchUsers = async () => {
    try {
      const response = await axiosInstance.get("/users");
      setUsers(response.data);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  const fetchQuests = async () => {
    try {
      const response = await axiosInstance.get("/quests");
      setQuests(response.data);
    } catch (error) {
      console.error("Error fetching quests:", error);
    }
  };

  const fetchRewards = async () => {
    try {
      const response = await axiosInstance.get("/rewards");
      setRewards(response.data);
    } catch (error) {
      console.error("Error fetching rewards:", error);
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
        reward_id: parseInt(selectedRewardId), // Using selectedRewardId here
        auto_claim: autoClaim,
        streak: parseInt(streak),
        duplication: parseInt(duplication),
        name: questName,
        description: questDescription,
      });
      setQuestName("");
      setQuestDescription("");
      setSelectedRewardId(""); // Reset selected reward ID
      setAutoClaim(false);
      setStreak(0);
      setDuplication(0);
      fetchQuests();
    } catch (error) {
      console.error("Error adding quest:", error);
    }
  };

  const addReward = async () => {
    try {
      await axiosInstance.post("/rewards", {
        reward_name: rewardName, // Send reward name to backend
        reward_item: rewardItem, // Send reward item to backend
        reward_qty: parseInt(rewardQty), // Send reward quantity to backend
      });
      setRewardName(""); // Reset reward name
      setRewardItem(""); // Reset reward item
      setRewardQty(1); // Reset reward quantity
      fetchRewards(); // Fetch rewards to update the list
    } catch (error) {
      console.error("Error adding reward:", error);
    }
  };

  const assignQuestToUser = async () => {
    try {
      await axiosInstance.post("/assign-quest", {
        user_id: parseInt(selectedUserId),
        quest_id: parseInt(selectedQuestId),
        status: "assigned",
      });
      setSelectedUserId("");
      setSelectedQuestId("");
      console.log("Quest assigned successfully");

      // Fetch updated users with quests
      fetchUsersWithQuests(); // Update the state with the latest user data
    } catch (error) {
      console.error("Error assigning quest:", error);
    }
  };

  const fetchUsersWithQuests = async () => {
    try {
      const response = await axiosInstance.get("/users-with-quests");
      setUsersWithQuests(response.data); // Assuming this response includes quests assigned to each user
    } catch (error) {
      console.error("Error fetching users with quests:", error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">
        User, Reward, and Quest Management
      </h1>

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

      {/* Rewards Section */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Rewards</h2>
        <div className="mb-4">
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
            className="bg-green-500 text-white p-2 rounded-md"
          >
            Add Reward
          </button>
        </div>
        {rewards.length > 0 ? (
          <ul className="list-disc pl-5">
            {rewards.map((reward) => (
              <li key={reward.reward_id} className="mb-1">
                {reward.reward_name} (Item: {reward.reward_item}, Quantity:{" "}
                {reward.reward_qty}, ID: {reward.reward_id})
              </li>
            ))}
          </ul>
        ) : (
          <p>No rewards found.</p>
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

          {/* Reward ID Dropdown */}
          <select
            value={selectedRewardId}
            onChange={(e) => setSelectedRewardId(e.target.value)}
            className="border rounded-md p-2 mr-2"
          >
            <option value="">Select Reward</option>
            {rewards.map((reward) => (
              <option key={reward.reward_id} value={reward.reward_id}>
                {reward.reward_name} (ID: {reward.reward_id})
              </option>
            ))}
          </select>

          <label className="mr-2">Auto Claim:</label>
          <input
            type="checkbox"
            checked={autoClaim}
            onChange={(e) => setAutoClaim(e.target.checked)}
          />

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
            className="bg-purple-500 text-white p-2 rounded-md"
          >
            Add Quest
          </button>
        </div>
        {quests.length > 0 ? (
          <ul className="list-disc pl-5">
            {quests.map((quest) => (
              <li key={quest.quest_id} className="mb-1">
                {quest.name} - {quest.description} (Reward ID: {quest.reward_id}
                )
              </li>
            ))}
          </ul>
        ) : (
          <p>No quests found.</p>
        )}
      </div>

      {/* Assign Quest to User Section */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Assign Quest to User</h2>
        <select
          value={selectedUserId}
          onChange={(e) => setSelectedUserId(e.target.value)}
          className="border rounded-md p-2 mr-2"
        >
          <option value="">Select User</option>
          {users.map((user) => (
            <option key={user.user_id} value={user.user_id}>
              {user.user_name} (ID: {user.user_id})
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
            <option key={quest.quest_id} value={quest.quest_id}>
              {quest.name} (ID: {quest.quest_id})
            </option>
          ))}
        </select>
        <button
          onClick={assignQuestToUser}
          className="bg-orange-500 text-white p-2 rounded-md"
        >
          Assign Quest
        </button>
      </div>

      {/* Users with Quests Section */}
      <div className="mt-10">
        <h2 className="text-2xl font-semibold mb-4">Users with Quests</h2>
        {usersWithQuests.length > 0 ? (
          <ul className="list-disc pl-5">
            {usersWithQuests.map((user) => (
              <li key={user.user_id} className="mb-1">
                {user.user_name} (ID: {user.user_id}) - Quests:{" "}
                {user.quests.length > 0 ? (
                  <ul className="list-disc pl-5">
                    {user.quests.map((quest) => (
                      <li key={quest.quest_id}>
                        {quest.name} (ID: {quest.quest_id}, Status:{" "}
                        {quest.status})
                      </li>
                    ))}
                  </ul>
                ) : (
                  "No quests assigned."
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p>No users with quests found.</p>
        )}
      </div>
    </div>
  );
};

export default App;
