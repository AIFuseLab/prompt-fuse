import React, { useState } from 'react';
import styles from './settings.module.css'; // Make sure to create and import the appropriate CSS module
import LLMList from './llm-list'; // Adjust the import path as needed

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

const Settings: React.FC<SettingsProps> = ({ isOpen, onClose }) => {
  const [selectedOption, setSelectedOption] = useState<string>("Add LLM");

  if (!isOpen) return null;

  return (
    <div className={styles.modal}>
      <div className={styles.modalContent}>
        <div className={styles.modalNavbar}>
          <h2 className={styles.modalTitle}>Settings</h2>
          <button
            onClick={onClose}
            className={styles.closeButton}
          >
            x
          </button>
        </div>
        <div className={styles.modalBody}>
          <div className={styles.sidebar}>
            <button
              className={`${styles.sidebarItem} ${
                selectedOption === "Add LLM" ? styles.selectedItem : ""
              }`}
              onClick={() => setSelectedOption("Add LLM")}
            >
              Add LLM
            </button>
            <button
              className={`${styles.sidebarItem} ${
                selectedOption === "LLM List" ? styles.selectedItem : ""
              }`}
              onClick={() => setSelectedOption("LLM List")}
            >
              LLM List
            </button>
          </div>
          <div className={styles.contentArea}>
            {selectedOption === "Add LLM" && (
              <div>
                <h3>Add LLM</h3>
                {/* Add LLM form here */}
              </div>
            )}
            {selectedOption === "LLM List" && (
              <div>
                <LLMList />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
