import React, { useState, useEffect } from "react";
import axios from "axios";
import styles from "./create-prompt-popup.module.css";
import { toast } from "react-toastify";
import { API_BASE_URL } from "../../config";
import { encode } from 'gpt-tokenizer'

interface Prompt {
  id: number;
  name: string;
  prompt: string;
  notes?: string;
  version?: number;
  llm_id?: string;
  prompt_template_id?: string;
}

interface CreatePromptPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onPromptCreated: (prompt: Prompt) => void;
  projectId: string;
  editingPrompt?: Prompt;
  promptTemplateId: string;
  viewingPrompt?: boolean;
}


interface LLM {
  id: string;
  name: string;
  llm_model_id: string;
}

function CreatePromptPopup({
  isOpen,
  onClose,
  onPromptCreated,
  projectId,
  editingPrompt,
  promptTemplateId,
  viewingPrompt,
}: CreatePromptPopupProps) {
  const [prompt, setPrompt] = useState<Omit<Prompt, "id">>({
    name: "",
    prompt: "",
    notes: "",
    version: 0,
    llm_id: "",
    prompt_template_id: promptTemplateId,
  });

  const [availableLLMs, setAvailableLLMs] = useState<LLM[]>([]);

  useEffect(() => {
    const fetchLLMs = async () => {
      try {
        const response = await axios.get<LLM[]>(`${API_BASE_URL}/llms`);
        setAvailableLLMs(response.data);
        toast.success('LLMs fetched successfully');
      } catch (error: any) {
        toast.error(error?.response?.data?.detail);
      }
    };

    fetchLLMs();
    if (editingPrompt) {
      setPrompt({
        name: editingPrompt.name || "",
        prompt: editingPrompt.prompt || "",
        notes: editingPrompt.notes || "",
        version: editingPrompt.version || 0,
        llm_id: editingPrompt.llm_id || "",
        prompt_template_id: promptTemplateId,
      });
    }
  }, [editingPrompt, promptTemplateId]);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setPrompt({ ...prompt, [name]: value });
  };

  const savePrompt = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post<Prompt>(
        `${API_BASE_URL}/prompt`,
        prompt
      );
      onPromptCreated(response.data);
      setPrompt({
        name: "",
        prompt: "",
        notes: "",
        version: 0,
        prompt_template_id: promptTemplateId,
        llm_id: "",
      });
      onClose();
      toast.success('Prompt created successfully');
    } catch (error: any) {
      toast.error(error?.response?.data?.detail);
    }
  };

  const updatePromptTemplate = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await axios.put<Prompt>(
        `${API_BASE_URL}/prompt/${editingPrompt?.id}`,
        prompt
      );
      onPromptCreated(response.data);
      setPrompt({
        name: "",
        prompt: "",
        notes: "",
        llm_id: "",
        prompt_template_id: promptTemplateId,
      });
      onClose();
      toast.success('Prompt updated successfully');
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "An error occurred while updating the prompt");
    }
  };

  if (!isOpen) return null;

  const calculateTokens = (text: string) => {
    return encode(text).length;
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.popup}>
        <h2 className={styles.title}>{viewingPrompt  ? "View Prompt" : editingPrompt  ? "Update Prompt" : "Add Initial Prompt"}</h2>
        <form onSubmit={editingPrompt ? updatePromptTemplate : savePrompt}>
          <div>
            <small>Title</small>
            <input
              type="text"
              name="name"
              placeholder="Prompt Title"
              className={styles.input}
              value={prompt.name}
              onChange={handleInputChange}
              required
              disabled={viewingPrompt}
            />
          </div>
          <div>
            <div className={styles.promptTextContainer}>
              <small>Prompt</small>
              <small className={styles.charCounter}>
                Chars: {prompt.prompt.length} / ∞
              </small>
              <small className={styles.tokenCounter}>
                Tokens: {calculateTokens(prompt.prompt)}
              </small>
            </div>
            <textarea
              name="prompt"
              placeholder="Prompt"
              className={styles.textarea}
              value={prompt.prompt}
              onChange={handleInputChange}
              required
              disabled={viewingPrompt}
            />
          </div>
          <div>
            <small>Note</small>
            <textarea
              name="notes"
              placeholder="Note"
              className={styles.textarea}
              value={prompt.notes}
              onChange={handleInputChange}
              disabled={viewingPrompt}
            />
          </div>
          <div>
            <small>LLM Model</small>
            <select
              name="llm_id"
              className={styles.input}
              value={prompt.llm_id}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                handleInputChange(e)
              }
              required
              disabled={viewingPrompt}
            >
              <option value="" disabled>
                Select an LLM model
              </option>
              {availableLLMs.map((llm) => (
                <option key={llm.id} value={llm.id}>
                  {llm.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <small>Version Number</small>
            <input
              type="number"
              name="version_number"
              placeholder="Version Number"
              className={styles.input}
              value={prompt.version}
              onChange={handleInputChange}
              disabled={true}
              title="Version"
            />
          </div>
          <div className={styles.buttonContainer}>
            <button
              type="button"
              className={styles.cancelButton}
              onClick={onClose}
            >
              Cancel
            </button>
            {!viewingPrompt && (
              <button type="submit" className={styles.createButton}>
                { editingPrompt ? "Update Prompt" : "Add Initial Prompt"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreatePromptPopup;
