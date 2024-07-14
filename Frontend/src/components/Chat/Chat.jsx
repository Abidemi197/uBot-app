import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { uploadVideo, askQuestion, getChatHistory, clearChatHistory } from '../../api/youtubeApi';
import styles from './Chat.module.css';
import { FaUpload, FaPaperPlane, FaTrash } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';

function Chat() {
  const [input, setInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [videoUploaded, setVideoUploaded] = useState(false);
  const { user } = useAuth();
  const chatHistoryRef = useRef(null);

  useEffect(() => {
    fetchChatHistory();
  }, []);

  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const fetchChatHistory = async () => {
    setIsLoading(true);
    try {
      const history = await getChatHistory(user.token);
      setChatHistory(history);
      setVideoUploaded(history.some(chat => chat.question === "Video Summary"));
    } catch (err) {
      setError('Failed to fetch chat history. Please try again.');
    }
    setIsLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    if (!videoUploaded) {
      await handleVideoUpload(e);
    } else {
      await handleQuestionSubmit(e);
    }
  };

  const handleVideoUpload = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await uploadVideo(input, user.token);
      setVideoUploaded(true);
      await fetchChatHistory();
      setInput('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload video. Please try again.');
    }
    setIsLoading(false);
  };

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const answer = await askQuestion(input, user.token);
      setChatHistory(prevHistory => [...prevHistory, { question: input, response: answer }]);
      setInput('');
    } catch (err) {
      if (err.response?.data?.error === "No video uploaded yet. Please upload a video first.") {
        setError("Please upload a video before asking questions.");
      } else {
        setError(err.response?.data?.error || 'Failed to get an answer. Please try again.');
      }
    }
    setIsLoading(false);
  };

  const handleClearChat = async () => {
    setIsLoading(true);
    try {
      await clearChatHistory(user.token);
      setChatHistory([]);
      setVideoUploaded(false);
    } catch (err) {
      setError('Failed to clear chat history. Please try again.');
    }
    setIsLoading(false);
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHistory} ref={chatHistoryRef}>
        {chatHistory.length > 0 ? (
          chatHistory.map((chat, index) => (
            <div key={index} className={styles.chatEntry}>
              <p className={styles.userMessage}><strong>You:</strong> {chat.question}</p>
              <div className={styles.botMessage}>
                <strong>Bot:</strong> 
                <ReactMarkdown>{chat.response}</ReactMarkdown>
              </div>
            </div>
          ))
        ) : (
          <p className={styles.noChatMessage}>No chat history yet. Upload a video to get started!</p>
        )}
      </div>
      <div className={styles.inputArea}>
        <form className={styles.form} onSubmit={handleSubmit}>
          <button 
            type="button" 
            onClick={handleVideoUpload} 
            disabled={isLoading} 
            className={styles.iconButton}
            title="Upload Video"
          >
            <FaUpload />
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter YouTube URL or ask a question"
            required
            className={styles.input}
          />
          <button 
            type="submit" 
            disabled={isLoading || !input.trim()} 
            className={styles.iconButton}
            title="Send"
          >
            <FaPaperPlane />
          </button>
        </form>
        <button 
          onClick={handleClearChat} 
          disabled={isLoading} 
          className={styles.clearButton}
          title="Clear Chat History"
        >
          <FaTrash />
        </button>
        {isLoading && <div className={styles.loading}></div>}
        {error && <p className={styles.error}>{error}</p>}
      </div>
    </div>
  );
}

export default Chat;