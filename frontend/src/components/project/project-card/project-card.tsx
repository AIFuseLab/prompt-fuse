import React from "react";
import { Edit2, Trash2 } from "lucide-react";
import styles from "./project-card.module.css";

interface Project {
  id: number;
  name: string;
  description: string;
  creation_date: string;
  last_updated: string;
}

interface ProjectCardProps {
  project_com: Project;
  onProjectClick: (id: string) => void;
  onEditClick: (e: React.MouseEvent, project: Project) => void;
  onDeleteClick: (e: React.MouseEvent, project: Project) => void;
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  project_com,
  onProjectClick,
  onEditClick,
  onDeleteClick,
}) => {
  return (
    <div
      className={styles.projectItem}
      onClick={() => onProjectClick(project_com.id.toString())}
    >
      <div className={styles.projectDetails}>
        <h3 className={styles.projectName}>{project_com.name}</h3>
        <p className={styles.projectDescription}>{project_com.description}</p>
      </div>
      <div className={styles.buttonGroup}>
        <button
          className={styles.editButton}
          onClick={(e) => onEditClick(e, project_com)}
        >
          <Edit2 className="h-4 w-4" />
        </button>
        <button
          className={styles.deleteButton}
          onClick={(e) => onDeleteClick(e, project_com)}
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default ProjectCard;
