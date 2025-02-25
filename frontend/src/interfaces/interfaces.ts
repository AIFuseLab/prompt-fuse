import React from "react";

export interface IPromptTemplate {
  id: string;
  name: string;
  description: string | null;
  creation_date: string;
  updated_at: string;
  number_of_prompts: number;
  project_id: string | null;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  creation_date: string;
  last_updated: string;
}
