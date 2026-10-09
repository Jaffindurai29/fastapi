import { useEffect, useState } from "react";
import api, { errorText } from "../api";
import { useAuth } from "../auth";

export default function AdminUsersPage() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState([]);
  const [notice, setNotice] = useState(null);

  function load() {
    api.get("/users").then((res) => setUsers(res.data));
  }

  useEffect(load, []);

  async function changeRole(user, role) {
    setNotice(null);
    try {
      await api.patch(`/users/${user.id}/role`, { role });
      load();
    } catch (err) {
      setNotice({ type: "error", text: errorText(err) });
    }
  }

  return (
    <section>
      <h2>Users</h2>
      {notice && <div className={`alert ${notice.type}`}>{notice.text}</div>}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Id (hashed)</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>
                  {u.username}
                  {u.id === me.id && <span className="muted"> (you)</span>}
                </td>
                <td className="muted">{u.id}</td>
                <td>
                  {/* You can't change your own role: the backend refuses too. */}
                  <select
                    value={u.role}
                    disabled={u.id === me.id}
                    onChange={(e) => changeRole(u, e.target.value)}
                  >
                    <option value="customer">customer</option>
                    <option value="admin">admin</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
