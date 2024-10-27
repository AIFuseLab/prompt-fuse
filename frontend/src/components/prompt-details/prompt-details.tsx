import React, { useEffect, useState } from "react";
import styles from "./prompt-details.module.css";
import Navbar from "../navbar/navbar";
import Settings from "../settings/settings";
import { API_BASE_URL } from "../../config";
import CreatePromptPopup from "../create-prompt-popup/create-prompt-popup";
import axios from "axios";
import { toast } from "react-toastify";
import ConfirmationPopup from "../delete-confirmation/delete-confirmation";
import PromptCard from "../prompt-card/prompt-card";

interface IPrompt {
  id: string;
  name: string;
  description: string | null;
  prompt: string;
  notes: string | null;
  creation_date: string;
  version_number: number;
  llm_id: string | null;
  project_id: string | null;
  llm_model_name: string | null;
}

const PromptDetails: React.FC = () => {
  function extractIdsFromUrl() {
    const url = window.location.href;

    const pattern = /\/project\/([a-f0-9-]+)\/prompt\/([a-f0-9-]+)/;

    const match = url.match(pattern);

    if (match) {
      const projectId = match[1];
      const promptTemplateId = match[2];
      return { projectId, promptTemplateId };
    } else {
      toast.error("Invalid URL");
      return null;
    }
  }

  const ids = extractIdsFromUrl();

  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [isPromptModalOpen, setIsPromptModalOpen] = useState(false);
  const [isTestModalOpen, setIsTestModalOpen] = useState(false);

  const [promptTemplate, setPromptTemplate] = useState<any>(null);
  const [prompts, setPrompts] = useState<any[]>([]);

  const [editingPrompt, setEditingPrompt] = useState<any>(null);
  const [viewingPrompt, setViewingPrompt] = useState<any>(null);
  const [promptToDelete, setPromptToDelete] = useState<string | null>(null);
  const [isDeleteConfirmationOpen, setIsDeleteConfirmationOpen] =
    useState(false);

  const filteredPrompts = prompts.filter(
    (prompt) =>
      prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prompt.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const fetchPrompts = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/prompts/${ids?.promptTemplateId}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPrompts(data.reverse());
    } catch (error) {
      toast.error('Failed to fetch prompts');
      return null;
    }
  };

  useEffect(() => {
    const fetchPromptTemplateDetails = async () => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/prompt-template/${ids?.promptTemplateId}`
        );
        setPromptTemplate(response.data);
      } catch (error: any) {
        toast.error(
          error?.response?.data?.detail ||
            "Failed to fetch prompt template details"
        );
      }
    };

    fetchPromptTemplateDetails();
  }, [ids?.promptTemplateId]);

  useEffect(() => {
    fetchPrompts();
  }, []);

  const handleEditPrompt = (promptId: string) => {
    const promptToEdit = prompts?.find(
      (prompt: IPrompt) => prompt.id === promptId
    );

    if (promptToEdit) {
      setEditingPrompt(promptToEdit);
      setIsPromptModalOpen(true);
    }
  };

  const handleViewPrompt = (promptId: string) => {
    const promptToView = prompts?.find(
      (prompt: IPrompt) => prompt.id === promptId
    );
    if (promptToView) {
      setEditingPrompt(promptToView);
      setViewingPrompt(true);
      setIsPromptModalOpen(true);
    }
  };

  const handleDeletePrompt = (promptId: string) => {
    setPromptToDelete(promptId);
    setIsDeleteConfirmationOpen(true);
  };

  const confirmDeletePrompt = async () => {
    if (promptToDelete) {
      try {
        await axios.delete(`${API_BASE_URL}/prompt/${promptToDelete}`);
        toast.success('Prompt deleted successfully');
        // await fetchProjectPrompts();
      } catch (error: any) {
        toast.error(error?.response?.data?.detail);
      }
    }
    setIsDeleteConfirmationOpen(false);
    setPromptToDelete(null);
    fetchPrompts();
  };

  const handlePromptCreatedOrUpdated = async () => {
    setIsPromptModalOpen(false);
    setEditingPrompt(null);
    fetchPrompts();
  };

  return (
    <div className={styles.container}>
      <Navbar
        onSettingsClick={() => setIsSettingsModalOpen(true)}
        redirectTo={`/project/${ids?.projectId}`}
        title={"Prompt Details"}
      />
      <div className={styles.innerContainer}>
        <div className={styles.projectHeader}>
          <h1 className={styles.title}>{promptTemplate?.name}</h1>
          <p className={styles.description}>{promptTemplate?.description}</p>
          <p
            className={styles.description}
            style={{ paddingTop: "1rem", fontStyle: "italic" }}
          >
            Number of Prompts: {prompts.length}
          </p>
        </div>
        <div className={styles.searchAndPrompt}>
          <div className={styles.searchBar}>
            <input
              type="text"
              placeholder="Search Prompts (by prompt & title)..."
              className={styles.searchInput}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          {prompts.length === 0 && (
            <button
              className={styles.createPromptButton}
              onClick={() => setIsPromptModalOpen(true)}
            >
              Add Initial Prompt
            </button>
          )}
          {prompts.length > 0 && (
            <button
              className={styles.createPromptButton}
              onClick={() => {
                setIsTestModalOpen(true);
                setIsPromptModalOpen(false);
              }}
            >
              Add Test
            </button>
          )}
        </div>
      </div>
      <div className={styles.promptList}>
        {filteredPrompts.map((prompt) => (
          <div key={prompt.id}>
            <PromptCard
              prompt={prompt}
              onEdit={handleEditPrompt}
              onDelete={handleDeletePrompt}
              onView={handleViewPrompt}
              isTestModalOpen={isTestModalOpen}
              setIsTestModalOpen={setIsTestModalOpen}
              prompts={prompts}
            />
          </div>
        ))}
      </div>

      {isPromptModalOpen && (
        <CreatePromptPopup
          isOpen={isPromptModalOpen}
          onClose={() => {
            setIsPromptModalOpen(false);
            setEditingPrompt(null);
            setViewingPrompt(false);
          }}
          projectId={ids?.projectId!}
          promptTemplateId={ids?.promptTemplateId!}
          onPromptCreated={handlePromptCreatedOrUpdated}
          editingPrompt={editingPrompt}
          viewingPrompt={viewingPrompt}
        />
      )}
      <ConfirmationPopup
        isOpen={isDeleteConfirmationOpen}
        onClose={() => setIsDeleteConfirmationOpen(false)}
        onConfirm={confirmDeletePrompt}
        message="Are you sure you want to delete this prompt?"
      />
      <Settings
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
      />
    </div>
  );
};

export default PromptDetails;
