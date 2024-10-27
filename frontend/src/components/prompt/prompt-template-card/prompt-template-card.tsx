import React from "react";
import { BarChart2, Edit, Trash2 } from "lucide-react";
import styles from "./prompt-template-card.module.css";

interface Prompt {
  id: string;
  name: string;
  description: string | null;
  creation_date: string;
  updated_at: string;
  number_of_prompts: number;
  project_id: string | null;
}

interface PromptTemplateCardProps {
  onPromptTemplateClick: (projectId: string, promptId: string) => void;
  prompt: Prompt;
  onEdit: (promptId: string) => void;
  onDelete: (promptId: string) => void;
}

const PromptTemplateCard: React.FC<PromptTemplateCardProps> = ({
  onPromptTemplateClick,
  prompt,
  onEdit,
  onDelete,
}) => {
  return (
    <div className={styles.promptItem}>
      <div
        className={styles.promptDetails}
        onClick={() =>
          onPromptTemplateClick(
            prompt.project_id?.toString()!,
            prompt.id.toString()
          )
        }
      >
        <h3 className={styles.promptName}>{prompt.name}</h3>
        <p className={styles.promptDescription}>{prompt.description}</p>
      </div>
      <div className={styles.buttonGroup}>
        <div onClick={() => {}} title="Analytics" className={styles.analyticsButton}>
          <BarChart2 className="h-4 w-4" />
        </div>
        <div
          onClick={(e) => onEdit(prompt.id.toString())}
          title="Edit"
          className={styles.editButton}
        >
          <Edit className="h-4 w-4" />
        </div>
        <div
          onClick={(e) => onDelete(prompt.id.toString())}
          title="Delete"
          className={styles.deleteButton}
        >
          <Trash2 className="h-4 w-4" />
        </div>
      </div>
    </div>
  );
};

export default PromptTemplateCard;
