import React, { useState } from 'react';

function KnowledgeBase() {
  const [urls, setUrls] = useState([]);
  const [newUrl, setNewUrl] = useState('');

  const handleAddUrl = () => {
    if (newUrl.trim() && urls.length < 10) {
      setUrls([...urls, newUrl]);
      setNewUrl('');
    }
  };

  return (
    <div>
      <h2>Knowledge Base</h2>
      <div>
        <input
          type="text"
          value={newUrl}
          onChange={(e) => setNewUrl(e.target.value)}
          placeholder="Enter YouTube URL"
        />
        <button onClick={handleAddUrl}>Add URL</button>
      </div>
      <ul>
        {urls.map((url, index) => (
          <li key={index}>{url}</li>
        ))}
      </ul>
    </div>
  );
}

export default KnowledgeBase;