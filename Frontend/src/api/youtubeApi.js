// src/api/youtubeApi.js

import axios from 'axios';

const API_URL = 'http://localhost:5000'; // Update this with your backend URL

export async function uploadVideo(videoUrl, token) {
  try {
    const response = await axios.post(`${API_URL}/upload-video`, 
      { videoUrl },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  } catch (error) {
    throw error;
  }
}

export async function askQuestion(question, token) {
  try {
    const response = await axios.post(`${API_URL}/ask-question`, 
      { question },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data.answer;
  } catch (error) {
    throw error;
  }
}

export async function getChatHistory(token) {
  try {
    const response = await axios.get(`${API_URL}/chat-history`, 
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data.chat_history;
  } catch (error) {
    throw error;
  }
}

export async function clearChatHistory(token) {
  try {
    const response = await axios.post(`${API_URL}/clear-chat-history`, {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export async function refreshToken(token) {
  try {
    const response = await axios.post(`${API_URL}/refresh`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data.access_token;
  } catch (error) {
    throw error;
  }
}