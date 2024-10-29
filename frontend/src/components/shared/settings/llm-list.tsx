import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { API_BASE_URL } from '../../../config';
import styles from './settings.module.css';
import { Edit2, Trash2 } from "lucide-react";

interface LLM {
  id: string;
  name: string;
  description: string | null;
  llm_model_id: string | null;
  aws_region: string | null;
  access_key: string | null;
  secret_access_key: string | null;
  selected: boolean;
}

const LLMList: React.FC = () => {
  const [llms, setLLMs] = useState<LLM[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingLLM, setEditingLLM] = useState<LLM | null>(null);

  useEffect(() => {
    fetchLLMs();
  }, []);

  const fetchLLMs = async () => {
    try {
      const response = await axios.get<LLM[]>(`${API_BASE_URL}/llms`);
      setLLMs(response.data);
      setLoading(false);
    } catch (error: any) {
      toast.error(error?.response?.data?.detail);
      setError('Failed to fetch LLMs');
      setLoading(false);
    }
  };

  const deleteLLM = async (id: string) => {
    try {
      await axios.delete(`${API_BASE_URL}/llm/${id}`);
      fetchLLMs();
      toast.success('LLM deleted successfully');
    } catch (error: any) {
      toast.error(error?.response?.data?.detail);
      setError('Failed to delete LLM');
    }
  };

  const updateLLM = async (llm: LLM) => {
    try {
      await axios.put(`${API_BASE_URL}/llm/${llm.id}`, llm);
      setEditingLLM(null);
      fetchLLMs();
      toast.success('LLM updated successfully');
    } catch (error: any) {
      toast.error(error?.response?.data?.detail);
      setError('Failed to update LLM');
    }
  };

  const handleEdit = (llm: LLM) => {
    setEditingLLM(llm);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (editingLLM) {
      setEditingLLM({
        ...editingLLM,
        [e.target.name]: e.target.value,
      });
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {llms.length === 0 ? (
        <p>No LLMs found.</p>
      ) : (
        <ul>
          {llms.map((llm) => (
            <li key={llm.id}>
              {editingLLM && editingLLM.id === llm.id ? (
                <form onSubmit={(e) => {
                  e.preventDefault();
                  updateLLM(editingLLM);
                }} className={styles.form}>
                  <input name="name" value={editingLLM.name} onChange={handleChange} className={styles.input} />
                  <input name="description" value={editingLLM.description || ''} onChange={handleChange} className={styles.input} />
                  <input name="llm_model_id" value={editingLLM.llm_model_id || ''} onChange={handleChange} className={styles.input} />
                  <div className={styles.buttonContainer}>
                    <button type="submit">Save</button>
                    <button onClick={() => setEditingLLM(null)}>Cancel</button>
                  </div>
                </form>
              ) : (
                <div className={styles.llmItem}>
                  <strong className={styles.llmName}>{llm.name}</strong>
                  {llm.description && <p className={styles.llmDescription}>{llm.description}</p>}
                  {llm.llm_model_id && <p className={styles.llmModelId}>Model ID: {llm.llm_model_id}</p>}
                  {llm.aws_region && <p className={styles.llmAwsRegion}>AWS Region: {llm.aws_region}</p>}
                  <div className={styles.buttonContainerList}>
                    <button onClick={() => handleEdit(llm)}>
                      <Edit2 className="h-5 w-5 mr-2" style={{ color: 'black' }} />
                    </button>
                    <button onClick={() => deleteLLM(llm.id)}>
                      <Trash2 className="h-5 w-5 mr-2" style={{ color: 'black' }} />
                    </button>
                  </div>
                  <hr className={styles.hr} />
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default LLMList;
