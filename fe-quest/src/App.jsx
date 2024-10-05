import React, { useEffect, useState } from "react";
import Register from "./components/Register";
import Login from "./components/Login";
import UserList from "./components/UserList";
import QuestProgress from "./components/QuestProgress";
import ClaimReward from "./components/ClaimReward";
import axios from "axios";

const App = () => {
  const [users, setUsers] = useState([]);
  const [userId, setUserId] = useState(null);

  const fetchUsers = async () => {
    try {
      const response = await axios.get("http://localhost:8001/users");
      setUsers(response.data);
    } catch (error) {
      console.error("Error fetching users", error);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleUserAdded = () => {
    fetchUsers(); // Fetch the updated user list
  };

  const handleLogin = (id) => {
    setUserId(id); // Set the logged-in user ID
  };

  const handleLogout = async () => {
    const payload = { user_id: userId };
    console.log("Logging out with payload:", payload); // Log the payload
    try {
      await axios.post("http://localhost:8001/logout", payload);
      setUserId(null); // Clear the user ID
      alert("Logged out successfully");
    } catch (error) {
      console.error("Error logging out", error.response?.data || error);
      alert("Logout failed");
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">User Authentication</h1>

      <div className="flex flex-col md:flex-row justify-between space-y-4 md:space-y-0">
        <div className="w-full md:w-1/2 p-4 border rounded-lg shadow-lg bg-white">
          <Register onUserAdded={handleUserAdded} />
        </div>

        <div className="w-full md:w-1/2 p-4 border rounded-lg shadow-lg bg-white">
          <Login onLogin={handleLogin} />
        </div>
      </div>

      {userId ? ( // Show if user is logged in
        <div>
          <button
            onClick={handleLogout}
            className="mt-4 p-2 bg-red-500 text-white rounded"
          >
            Logout
          </button>
          <QuestProgress userId={userId} />
          <ClaimReward userId={userId} />
        </div>
      ) : null}

      <div className="mt-6 p-4 border rounded-lg shadow-lg bg-white">
        <UserList users={users} />
      </div>
    </div>
  );
};

export default App;
