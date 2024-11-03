import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { useNavigate, useParams } from "react-router-dom";
import styles from "./project-details.module.css";
import Navbar from "../../shared/navbar/navbar";
import Settings from "../../shared/settings/settings";
import PromptTemplateCard from "../../prompt/prompt-template-card/prompt-template-card";
import ConfirmationPopup from "../../shared/delete-confirmation/delete-confirmation";
import CreatePromptTemplatePopup from "../../prompt/create-prompt-template-popup/create-prompt-template-popup";
import { toast } from "react-toastify";
import { API_BASE_URL } from "../../../config";
import { ChevronUp, ChevronDown, Terminal, SquareFunction, Edit, Trash2 } from "lucide-react";

interface IPromptTemplate {
  id: string;
  name: string;
  description: string | null;
  creation_date: string;
  updated_at: string;
  number_of_prompts: number;
  project_id: string | null;
}

function ProjectDetails() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<any>(null);
  const [promptTemplates, setPromptTemplates] = useState<IPromptTemplate[]>([]);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [isPromptModalOpen, setIsPromptModalOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<any>(null);
  const [isDeleteConfirmationOpen, setIsDeleteConfirmationOpen] =
    useState(false);
  const [isCarouselOpen, setIsCarouselOpen] = useState(false);

  const toggleCarousel = () => {
    setIsCarouselOpen(!isCarouselOpen);
  };
  const navigate = useNavigate();

  const [promptToDelete, setPromptToDelete] = useState<string | null>(null);
  const filteredPrompts = promptTemplates.filter(
    (promptTemplate) =>
      promptTemplate.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      promptTemplate.description
        ?.toLowerCase()
        .includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    const fetchProjectDetails = async () => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/project/${projectId}`
        );
        setProject(response.data);
      } catch (error: any) {
        toast.error(error?.response?.data?.message);
      }
    };

    fetchProjectDetails();
  }, [projectId]);


  const fetchProjectPrompts = useCallback(async () => {
    try {
      const response: any = await axios.get(
        `${API_BASE_URL}/prompt-templates/${projectId}`
      );
      setPromptTemplates(response.data.reverse());
    } catch (error: any) {
      toast.error(
        error?.response?.data?.message || "Failed to fetch prompt templates"
      );
    }
  }, [projectId]);

  useEffect(() => {
    fetchProjectPrompts();
  }, [projectId, fetchProjectPrompts]);

  if (!project) {
    return <div className={styles.loading}>Loading...</div>;
  }

  const handleEditPrompt = (promptId: string) => {
    const promptToEdit = promptTemplates.find(
      (prompt: IPromptTemplate) => prompt.id === promptId
    );

    if (promptToEdit) {
      setEditingPrompt(promptToEdit);
      setIsPromptModalOpen(true);
    }
  };

  const handleDeletePrompt = (promptId: string) => {
    setPromptToDelete(promptId);
    setIsDeleteConfirmationOpen(true);
  };

  const confirmDeletePromptTemplate = async () => {
    if (promptToDelete) {
      try {
        await axios.delete(`${API_BASE_URL}/prompt-template/${promptToDelete}`);
        await fetchProjectPrompts();
        toast.success("Prompt template deleted successfully");
      } catch (error: any) {
        toast.error(error?.response?.data?.message);
      }
    }
    setIsDeleteConfirmationOpen(false);
    setPromptToDelete(null);
  };

  const handlePromptCreatedOrUpdated = async () => {
    await fetchProjectPrompts();
    setIsPromptModalOpen(false);
    setEditingPrompt(null);
  };


  const handlePromptTemplateClick = (
    projectId: number | string,
    promptId: string
  ) => {
    navigate(`/project/${projectId}/prompt/${promptId}`);
  };



  return (
    <div className={styles.container}>
      <Navbar
        onSettingsClick={() => setIsSettingsModalOpen(true)}
        redirectTo={`/`}
        title="Prompt Template"
      />
      <div className={styles.innerContainer}>
        <div className={styles.projectHeader}>
          <h1 className={styles.title}>{project.name}</h1>
          <p className={styles.description}>{project.description}</p>
          <p
            className={styles.description}
            style={{ paddingTop: "1rem", fontStyle: "italic" }}
          >
            Number of Prompt Templates: {promptTemplates.length}
          </p>
        </div>

        <div className={styles.searchAndPrompt}>
          <div className={styles.searchBar}>
            <input
              type="text"
              placeholder="Search Prompt Templates..."
              className={styles.searchInput}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button
            className={styles.createPromptButton}
            onClick={() => setIsPromptModalOpen(true)}
          >
            <Terminal className="h-6.5 w-5" />
          </button>
        </div>


        <div className={styles.promptList}>
          {filteredPrompts.map((prompt) => (
            <div key={prompt.id}>
              <PromptTemplateCard
                prompt={prompt}
                onEdit={handleEditPrompt}
                onDelete={handleDeletePrompt}
                onPromptTemplateClick={handlePromptTemplateClick}
              />
            </div>
          ))}
        </div>

        <Settings
          isOpen={isSettingsModalOpen}
          onClose={() => setIsSettingsModalOpen(false)}
        />

        {isPromptModalOpen && (
          <CreatePromptTemplatePopup
            isOpen={isPromptModalOpen}
            onClose={() => {
              setIsPromptModalOpen(false);
              setEditingPrompt(null);
            }}
            projectId={projectId!}
            onPromptCreated={handlePromptCreatedOrUpdated}
            editingPrompt={editingPrompt}
          />
        )}

        <ConfirmationPopup
          isOpen={isDeleteConfirmationOpen}
          onClose={() => setIsDeleteConfirmationOpen(false)}
          onConfirm={confirmDeletePromptTemplate}
          message="Are you sure you want to delete this prompt template?"
        />
      </div>
    </div>
  );
}

export default ProjectDetails;
