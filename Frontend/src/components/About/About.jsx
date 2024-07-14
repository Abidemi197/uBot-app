// src/components/About/About.jsx

import React from 'react';
import './About.css'; // We'll create this CSS file for styling

function About() {
  return (
    <div className="about-container">
      <h1>Welcome to YouBot</h1>
      
      <section className="app-description">
        <h2>What is YouBot?</h2>
        <p>
          YouBot is a Retrieval-Augmented Generation (RAG) application that can help you extract information from youtube faster than ever.
           By combining advanced natural language processing with 
          video content analysis, YouBot provides intelligent responses based on the information extracted 
          from YouTube videos.
        </p>
      </section>

      <section className="features">
        <h2>Key Features</h2>
        <ul>
          <li>Video-based Question Answering: Ask questions about uploaded YouTube videos and receive accurate answers.</li>
          <li>Knowledge Base: upload and query multiple videos at the same time.</li>
          <li>Automatic Video Summarization: Get concise summaries of uploaded videos.</li>
        </ul>
      </section>

      <section className="how-to-use">
        <h2>How to Use YouBot</h2>
        <ol>
          <li>Sign Up: Create a new account or log in if you're a returning user.</li>
          <li>Upload a Videos: On the Chat page, enter a YouTube URL to upload a video for analysis(an auto summary will be provided).</li>
          <li>Ask Questions: Once a video is uploaded, ask questions about its content.</li>
          <li>Multiple videos can be uploaded into knowledge base, number of videos depends on average length</li>
          <li>Use clear history button to start a fresh knowledge base and chat</li>
          <li>Explore Answers: Receive AI-generated answers based on all the video content provided.</li>
        </ol>
      </section>

      <section className="technology-stack">
        <h2>Technology Stack</h2>
        <ul>
          <li>Frontend: React with Vite for a fast, modern user interface</li>
          <li>Backend: Flask for a robust Python-based server</li>
          <li>Database: SQLite for efficient data storage</li>
          <li>AI Integration: Utilizes advanced NLP models for video analysis and question answering</li>
          <li>Authentication: JWT for secure user sessions</li>
        </ul>
      </section>

      <section className="creator-info">
        <h2>About the Creator</h2>
        <p>YouBot was developed by Abidemi Salami, a passionate AI enthusiast dedicated to utilizing AI to its fullest potential.</p>
        <p>Connect with Abidemi:</p>
        <ul>
          <li>LinkedIn: <a href="https://linkedin.com/in/abidemi-salami-26095426a" target="_blank" rel="noopener noreferrer">Abidemi Salami</a></li>
          <li>GitHub: <a href="https://github.com/Abidemi197?tab=repositories" target="_blank" rel="noopener noreferrer">Abidemi197</a></li>
        </ul>
      </section>
    </div>
  );
}

export default About;