import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";

import DashboardPage from "../pages/DashboardPage";
import DocumentsPage from "../pages/DocumentsPage";
import UploadPage from "../pages/UploadPage";
import DocumentDetailsPage from "../pages/DocumentDetailsPage";
import ChatPage from "../pages/ChatPage";
import GlobalChatPage from "../pages/GlobalChatPage";


import Layout from "../components/Layout";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public */}
        <Route
          path="/login"
          element={<LoginPage />}
        />

        <Route
          path="/register"
          element={<RegisterPage />}
        />

        {/* Protected */}
        <Route element={<Layout />}>

          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/documents"
            element={<DocumentsPage />}
          />

          <Route
            path="/documents/:id"
            element={<DocumentDetailsPage />}
          />

          <Route
            path="/chat/all"
            element={<GlobalChatPage />}
          />
          <Route
            path="/upload"
            element={<UploadPage />}
          />

          <Route
            path="/chat/:document_id"
            element={<ChatPage />}
          />

        </Route>

        <Route
          path="/"
          element={<Navigate to="/dashboard" />}
        />

      </Routes>
    </BrowserRouter>
  );
}