import ProfileAvatar from "./ProfileAvatar";

type ProfileBannerProps = {
  name: string;
  email: string;
  imageUrl: string | null;
  uploading: boolean;
  onImageSelected: (file: File) => void;
};

export default function ProfileBanner({
  name,
  email,
  imageUrl,
  uploading,
  onImageSelected,
}: ProfileBannerProps) {
  const memberSince = new Date().getFullYear();

  return (
    <div className="profile-banner">
      <div className="profile-banner-background">
        <div className="profile-banner-decorations">
          <div className="decoration-circle decoration-1" />
          <div className="decoration-circle decoration-2" />
          <div className="decoration-circle decoration-3" />
        </div>
      </div>
      <div className="profile-banner-content">
        <ProfileAvatar
          name={name}
          imageUrl={imageUrl}
          uploading={uploading}
          onImageSelected={onImageSelected}
        />
        <div className="profile-user-info">
          <h1>{name || "User"}</h1>
          <p className="profile-email">{email || "No email set"}</p>
          <div className="profile-status">
            <span className="profile-status-dot" />
            Active
            <span className="profile-status-divider">|</span>
            <span className="profile-status-member">Member since {memberSince}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
