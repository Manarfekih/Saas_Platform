// src/components/profile/ProfileAvatar.tsx

import { useRef, type ChangeEvent } from "react";
import api from "../../api/auth";

type ProfileAvatarProps = {
  name: string;
  imageUrl?: string | null;
  uploading?: boolean;
  onImageSelected: (file: File) => void;
};

function resolveImageSrc(imageUrl?: string | null) {
  if (!imageUrl) return null;
  if (imageUrl.startsWith("http")) return imageUrl;
  
  const normalizedPath = imageUrl.startsWith("/") ? imageUrl : `/${imageUrl}`;
  const baseURL = api.defaults.baseURL?.replace(/\/api$/, "") ?? "http://localhost:8000";
  return `${baseURL}${normalizedPath}`;
}

export default function ProfileAvatar({
  name,
  imageUrl,
  uploading = false,
  onImageSelected,
}: ProfileAvatarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const imageSrc = resolveImageSrc(imageUrl);

  const initials = name
    ? name
        .split(" ")
        .map((word) => word[0]?.toUpperCase())
        .slice(0, 2)
        .join("")
    : "?";

  const handleChooseImage = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    onImageSelected(file);
    e.target.value = "";
  };

  return (
    <div className="profile-avatar-wrapper">
      {imageSrc ? (
        <img 
          src={imageSrc} 
          alt={name || "User avatar"} 
          className="profile-avatar-image" 
        />
      ) : (
        <div className="profile-avatar-initials">{initials}</div>
      )}

      <button
        type="button"
        className="profile-avatar-edit"
        onClick={handleChooseImage}
        disabled={uploading}
        aria-label="Change profile picture"
      >
        {uploading ? (
          <span className="avatar-upload-spinner"></span>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
            <circle cx="12" cy="13" r="4" />
          </svg>
        )}
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        hidden
        onChange={handleFileChange}
      />
    </div>
  );
}