import React, { useState } from 'react';

function VideoUpload() {
  const [url, setUrl] = useState('');

  const handleUpload = () => {
    console.log('Uploading video:', url);
    // Here you would typically send a request to your backend
  };

  return (
    <div>
      <h3>Upload YouTube Video</h3>
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter YouTube URL"
      />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}

export default VideoUpload;