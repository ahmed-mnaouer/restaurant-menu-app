import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import axios from "axios";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Navigate } from "react-router-dom";
import { isAuthenticated, getUserRole, logout } from "./utils/auth.js";

// Remove this line; data fetching should be handled inside the Menu component.

// --- Components ---
function Navbar() {
  const navigate = useNavigate();
  const loggedIn = isAuthenticated();
  const role = getUserRole();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-gray-800 text-white p-4 flex justify-between items-center">
      <h1 className="text-xl font-bold">🍽️ Restaurant Menu</h1>
      <div className="space-x-4">
        <Link to="/" className="hover:text-yellow-400">
          Home
        </Link>
        {loggedIn && (
          <Link to="/menu" className="hover:text-yellow-400">
            Menu
          </Link>
        )}
        {!loggedIn && (
          <Link to="/login" className="hover:text-yellow-400">
            Login
          </Link>
        )}
        {role === "manager" && (
          <Link to="/dashboard" className="hover:text-yellow-400">
            Dashboard
          </Link>
        )}
        {loggedIn && (
          <button onClick={handleLogout} className="hover:text-yellow-400">
            Logout
          </button>
        )}
      </div>
    </nav>
  );
}

function DishCard({ dish }) {
  return (
    <div className="bg-white rounded-2xl shadow p-4 m-2 w-72">
      <h2 className="text-lg font-semibold mb-2">{dish.name}</h2>
      <p className="text-gray-600 italic mb-1">{dish.variant}</p>
      <p className="text-gray-700">{dish.description}</p>
      <div className="mt-2 flex justify-between items-center">
        <span className="font-bold text-yellow-700">€{dish.price}</span>
        <span className="text-sm text-gray-500">{dish.course}</span>
      </div>
    </div>
  );
}

// --- Pages ---
function Home() {
  return (
    <div className="text-center mt-10">
      <h1 className="text-3xl font-bold mb-4">Bienvenue au Restaurant !</h1>
      <p className="text-gray-600 text-lg">
        Explorez notre menu authentique et savoureux.
      </p>
    </div>
  );
}

function Menu() {
  const [menu, setMenu] = React.useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/menu")
      .then((res) => {
        const data = res.data || {};
        if (data.starters || data.main_courses || data.desserts) {
          setMenu([
            ...(data.starters || []),
            ...(data.main_courses || []),
            ...(data.desserts || []),
          ]);
        } else if (Array.isArray(data)) {
          setMenu(data);
        } else if (data.menu) {
          setMenu(data.menu);
        } else {
          setMenu([]);
        }
      })
      .catch((err) => console.error("Error fetching menu:", err));
  }, []);

  if (!menu.length)
    return (
      <p className="text-center mt-10 text-gray-600">Chargement du menu...</p>
    );

  return (
    <div className="p-6">
      <h2 className="text-3xl font-bold text-center mb-6">Notre Menu</h2>

      {/* Entrées */}
      <section className="mb-10">
        <h3 className="text-2xl font-semibold mb-4 text-yellow-700">Entrées</h3>
        <div className="flex flex-wrap justify-center gap-4">
          {menu
            .filter((dish) => dish.course === "Entrée")
            .map((dish) => (
              <DishCard key={dish.id} dish={dish} />
            ))}
        </div>
      </section>

      {/* Plats */}
      <section className="mb-10">
        <h3 className="text-2xl font-semibold mb-4 text-yellow-700">Plats</h3>
        <div className="flex flex-wrap justify-center gap-4">
          {menu
            .filter((dish) => dish.course === "Plat")
            .map((dish) => (
              <DishCard key={dish.id} dish={dish} />
            ))}
        </div>
      </section>

      {/* Desserts */}
      <section>
        <h3 className="text-2xl font-semibold mb-4 text-yellow-700">
          Desserts
        </h3>
        <div className="flex flex-wrap justify-center gap-4">
          {menu
            .filter((dish) => dish.course === "Dessert")
            .map((dish) => (
              <DishCard key={dish.id} dish={dish} />
            ))}
        </div>
      </section>
    </div>
  );
}

function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [role, setRole] = useState("customer");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const endpoint = isRegister
      ? "http://127.0.0.1:5000/register"
      : "http://127.0.0.1:5000/login";

    try {
      const res = await axios.post(endpoint, {
        username,
        password,
        role,
      });

      if (isRegister) {
        setMessage(
          "✅ Inscription réussie ! Vous pouvez maintenant vous connecter."
        );
        setIsRegister(false);
      } else {
        const token = res.data.access_token;
        const user = res.data.user;
        localStorage.setItem("token", token);
        localStorage.setItem("role", user.role);
        localStorage.setItem("username", user.username);
        setMessage("✅ Connexion réussie !");

        // Redirect
        if (user.role === "manager") {
          navigate("/dashboard");
        } else {
          navigate("/menu");
        }
      }
    } catch (err) {
      setMessage(
        "❌ " + (err.response?.data?.message || "Erreur de connexion")
      );
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white shadow rounded-2xl">
      <h2 className="text-2xl font-bold mb-4 text-center">
        {isRegister ? "Créer un compte" : "Connexion"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Nom d'utilisateur"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />

        {isRegister && (
          <div className="flex justify-around text-gray-700">
            <label>
              <input
                type="radio"
                value="customer"
                checked={role === "customer"}
                onChange={() => setRole("customer")}
              />{" "}
              Client
            </label>
            <label>
              <input
                type="radio"
                value="manager"
                checked={role === "manager"}
                onChange={() => setRole("manager")}
              />{" "}
              Manager
            </label>
          </div>
        )}

        <button
          type="submit"
          className="w-full bg-yellow-600 text-white py-2 rounded hover:bg-yellow-700"
        >
          {isRegister ? "S'inscrire" : "Se connecter"}
        </button>
      </form>

      <p
        className="text-sm text-center text-blue-600 mt-3 cursor-pointer"
        onClick={() => {
          setIsRegister(!isRegister);
          setMessage("");
        }}
      >
        {isRegister ? "Déjà un compte ? Connectez-vous" : "Créer un compte"}
      </p>

      {message && (
        <p className="text-center mt-4 text-gray-700 font-medium">{message}</p>
      )}
    </div>
  );
}

function Dashboard() {
  const [menu, setMenu] = useState([]);
  const [editingDish, setEditingDish] = useState(null);
  const [form, setForm] = useState({
    name: "",
    variant: "",
    course: "Entrée",
    price: "",
    description: "",
    calories: "",
    country_origin: "",
    availability: "Disponible",
  });

  const token = localStorage.getItem("token");

  // Fetch dishes
  const fetchMenu = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5000/menu");
      const all = [
        ...res.data.starters,
        ...res.data.main_courses,
        ...res.data.desserts,
      ];
      setMenu(all);
    } catch (err) {
      console.error("Error fetching menu:", err);
    }
  };

  useEffect(() => {
    fetchMenu();
  }, []);

  // Handle form input
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Add or update dish
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingDish) {
        await axios.put(
          `http://127.0.0.1:5000/update_dish/${editingDish.id}`,
          form,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setEditingDish(null);
      } else {
        await axios.post("http://127.0.0.1:5000/add_dish", form, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }
      setForm({
        name: "",
        variant: "",
        course: "Entrée",
        price: "",
        description: "",
        calories: "",
        country_origin: "",
        availability: "Disponible",
      });
      fetchMenu();
    } catch (err) {
      console.error("Error saving dish:", err);
      alert("⚠️ Unauthorized or invalid data");
    }
  };

  // Edit dish
  const handleEdit = (dish) => {
    setEditingDish(dish);
    setForm(dish);
  };

  // Delete dish
  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer ce plat ?")) return;
    try {
      await axios.delete(`http://127.0.0.1:5000/delete_dish/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchMenu();
    } catch (err) {
      console.error("Error deleting dish:", err);
      alert("⚠️ Unauthorized or error deleting");
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4 text-center">
        Panneau de Gestion du Menu
      </h2>

      {/* Form */}
      <form
        onSubmit={handleSubmit}
        className="max-w-3xl mx-auto bg-white p-4 rounded-2xl shadow mb-10"
      >
        <div className="grid grid-cols-2 gap-4">
          <input
            name="name"
            placeholder="Nom du plat"
            value={form.name}
            onChange={handleChange}
            className="border p-2 rounded"
            required
          />
          <input
            name="variant"
            placeholder="Variante"
            value={form.variant}
            onChange={handleChange}
            className="border p-2 rounded"
          />
          <select
            name="course"
            value={form.course}
            onChange={handleChange}
            className="border p-2 rounded"
          >
            <option>Entrée</option>
            <option>Plat</option>
            <option>Dessert</option>
          </select>
          <input
            type="number"
            name="price"
            placeholder="Prix (€)"
            value={form.price}
            onChange={handleChange}
            className="border p-2 rounded"
          />
          <input
            name="country_origin"
            placeholder="Origine"
            value={form.country_origin}
            onChange={handleChange}
            className="border p-2 rounded"
          />
          <input
            type="number"
            name="calories"
            placeholder="Calories"
            value={form.calories}
            onChange={handleChange}
            className="border p-2 rounded"
          />
          <select
            name="availability"
            value={form.availability}
            onChange={handleChange}
            className="border p-2 rounded"
          >
            <option>Disponible</option>
            <option>Épuisé</option>
            <option>Non disponible</option>
          </select>
        </div>

        <textarea
          name="description"
          placeholder="Description"
          value={form.description}
          onChange={handleChange}
          className="border p-2 rounded w-full mt-4"
        />

        <button
          type="submit"
          className="bg-yellow-600 text-white px-4 py-2 rounded mt-4 hover:bg-yellow-700"
        >
          {editingDish ? "Mettre à jour le plat" : "Ajouter un plat"}
        </button>
      </form>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-xl shadow">
          <thead>
            <tr className="bg-gray-200 text-left">
              <th className="p-2">ID</th>
              <th className="p-2">Nom</th>
              <th className="p-2">Variante</th>
              <th className="p-2">Type</th>
              <th className="p-2">Prix (€)</th>
              <th className="p-2">Disponibilité</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {menu.map((dish) => (
              <tr key={dish.id} className="border-t">
                <td className="p-2">{dish.id}</td>
                <td className="p-2">{dish.name}</td>
                <td className="p-2">{dish.variant}</td>
                <td className="p-2">{dish.course}</td>
                <td className="p-2">{dish.price}</td>
                <td className="p-2">{dish.availability}</td>
                <td className="p-2 space-x-2">
                  <button
                    onClick={() => handleEdit(dish)}
                    className="text-blue-600 hover:underline"
                  >
                    Modifier
                  </button>
                  <button
                    onClick={() => handleDelete(dish.id)}
                    className="text-red-600 hover:underline"
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// --- App Router ---

export const PrivateRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to="/login" replace />;
};

export const ManagerRoute = ({ children }) => {
  return isAuthenticated() && getUserRole() === "manager" ? (
    children
  ) : (
    <Navigate to="/login" replace />
  );
};

export default function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route
          path="/menu"
          element={
            <PrivateRoute>
              <Menu />
            </PrivateRoute>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ManagerRoute>
              <Dashboard />
            </ManagerRoute>
          }
        />
      </Routes>
    </Router>
  );
}
