import CheckIcon from "../icons/CheckIcon";
import LockIcon from "../icons/LockIcon";
import ShieldIcon from "../icons/ShieldIcon";
import UserIcon from "../icons/UserIcon";

export default function SecurityTips() {
  const tips = [
    {
      icon: <LockIcon />,
      title: "Use strong passwords",
      description:
        "At least 8 characters with uppercase, numbers, and special characters",
    },
    {
      icon: <ShieldIcon />,
      title: "Enable 2FA",
      description: "Add an extra layer of security to your account",
    },
    {
      icon: <CheckIcon />,
      title: "Avoid password reuse",
      description: "Use unique passwords for different services",
    },
    {
      icon: <UserIcon />,
      title: "Review active sessions",
      description: "Check and log out from devices you do not recognize",
    },
  ];

  return (
    <div className="security-tips-card">
      <h3>
        <span className="security-tips-shield">
          <ShieldIcon />
        </span>
        Security Tips
      </h3>
      <ul className="security-tips-list">
        {tips.map((tip) => (
          <li key={tip.title}>
            <span className="tip-icon">{tip.icon}</span>
            <div>
              <div className="tip-title">{tip.title}</div>
              <div className="tip-description">{tip.description}</div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
