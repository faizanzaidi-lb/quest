import React, { useEffect, useState } from "react";
import axios from "axios";

const QuestProgress = ({ userId }) => {
  const [quests, setQuests] = useState([]);

  useEffect(() => {
    const fetchQuests = async () => {
      if (!userId) return; // Avoid fetching if userId is not available
      try {
        const response = await axios.get(
          `http://localhost:8003/user-quests/${userId}`
        );
        setQuests(response.data);
      } catch (error) {
        console.error("Error fetching quest progress:", error);
      }
    };

    fetchQuests();
  }, [userId]);
  console.log(quests, "quests");

  return (
    <div className="mt-6 p-4 border rounded-lg shadow-lg bg-white">
      <h2 className="text-2xl font-semibold mb-4">Quest Progress</h2>
      <ul className="space-y-2">
        {quests.length > 0 ? (
          quests.map((quest) => (
            <li key={quest.quest_id} className="p-2 border-b last:border-b-0">
              <span className="font-medium">{quest.name}</span>:{" "}
              {quest.progress}/{quest.streak} - Status: {quest.status}
            </li>
          ))
        ) : (
          <li className="text-gray-500">No quests found.</li>
        )}
      </ul>
    </div>
  );
};

export default QuestProgress;
