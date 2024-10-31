import React, { useState, useEffect } from "react";
import axios from "axios";
import styles from "./main.module.css";
import { useNavigate } from "react-router-dom";
import { PlusCircle } from "lucide-react";
import ProjectPopup from "./project/project-popup/project-popup";
import ConfirmationPopup from "./shared/delete-confirmation/delete-confirmation";
import ProjectCard from "./project/project-card/project-card";
import Navbar from "./shared/navbar/navbar";
import Settings from "./shared/settings/settings";
import { toast } from "react-toastify";
import { API_BASE_URL } from "../config";

interface Project {
  id: number;
  name: string;
  description: string;
  creation_date: string;
  last_updated: string;
}


function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [isConfirmationOpen, setIsConfirmationOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);

  const navigate = useNavigate();
  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get<Project[]>(`${API_BASE_URL}/projects`);
      setProjects(response.data);
    } catch (error: any) {
      toast.error(error?.response?.data?.detail);
    }
  };

  const deleteProject = async (id: number) => {
    try {
      await axios.delete(`${API_BASE_URL}/project/${id}`);
      setProjects(projects.filter((p) => p.id !== id));
      toast.success('Project deleted successfully');
    } catch (error: any) {
      toast.error(error?.response?.data?.detail);
    }
    fetchProjects();
  };

  const handleProjectClick = (projectId: number | string) => {
    navigate(`/project/${projectId}`);
  };

  const handleEditClick = (e: React.MouseEvent, project: Project) => {
    e.stopPropagation();
    setEditingProject(project);
    setIsProjectModalOpen(true);
  };

  const handleProjectSaved = (savedProject: Project) => {
    if (editingProject) {
      setProjects(
        projects.map((p) => (p.id === savedProject.id ? savedProject : p))
      );
    } else {
      setProjects([...projects, savedProject]);
    }
    setIsProjectModalOpen(false);
    setEditingProject(null);
    fetchProjects();
  };

  const handleDeleteClick = (e: React.MouseEvent, project: Project) => {
    e.stopPropagation();
    setProjectToDelete(project);
    setIsConfirmationOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (projectToDelete) {
      await deleteProject(projectToDelete.id);
      setIsConfirmationOpen(false);
      setProjectToDelete(null);
      fetchProjects();
    }
  };

  return (
    <div className={styles.container}>
      <Navbar onSettingsClick={() => setIsSettingsModalOpen(true)} redirectTo={`/`} />

      <main className={styles.mainContent}>
        <div className={styles.projectHeader}>
          <h2 className={styles.subtitle}>Projects</h2>
          <button
            className={styles.createButton}
            onClick={() => {
              setEditingProject(null);
              setIsProjectModalOpen(true);
            }}
          >
            <PlusCircle className="h-5 w-5 mr-2" />
            Create Project
          </button>
        </div>

        <div className={styles.projectList}>
          {projects.map((project) => (
            <ProjectCard
              key={project.id.toString()}
              project_com={project as Project}
              onProjectClick={handleProjectClick}
              onEditClick={handleEditClick}
              onDeleteClick={handleDeleteClick}
            />
          ))}
        </div>
      </main>

      <ProjectPopup
        isOpen={isProjectModalOpen}
        onClose={() => setIsProjectModalOpen(false)}
        onProjectSaved={handleProjectSaved}
        project={editingProject ?? undefined}
      />

      <ConfirmationPopup
        isOpen={isConfirmationOpen}
        onClose={() => setIsConfirmationOpen(false)}
        onConfirm={handleConfirmDelete}
        message={`Are you sure you want to delete the project "${projectToDelete?.name}"?`}
      />

      <Settings
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
      />
    </div>
  );
}

export default Projects;
