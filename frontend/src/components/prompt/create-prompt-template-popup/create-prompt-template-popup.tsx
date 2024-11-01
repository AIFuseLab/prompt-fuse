import React, { useState, useEffect } from "react";
import axios from "axios";
import styles from "./create-prompt-template-popup.module.css";
import { toast } from "react-toastify";
import { API_BASE_URL } from "../../../config";

interface PromptTemplate {
  name: string;
  description: string;
  project_id: string;
}

interface CreatePromptTemplatePopupProps {
  isOpen: boolean;
  onClose: () => void;
  onPromptCreated: (prompt: PromptTemplate) => void;
  projectId: string;
  editingPrompt?: any;
}

function CreatePromptTemplatePopup({
  isOpen,
  onClose,
  onPromptCreated,
  projectId,
  editingPrompt,
}: CreatePromptTemplatePopupProps) {
  const [prompt, setPrompt] = useState<PromptTemplate>({
    name: "",
    description: "",
    project_id: projectId,
  });

  useEffect(() => {
    if (editingPrompt) {
      setPrompt({
        name: editingPrompt.name || "",
        description: editingPrompt.description || "",
        project_id: projectId,
      });
    }
  }, [editingPrompt, projectId]);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setPrompt({ ...prompt, [name]: value });
  };

  const savePromptTemplate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post<PromptTemplate>(
        `${API_BASE_URL}/prompt-templates`,
        prompt
      );
      onPromptCreated(response.data);
      setPrompt({
        name: "",
        description: "",
        project_id: projectId,
      });
      onClose();
      toast.success('Prompt template created successfully');
    } catch (error: any) {
      toast.error(error?.response?.data?.detail);
    }
  };

  const updatePromptTemplate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.put<PromptTemplate>(
        `${API_BASE_URL}/prompt-template/${editingPrompt.id}`,
        prompt
      );
      onPromptCreated(response.data);
      setPrompt({
        name: "",
        description: "",
        project_id: projectId,
      });
      toast.success('Prompt template updated successfully');
      onClose();
    } catch (error: any) {
      toast.error(error?.response?.data?.detail);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay}>
      <div className={styles.popup}>
        <h2 className={styles.title}>Create Prompt Template</h2>
        <form
          onSubmit={editingPrompt ? updatePromptTemplate : savePromptTemplate}
        >
          <input
            type="text"
            name="name"
            value={prompt.name}
            className={styles.input}
            onChange={handleInputChange}
            placeholder="Prompt Template Name"
            required
          />
          <textarea
            name="description"
            value={prompt.description}
            onChange={handleInputChange}
            className={styles.textarea}
            placeholder="Prompt Template Description"
            required
          />
          <div className={styles.buttonContainer}>
            <button
              type="button"
              onClick={onClose}
              className={styles.cancelButton}
            >
              Cancel
            </button>
            <button type="submit" className={styles.createButton}>
              {editingPrompt
                ? "Update Prompt Template"
                : "Create Prompt Template"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreatePromptTemplatePopup;
