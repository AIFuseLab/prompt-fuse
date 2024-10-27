import { useEffect, useState } from "react";
import styles from "./create-test-popup.module.css";
import { API_BASE_URL } from "../../config";
import { encode } from "gpt-tokenizer";
import { toast } from "react-toastify";
import { useParams } from 'react-router-dom';

interface CreateTestPopupProps {
  isOpen: boolean;
  onClose: () => void;
  prompts: Prompt[];
}

interface LLMTool {
  id: number;
  name: string;
}

interface Test {
  name: string;
  user_input: string | null;
  prompt_id: string[];
  input_type: string;
  image_input: File | null;
}

interface Prompt {
  id: number;
  name: string;
  prompt: string;
  notes?: string;
  version?: number;
  llm_id?: string;
  prompt_template_id?: string;
}


function CreateTestPopup({ isOpen, onClose, prompts }: CreateTestPopupProps) {
  const { projectId } = useParams<{ projectId: string }>();
  const [test, setTest] = useState<Omit<Test, "id">>({
    name: "",
    user_input: null,
    prompt_id: [],
    input_type: "text",
    image_input: null,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);

  const [llmTools, setLLMTools] = useState<LLMTool[]>([]);

  const fetchLLMTools = async (projectId: string) => {
    const response = await fetch(`${API_BASE_URL}/llm-tools/${projectId}`);
    const data = await response.json();
    setLLMTools(data);
  };

  useEffect(() => {
    if (projectId) {
      fetchLLMTools(projectId);
    }
  }, [projectId]);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setTest({ ...test, [name]: value });
  };

  const handleMultiSelectInputChange = (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const { options } = e.target;

    const selectedValues = Array.from(options)
      .filter((option) => option.selected)
      .map((option) => option.value);

    if (selectedValues.includes("all")) {
      setTest({
        ...test,
        prompt_id: prompts.map((prompt) => prompt.id.toString()),
      });
    } else {
      setTest({
        ...test,
        prompt_id: selectedValues,
      });
    }
  };

  const handleInputTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setTest({ ...test, input_type: value });
  };

  const calculateTokens = (text: string) => {
    return encode(text).length;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);

    let response = null;
    try {
      if (test.input_type === "text") {

        response = await fetch(`${API_BASE_URL}/test/text`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            test_name: test.name,
            user_input: test.user_input,
            prompt_ids: test.prompt_id,
            input_type: test.input_type,
          }),
        });
      } else {

        const formData = new FormData();
        formData.append('test_name', test.name);
        formData.append('prompt_ids', JSON.stringify(test.prompt_id));
        formData.append('input_type', test.input_type);
        if (imageFile) {
          formData.append('image_input', imageFile);
        }
  
        response = await fetch(`${API_BASE_URL}/test/image`, {
          method: "POST",
          body: formData,
        });
      }

      if (!response?.ok) {
        toast.error("Error creating test");
        throw new Error("Failed to create test");
      }

      toast.success("Test created successfully");
      onClose();
    } catch (error) {
      toast.error("Error creating test");
    } finally {
      setIsLoading(false);
    }
  };



  return (
    <div className={styles.overlay}>
      <div className={styles.popup}>
        <h2 className={styles.title}>Add Test</h2>
        <form onSubmit={handleSubmit}>
          <div>
            <small>Input Type</small>
            <div className={styles.inputTypeContainer}>
              <label>
                <input
                  type="radio"
                  name="input_type"
                  value="text"
                  checked={test.input_type === "text"}
                  onChange={handleInputTypeChange}
                  className={styles.inputType}
                />
                Text
              </label>
              <label>
                <input
                  type="radio"
                  name="input_type"
                  value="image"
                  checked={test.input_type === "image"}
                  onChange={handleInputTypeChange}
                  className={styles.inputType}
                />
                Image
              </label>
              <label>
                <input
                  type="radio"
                  name="input_type"
                  value="tools"
                  checked={test.input_type === "tools"}
                  onChange={handleInputTypeChange}
                  className={styles.inputType}
                />
                Tools
              </label>
            </div>
          </div>
          <div>
            <small>Name</small>
            <input
              type="text"
              name="name"
              placeholder="Test Name"
              className={styles.input}
              value={test.name}
              onChange={handleInputChange}
              required
            />
          </div>
          {test.input_type === "text" ? (
            <div>
              <div className={styles.promptTextContainer}>
                <small>User Input</small>
                <small className={styles.charCounter}>
                  Chars: {test?.user_input?.length} / ∞
                </small>
                <small className={styles.tokenCounter}>
                  Tokens: {calculateTokens(test?.user_input || "")}
                </small>
              </div>
              <textarea
                name="user_input"
                placeholder="User Input"
                className={styles.textareaInput}
                value={test?.user_input || ""}
                onChange={handleInputChange}
                required
              />
            </div>
          ) : test.input_type === "image" ? (
            <div>
              <div className={styles.promptTextContainer}>
                <small>Upload Image</small>
              </div>
              <input
                type="file"
                name="image_input"
                accept="image/*"
                className={styles.uploadImageInput}
                onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                required
              />
            </div>
          ) : test.input_type === "tools" ? (
            <div>
              <small>LLM Tools</small>
              <div className={styles.toolSelectContainer}>
                <select name="tool_id" className={styles.inputSelect} multiple>
                  <option value="all">All Tools</option>
                  {llmTools.map((tool) => (
                    <option key={tool.id} value={tool.id}>
                      {tool.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          ) : null}
          <div>
            <small>Prompt</small>
            <select
              name="prompt_id"
              className={styles.inputSelect}
              value={test.prompt_id}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                handleMultiSelectInputChange(e)
              }
              multiple
              required
            >
              <option value="all">All Prompts</option>
              {prompts.map((prompt) => (
                <option key={prompt.id} value={prompt.id}>
                  {prompt.name} - {prompt.version}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.buttonContainer}>
            <button
              type="button"
              className={styles.cancelButton}
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </button>

            <button
              type="submit"
              className={styles.createButton}
              disabled={isLoading}
            >
              {isLoading ? <>Loading...</> : "Add Test"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateTestPopup;
