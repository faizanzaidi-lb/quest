import React, { useState } from "react";
import Signup from "./Signup";
import Login from "./Login";
import QuestStatus from "./QuestStatus";

const App = () => {
  const [userId, setUserId] = useState(null);

  const handleLogin = (id) => {
    setUserId(id);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100">
      <h1 className="text-4xl font-bold mb-8">Quest Management</h1>
      {!userId ? (
        <>
          <Signup onUserIdSet={handleLogin} />
          <Login onUserIdSet={handleLogin} />
        </>
      ) : (
        <QuestStatus userId={userId} />
      )}
    </div>
  );
};

export default App;
