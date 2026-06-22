import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={<LoginPage />}
        />

        <Route
          path="/register"
          element={<RegisterPage />}
        />
      </Routes>
    </BrowserRouter>
  );
}