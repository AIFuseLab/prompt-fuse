import React, { useState, useEffect } from "react";
import { Edit, Eye, ChevronDown, Trash2, ChevronUp } from "lucide-react";
import styles from "./prompt-card.module.css";
import CreateTestPopup from "../../test/create-test-popup/create-test-popup";
import axios from "axios";
import { API_BASE_URL } from "../../../config";
import ConfirmationPopup from "../../shared/delete-confirmation/delete-confirmation";
import { toast } from "react-toastify";
interface Prompt {
  id: number;
  name: string;
  prompt: string;
  notes?: string;
  version?: number;
  llm_id?: string;
  prompt_template_id?: string;
  llm_model_name?: string;
}

interface PromptCardProps {
  prompt: Prompt;
  onEdit: (promptId: string) => void;
  onDelete: (promptId: string) => void;
  onView: (promptId: string) => void;
  isTestModalOpen: boolean;
  setIsTestModalOpen: (isOpen: boolean) => void;
  prompts: Prompt[];
}

interface Test {
  id: string;
  test_name: string;
  user_input: string;
  prompt_ids: string[];
  llm_response: string | null;
  input_tokens: string | null;
  output_tokens: string | null;
  total_tokens: string | null;
  latency_ms: string | null;
  prompt_tokens: string | null;
  user_input_tokens: string | null;
  image: string | null;
}

const PromptCard: React.FC<PromptCardProps> = ({
  prompt,
  onEdit,
  onDelete,
  onView,
  isTestModalOpen,
  setIsTestModalOpen,
  prompts,
}) => {
  const [isCarouselOpen, setIsCarouselOpen] = useState(true);
  const [tests, setTests] = useState<Test[]>([]);
  const [isDeleteConfirmationOpen, setIsDeleteConfirmationOpen] =
    useState(false);
  const [testToDelete, setTestToDelete] = useState<string | null>(null);

  const toggleCarousel = () => {
    setIsCarouselOpen(!isCarouselOpen);
  };

  useEffect(() => {
    if (isCarouselOpen) {
      fetchTests();
    }
  }, [isCarouselOpen]);

  const fetchTests = async () => {
    try {
      const response = await axios.get<Test[]>(
        `${API_BASE_URL}/tests/${prompt.id}`
      );
      setTests(response.data);
    } catch (error) {
      toast.error('Failed to fetch tests');
    }
  };

  const handleDeleteTest = async (testId: string) => {
    try {
      await axios.delete(`${API_BASE_URL}/test/${testId}/prompt/${prompt.id}`);
      setTests(tests.filter((test) => test.id !== testId));
      toast.success("Test deleted successfully");
    } catch (error) {
      toast.error("Failed to delete test");
    }
  };

  const handleDeleteClick = (testId: string) => {
    setTestToDelete(testId);
    setIsDeleteConfirmationOpen(true);
  };

  const confirmDeleteTest = () => {
    if (testToDelete) {
      handleDeleteTest(testToDelete);
      setIsDeleteConfirmationOpen(false);
      setTestToDelete(null);
    }
  };

  const [showFullText, setShowFullText] = useState(false);
  const [showImage, setShowImage] = useState(false);
  const [showImageTest, setShowImageTest] = useState(false);

  const toggleText = () => {
    setShowFullText(!showFullText);
  };

  return (
    <div className={styles.promptContainer}>
      <div className={styles.promptItem}>
        <div className={styles.promptDetails}>
          <h1 className={styles.promptName}>{prompt.prompt}</h1>
          <p className={styles.promptVersion}>Title: {prompt.name}</p>
          {prompt.notes && (
            <p className={styles.promptVersion}>Notes: {prompt.notes}</p>
          )}
          <p className={styles.promptVersion} style={{ color: 'red', fontWeight: 'bold', fontStyle: 'italic' }}>Version: {prompt.version}</p>
          <p className={styles.promptModel}>Model: {prompt.llm_model_name}</p>
          <p className={styles.promptModel}>Number of Tests: {tests.length}</p>
        </div>
        <div className={styles.buttonGroup}>
          <div onClick={toggleCarousel} title="Test Setup">
            {isCarouselOpen ? (
              <ChevronUp className="h-4 w-4 mr-2" />
            ) : (
              <ChevronDown className="h-4 w-4 mr-2" />
            )}
          </div>
          <div
            onClick={() => onView(prompt.id.toString())}
            className={styles.viewButton}
          >
            <Eye className="h-4 w-4" />
          </div>
          <div
            onClick={(e) => onEdit(prompt.id.toString())}
            className={styles.editButton}
          >
            <Edit className="h-4 w-4" />
          </div>
          <div
            onClick={(e) => onDelete(prompt.id.toString())}
            className={styles.deleteButton}
          >
            <Trash2 className="h-4 w-4" />
          </div>
        </div>
      </div>
      <div className={styles.carouselContainer}>
        {isCarouselOpen && (
          <div className={styles.carousel}>
            <hr className={styles.divider} />
            {!showImage && (
              <button
                onClick={() => setShowImage(true)}
                className={styles.viewImageButton}
              >
                View Images
              </button>
            )}
            {showImage && (
              <button
                onClick={() => setShowImage(false)}
                className={styles.viewImageButton}
              >
                Hide Images
              </button>
            )}
            {tests.map((test) => (
              <div className={styles.testItem} key={test.id}>
                <div className={styles.header}>
                  <span className={styles.title}>{test.test_name}</span>
                  {test.image ? (
                    <div />
                  ) : (
                    <span className={styles.title}>User Input:</span>
                  )}
                  <div
                    onClick={() => handleDeleteClick(test.id)}
                    className={styles.deleteButton}
                  >
                    <Trash2 className="h-4 w-4 cursor-pointer" />
                  </div>
                </div>

                {test.image ? (
                  <div>
                    <div
                      className={styles.imageContainer}
                      style={{ display: showImage ? "block" : "none" }}
                    >
                      <img
                        src={`data:image/png;base64,${test.image}`}
                        alt="Test Visual Representation"
                        className={styles.testImage}
                      />
                    </div>
                  </div>
                ) : (
                  <div className={styles.userInput}>{test.user_input}</div>
                )}

                <div className={styles.llmResponse}>
                  <span className={styles.title}>LLM Response:</span>
                  <p>
                    {showFullText ? (
                      <div
                        dangerouslySetInnerHTML={{
                          __html: test?.llm_response?.replace(/\n/g, "<br>")!,
                        }}
                      />
                    ) : (
                      <div
                        dangerouslySetInnerHTML={{
                          __html: `${test?.llm_response
                            ?.substring(0, 290)
                            ?.replace(/\n/g, "<br>")}${
                            test?.llm_response?.length! > 290 ? "..." : ""
                          }`,
                        }}
                      />
                    )}
                    {!showFullText && test?.llm_response?.length! > 290 && (
                      <span onClick={toggleText} className={styles.showMore}>
                        Show More
                      </span>
                    )}
                    {showFullText && test?.llm_response?.length! > 290 && (
                      <span onClick={toggleText} className={styles.showMore}>
                        Show Less
                      </span>
                    )}
                  </p>
                </div>

                {/* <hr className={styles.separator} /> */}

                <div className={styles.metrics}>
                  <div className={styles.metricItem}>
                    <span>Input Tokens:</span> {test.input_tokens}
                  </div>
                  <div className={styles.metricItem}>
                    <span>Output Tokens:</span> {test.output_tokens}
                  </div>
                  <div className={styles.metricItem}>
                    <span>Total Tokens:</span> {test.total_tokens}
                  </div>
                  <div className={styles.metricItem}>
                    <span>Latency (ms):</span> {test.latency_ms}
                  </div>
                  <div className={styles.metricItem}>
                    <span>Prompt Tokens:</span> {test.prompt_tokens}
                  </div>
                  {test.image ? (
                    <div />
                  ) : (
                    <div className={styles.metricItem}>
                      <span>User Input Tokens:</span> {test.user_input_tokens}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      <ConfirmationPopup
        isOpen={isDeleteConfirmationOpen}
        onClose={() => setIsDeleteConfirmationOpen(false)}
        onConfirm={confirmDeleteTest}
        message="Are you sure you want to delete this test?"
      />
      {isTestModalOpen && (
        <CreateTestPopup
          isOpen={isTestModalOpen}
          onClose={() => setIsTestModalOpen(false)}
          prompts={prompts}
        />
      )}
    </div>
  );
};

export default PromptCard;
