import React, { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { API_BASE_URL } from "../../../config";

interface Project {
  id: number;
  name: string;
  description: string;
  creation_date: string;
  last_updated: string;
}

interface ProjectPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onProjectSaved: (project: Project) => void;
  project?: Project;
}


function ProjectPopup({
  isOpen,
  onClose,
  onProjectSaved,
  project
}: ProjectPopupProps) {
  const [currentProject, setCurrentProject] = useState({ name: "", description: "" });
  const isEditing = !!project;

  useEffect(() => {
    if (project) {
      setCurrentProject({ name: project.name, description: project.description });
    } else {
      setCurrentProject({ name: "", description: "" });
    }
  }, [project]);

  const saveProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let response;
      if (isEditing) {
        response = await axios.put<Project>(
          `${API_BASE_URL}/project/${project.id}`,
          currentProject
        );
      } else {
        response = await axios.post<Project>(
          `${API_BASE_URL}/project`,
          currentProject
        );
      }
      onProjectSaved(response.data);
      setCurrentProject({ name: "", description: "" });
      onClose();
      toast.success('Project saved successfully');
    } catch (error: any) {
      toast.error(error?.response?.data?.message);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-4 text-black">
          {isEditing ? 'Edit Project' : 'Create New Project'}
        </h2>
        <input
          type="text"
          placeholder="Project Name"
          className="w-full mb-4 p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black"
          value={currentProject.name}
          onChange={(e) =>
            setCurrentProject({ ...currentProject, name: e.target.value })
          }
          required
        />
        <textarea
          placeholder="Project Description"
          className="w-full mb-4 p-2 border border-gray-300 rounded resize-none focus:outline-none focus:ring-2 focus:ring-black"
          value={currentProject.description}
          onChange={(e) =>
            setCurrentProject({ ...currentProject, description: e.target.value })
          }
          required
        />
        <div className="flex justify-end">
          <button
            className="px-4 py-2 bg-white text-black border border-black rounded mr-2 hover:bg-gray-100"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800"
            onClick={saveProject}
          >
            {isEditing ? 'Update Project' : 'Create Project'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProjectPopup;
