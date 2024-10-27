import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import Projects from "./components/main";
import ProjectDetails from "./components/project-details/project-details";
import PromptDetails from "./components/prompt-details/prompt-details";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ToastContainer hideProgressBar={true} newestOnTop={true} />
      <Routes>
        <Route path="/" element={<Projects />} />
        <Route path="/project/:projectId" element={<ProjectDetails />} />
        <Route path="/project/:projectId/prompt/:promptId" element={<PromptDetails />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
