import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

console.log("React Entry Point Loading...");

try {
  const rootElement = document.getElementById("root");
  if (!rootElement) {
    throw new Error("Root element not found");
  }

  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
  console.log("React Root Rendered successfully");
} catch (error) {
  console.error("Critical React Mount Error:", error);
  document.body.innerHTML = `<div style="color:red; padding: 20px;">
    <h1>Critical Error</h1>
    <pre>${String(error)}</pre>
  </div>`;
}
