import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { API_BASE_URL } from '../../../config';

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
      <h3>LLM List</h3>
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
                }}>
                  <input name="name" value={editingLLM.name} onChange={handleChange} />
                  <input name="description" value={editingLLM.description || ''} onChange={handleChange} />
                  <input name="llm_model_id" value={editingLLM.llm_model_id || ''} onChange={handleChange} />
                  <input name="aws_region" value={editingLLM.aws_region || ''} onChange={handleChange} />
                  <input name="access_key" value={editingLLM.access_key || ''} onChange={handleChange} />
                  <input name="secret_access_key" value={editingLLM.secret_access_key || ''} onChange={handleChange} />
                  <input name="selected" type="checkbox" checked={editingLLM.selected || false} onChange={handleChange} />
                  <button type="submit">Save</button>
                  <button onClick={() => setEditingLLM(null)}>Cancel</button>
                </form>
              ) : (
                <>
                  <strong>{llm.name}</strong>
                  {llm.description && <p>{llm.description}</p>}
                  {llm.llm_model_id && <p>Model ID: {llm.llm_model_id}</p>}
                  {llm.aws_region && <p>AWS Region: {llm.aws_region}</p>}
                  <button onClick={() => handleEdit(llm)}>Edit</button>
                  <button onClick={() => deleteLLM(llm.id)}>Delete</button>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default LLMList;
