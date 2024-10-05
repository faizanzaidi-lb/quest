import React from "react";

const UserList = ({ users }) => {
  return (
    <div className="mt-6 p-4 border rounded-lg shadow-lg bg-white">
      <h2 className="text-2xl font-semibold mb-4">User List</h2>
      <ul className="space-y-2">
        {users.length > 0 ? (
          users.map((user) => (
            <li key={user.user_id} className="p-2 border-b last:border-b-0">
              <span className="font-medium text-lg mr-6">{user.user_id}</span>
              <span className="font-medium text-lg">{user.username}</span>
            </li>
          ))
        ) : (
          <li className="text-gray-500">No users found.</li>
        )}
      </ul>
    </div>
  );
};

export default UserList;
