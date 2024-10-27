import React from "react";
import { Settings } from "lucide-react";
import styles from "./navbar.module.css";
import { useNavigate } from "react-router-dom";

interface NavbarProps {
  onSettingsClick: () => void;
  redirectTo: string;
  title?: string;
}

const Navbar: React.FC<NavbarProps> = ({
  onSettingsClick,
  redirectTo,
  title,
}) => {
  const navigate = useNavigate();

  return (
    <nav className={styles.navbar}>
      <h1 className={styles.title} onClick={() => navigate(redirectTo)}>
        {title || "Prompt Manager"}
      </h1>
      <button className={styles.settingsButton} onClick={onSettingsClick}>
        <Settings className="h-5 w-5" color="white" />
      </button>
    </nav>
  );
};

export default Navbar;
