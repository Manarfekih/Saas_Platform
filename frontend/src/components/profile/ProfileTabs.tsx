export type ProfileTab = "info" | "security";

type ProfileTabsProps = {
  activeTab: ProfileTab;
  onChange: (tab: ProfileTab) => void;
};

export default function ProfileTabs({ activeTab, onChange }: ProfileTabsProps) {
  return (
    <div className="profile-tabs">
      <button
        id="tab-profile-info"
        type="button"
        className={`profile-tab ${activeTab === "info" ? "active" : ""}`}
        onClick={() => onChange("info")}
      >
        Profile Information
      </button>

      <button
        id="tab-profile-security"
        type="button"
        className={`profile-tab ${activeTab === "security" ? "active" : ""}`}
        onClick={() => onChange("security")}
      >
        Security
      </button>
    </div>
  );
}
