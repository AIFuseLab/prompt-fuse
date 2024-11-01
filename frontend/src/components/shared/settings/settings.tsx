import React, { useState } from 'react';
import styles from './settings.module.css'; // Make sure to create and import the appropriate CSS module
import LLMList from './llm-list'; // Adjust the import path as needed
import { API_BASE_URL } from '../../../config';
import { toast } from 'react-toastify';

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

interface LLM {
  name: string;
  description: string | null;
  llm_model_id: string | null;
  aws_region: string | null;
  access_key: string | null;
  secret_access_key: string | null;
  selected: boolean;
}

const Settings: React.FC<SettingsProps> = ({ isOpen, onClose }) => {
  const [selectedOption, setSelectedOption] = useState<string>("Add LLM");
  const [llmName, setLlmName] = useState<string>("");
  const [llmDescription, setLlmDescription] = useState<string>("");
  const [llmModelId, setLlmModelId] = useState<string>("");
  const [awsRegion, setAwsRegion] = useState<string>("");
  const [accessKey, setAccessKey] = useState<string>("");
  const [secretAccessKey, setSecretAccessKey] = useState<string>("");

  const handleSubmit = async (llm: LLM) => {
    try {
      const response = await fetch(`${API_BASE_URL}/llms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(llm),
      });

      if (!response.ok) {
        throw new Error('Failed to create LLM');
      }

      const data = await response.json();
      toast.success('LLM created successfully');
      onClose();
      setLlmName('');
      setLlmDescription('');
      setLlmModelId('');
      setAwsRegion('');
      setAccessKey('');
      setSecretAccessKey('');
    } catch (error) {
      console.error('Error creating LLM:', error);
      toast.error('Error creating LLM');
    }
  };

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
              className={`${styles.sidebarItem} ${selectedOption === "Add LLM" ? styles.selectedItem : ""
                }`}
              onClick={() => setSelectedOption("Add LLM")}
            >
              Add LLM
            </button>
            <button
              className={`${styles.sidebarItem} ${selectedOption === "LLM List" ? styles.selectedItem : ""
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
                <form onSubmit={(e) => {
                  e.preventDefault();
                  handleSubmit({
                    name: llmName,
                    description: llmDescription,
                    llm_model_id: llmModelId,
                    aws_region: awsRegion,
                    access_key: accessKey,
                    secret_access_key: secretAccessKey,
                    selected: false,
                  });
                }} className={styles.form}>
                  <div>
                    <small>Name</small><br />
                    <input name="name" value={llmName} title='Name' onChange={(e) => setLlmName(e.target.value)} className={styles.input} required />
                  </div>
                  <div>
                    <small>Description</small><br />
                    <input name="description" value={llmDescription} title='Description' onChange={(e) => setLlmDescription(e.target.value)} className={styles.input} required />
                  </div>
                  <div>
                    <small>LLM Model ID</small><br />
                    <input name="llm_model_id" placeholder='anthropic.claude-3-5-sonnet-20240620-v1:0' value={llmModelId} title='LLM Model ID' onChange={(e) => setLlmModelId(e.target.value)} className={styles.input} required />
                  </div>
                  <div>
                    <small>AWS Region</small><br />
                    <input name="aws_region" value={awsRegion} title='AWS Region' onChange={(e) => setAwsRegion(e.target.value)} className={styles.input} required />
                  </div>
                  <div>
                    <small>Access Key</small><br />
                    <input name="access_key" value={accessKey} title='Access Key' onChange={(e) => setAccessKey(e.target.value)} className={styles.input} required />
                  </div>
                  <div>
                    <small>Secret Access Key</small><br />
                    <input name="secret_access_key" value={secretAccessKey} title='Secret Access Key' onChange={(e) => setSecretAccessKey(e.target.value)} className={styles.input} required />
                  </div>
                  {/* <input name="selected" type="checkbox" checked={false} onChange={() => { }} /> */}
                  <div className={styles.buttonContainer}>
                    <button type="submit" className={styles.button}>Save</button>
                    <button onClick={() => { }} className={styles.buttonCancel}>Cancel</button>
                  </div>
                </form>
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
