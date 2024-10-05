import React, { useState } from "react";
import axios from "axios";

const ClaimReward = ({ userId }) => {
  const [questId, setQuestId] = useState("");
  const [loading, setLoading] = useState(false);

  const handleClaim = async () => {
    if (!questId) return alert("Please enter a Quest ID");

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:8003/claim-reward/", {
        user_id: userId,
        quest_id: questId,
      });
      alert(response.data.message);
      setQuestId(""); // Reset quest ID after claiming
    } catch (error) {
      alert(error.response?.data?.detail || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-6 p-4 border rounded-lg shadow-lg bg-white">
      <h2 className="text-2xl font-semibold mb-4">Claim Reward</h2>
      <input
        type="number"
        value={questId}
        onChange={(e) => setQuestId(e.target.value)}
        placeholder="Quest ID"
        className="border border-gray-300 p-2 rounded-lg mb-4 w-full focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
      <button
        onClick={handleClaim}
        disabled={loading}
        className={`bg-blue-500 text-white p-2 rounded-lg w-full ${
          loading ? "opacity-50 cursor-not-allowed" : "hover:bg-blue-600"
        } transition`}
      >
        {loading ? "Claiming..." : "Claim Reward"}
      </button>
    </div>
  );
};

export default ClaimReward;
