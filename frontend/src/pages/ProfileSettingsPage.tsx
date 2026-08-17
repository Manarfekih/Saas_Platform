import { useEffect, useState, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/auth";
import { useAuth } from "../context/AuthContext";
import PasswordForm from "../components/profile/PasswordForm";
import ProfileBanner from "../components/profile/ProfileBanner";
import ProfileInfoForm from "../components/profile/ProfileInfoForm";
import ProfileTabs, { type ProfileTab } from "../components/profile/ProfileTabs";
import SecurityTips from "../components/profile/SecurityTips";
import Toast from "../components/profile/Toast";
import { getPasswordStrength } from "../utils/passwordUtils";
import "../styles/profile.css";

export default function ProfileSettingsPage() {
  const navigate = useNavigate();
  const { token, userEmail, userName, profileImage: authProfileImage, refreshUser, logout } = useAuth();

  // State
  const [activeTab, setActiveTab] = useState<ProfileTab>("info");
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [profileImage, setProfileImage] = useState<string | null>(authProfileImage ?? null);
  const [uploadingImage, setUploadingImage] = useState(false);

  const [name, setName] = useState(userName ?? "");
  const [email, setEmail] = useState(userEmail ?? "");
  const [infoLoading, setInfoLoading] = useState(false);

  const [currentPwd, setCurrentPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [secLoading, setSecLoading] = useState(false);

  
  

  const authHeaders = useMemo(() => 
    token ? { Authorization: `Bearer ${token}` } : null,
    [token]
  );

  // Sync profile image with auth context
  useEffect(() => {
    setProfileImage(authProfileImage ?? null);
  }, [authProfileImage]);

  // Auto-dismiss toast
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(null), 3500);
    return () => clearTimeout(timer);
  }, [toast]);

  // Handlers
  const showToast = useCallback((type: "success" | "error", message: string) => {
    setToast({ type, message });
  }, []);

  const handleInfoSave = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authHeaders) return;

    setInfoLoading(true);
    try {
      const { data } = await api.put(
        "/auth/me",
        { name, email },
        { headers: authHeaders }
      );

      setName(data.name);
      setEmail(data.email);
      await refreshUser();
      showToast("success", "Profile updated successfully.");
    } catch (error: any) {
      const msg = error?.response?.data?.detail ?? "Failed to update profile.";
      showToast("error", msg);
    } finally {
      setInfoLoading(false);
    }
  }, [authHeaders, name, email, refreshUser, showToast]);

  const handleImageUpload = useCallback(async (file: File) => {
    if (!authHeaders) return;

    setUploadingImage(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const { data } = await api.post("/auth/me/profile-image", formData, {
        headers: authHeaders,
      });

      setProfileImage(data.profile_image ?? null);
      await refreshUser();
      showToast("success", "Profile image updated.");
    } catch (error: any) {
      const msg = error?.response?.data?.detail ?? "Failed to upload image.";
      showToast("error", msg);
    } finally {
      setUploadingImage(false);
    }
  }, [authHeaders, refreshUser, showToast]);

  const handlePasswordSave = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authHeaders) return;

    // Validation
    if (newPwd !== confirmPwd) {
      showToast("error", "New passwords do not match.");
      return;
    }
    if (newPwd.length < 8) {
      showToast("error", "Password must be at least 8 characters.");
      return;
    }

    setSecLoading(true);
    try {
      await api.put(
        "/auth/me",
        { current_password: currentPwd, new_password: newPwd },
        { headers: authHeaders }
      );

      showToast("success", "Password changed successfully.");
      setCurrentPwd("");
      setNewPwd("");
      setConfirmPwd("");
    } catch (error: any) {
      const msg = error?.response?.data?.detail ?? "Failed to change password.";
      showToast("error", msg);
    } finally {
      setSecLoading(false);
    }
  }, [authHeaders, currentPwd, newPwd, confirmPwd, showToast]);

  const resetForm = useCallback(() => {
    setName(userName ?? "");
    setEmail(userEmail ?? "");
  }, [userName, userEmail]);

  const clearPasswordForm = useCallback(() => {
    setCurrentPwd("");
    setNewPwd("");
    setConfirmPwd("");
  }, []);

  const handleSignOut = useCallback(() => {
    logout();
    navigate("/login", { replace: true });
  }, [logout, navigate]);

  const pwdStrength = useMemo(() => 
    getPasswordStrength(newPwd), 
    [newPwd]
  );

  return (
    <div className="profile-settings-page">
      <div className="profile-settings-container">
        {/* Banner */}
        <ProfileBanner
          name={name}
          email={email}
          imageUrl={profileImage}
          uploading={uploadingImage}
          onImageSelected={handleImageUpload}
        />

        {/* Tabs */}
        <ProfileTabs activeTab={activeTab} onChange={setActiveTab} />

        {/* Tab Content */}
        <div className="profile-tab-content">
          {activeTab === "info" && (
            <>
              <ProfileInfoForm
                name={name}
                email={email}
                loading={infoLoading}
                onNameChange={setName}
                onEmailChange={setEmail}
                onSubmit={handleInfoSave}
                onReset={resetForm}
              />
              
            </>
          )}

          {activeTab === "security" && (
            <div className="profile-security-section">
              <PasswordForm
                currentPwd={currentPwd}
                newPwd={newPwd}
                confirmPwd={confirmPwd}
                loading={secLoading}
                pwdStrength={pwdStrength}
                onCurrentChange={setCurrentPwd}
                onNewChange={setNewPwd}
                onConfirmChange={setConfirmPwd}
                onSubmit={handlePasswordSave}
                onClear={clearPasswordForm}
              />
              <SecurityTips />
            </div>
          )}
        </div>
      </div>

      <div style={{ maxWidth: "900px", margin: "24px auto 0", padding: "0 24px", display: "flex", justifyContent: "flex-end" }}>
        <button
          id="profile-signout-btn"
          type="button"
          onClick={handleSignOut}
          className="btn-itgate btn-itgate-sm"
          style={{ gap: "7px" }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="14"
            height="14"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
            />
          </svg>

          Sign Out
        </button>
      </div>

      {/* Toast Notification */}
      {toast && <Toast type={toast.type} message={toast.message} />}
    </div>
  );
}



