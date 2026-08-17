import CheckIcon from "../icons/CheckIcon";
import XIcon from "../icons/XIcon";

type ToastProps = {
  type: "success" | "error";
  message: string;
};

export default function Toast({ type, message }: ToastProps) {
  return (
    <div className={`profile-toast ${type}`}>
      <span className="profile-toast-icon">
        {type === "success" ? <CheckIcon /> : <XIcon />}
      </span>
      {message}
    </div>
  );
}
