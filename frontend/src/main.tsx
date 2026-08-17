import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/delete-modal.css";


import "./index.css";
import "./styles/profile.css";

import {
  AuthProvider,
} from "./context/AuthContext";

ReactDOM.createRoot(
  document.getElementById("root")!
).render(
  <AuthProvider>
    <App />
  </AuthProvider>
);
