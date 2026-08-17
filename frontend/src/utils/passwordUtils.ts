// src/utils/passwordUtils.ts

export interface PasswordStrength {
  label: string;
  width: string;
  color: string;
  score: number;
}

export function getPasswordStrength(password: string): PasswordStrength {
  if (!password) {
    return { label: "", width: "0%", color: "transparent", score: 0 };
  }

  let score = 0;
  if (password.length >= 8) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/[0-9]/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;

  const strengthMap = [
    { label: "Weak", width: "25%", color: "#F26F4D", score: 1 },
    { label: "Fair", width: "50%", color: "#F3A338", score: 2 },
    { label: "Good", width: "75%", color: "#23BABF", score: 3 },
    { label: "Strong", width: "100%", color: "#47B16A", score: 4 },
  ];

  return strengthMap[Math.min(score - 1, 3)] ?? { label: "", width: "0%", color: "transparent", score: 0 };
}