# 🤖 Spandoek Chatbot API Guide

## Overview

The Spandoek Chatbot is an AI-powered system that provides intelligent answers to any questions about the website platform. It has full access to the project documentation and uses OpenAI's GPT models to generate accurate, context-aware responses.

## ✨ Features

- ✅ **Dynamic Q&A**: Ask any question about the platform
- ✅ **Documentation-Based**: Answers backed by official documentation
- ✅ **Streaming Support**: Real-time response streaming for better UX
- ✅ **Context Aware**: Understands conversational history
- ✅ **Confidence Scoring**: Know how confident the answer is
- ✅ **Source Tracking**: See which documentation sections were used
- ✅ **Auto Documentation Loading**: Reads from README.md and project files on startup

## 📡 API Endpoints

### 1. **POST** `/api/chatbot/ask` - Get Answer (Non-Streaming)

Submit a question and get a complete response immediately.

**Request Body:**
```json
{
  "question": "What are the main features of the Spandoek banner editor?",
  "temperature": 0.7,
  "max_tokens": 500,
  "conversation_history": null
}
```

**Response:**
```json
{
  "answer": "The Spandoek banner editor is powered by Fabric.js and includes:\n\n1. **Layer Management** - Organize and manage multiple design elements\n2. **Custom Image Uploads** - Add your own images...",
  "sources": ["Advanced Interactive Canvas Editor", "Key Features"],
  "confidence": 0.95,
  "is_streaming": false
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `question` | string | ✅ | - | Your question about the platform |
| `temperature` | float | ❌ | 0.7 | Response creativity (0-1, lower=more factual) |
| `max_tokens` | integer | ❌ | 500 | Max response length (max 2000) |
| `conversation_history` | array | ❌ | null | Previous messages for context |

---

### 2. **POST** `/api/chatbot/ask/stream` - Get Answer (Streaming)

Get responses in real-time as they're being generated.

**Request:**
```bash
curl -X POST http://localhost:8000/api/chatbot/ask/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I install the project?"}'
```

**Response Format:** Server-Sent Events (SSE) with JSON

```
data: {"type":"metadata","sources":["Installation"]}

data: {"type":"content","data":"To install the Spandoek project, follow "}

data: {"type":"content","data":"these steps:\n\n1. Clone the repository"}

data: {"type":"done","confidence":0.95}
```

---

### 3. **GET** `/api/chatbot/documentation/summary` - Get Docs Info

Get information about loaded documentation.

**Response:**
```json
{
  "status": "success",
  "summary": {
    "total_chars": 15234,
    "total_sections": 24,
    "section_names": [
      "Spandoek Client",
      "Key Features",
      "Advanced Interactive Canvas Editor",
      "Technology Stack"
    ],
    "last_loaded": "2024-05-21T10:30:00",
    "loaded_files": ["README", "requirements", "Dockerfile", "docker-compose"]
  },
  "message": "Documentation contains 15234 characters across 24 sections"
}
```

---

### 4. **GET** `/api/chatbot/documentation/search?query=...` - Search Docs

Search the documentation for specific topics.

**Request:**
```
GET /api/chatbot/documentation/search?query=authentication
```

**Response:**
```json
{
  "query": "authentication",
  "sections_found": ["Enterprise Authentication & Security", "Auth Middleware"],
  "context": "## Enterprise Authentication & Security\n\nFully integrated custom auth suite...",
  "total_matches": 2
}
```

---

### 5. **POST** `/api/chatbot/reload-docs` - Reload Documentation

Force reload documentation from disk (useful after updating README).

**Response:**
```json
{
  "status": "success",
  "message": "Documentation reloaded",
  "summary": {
    "total_chars": 15234,
    "total_sections": 24
  }
}
```

---

### 6. **GET** `/api/chatbot/health` - Health Check

Check if chatbot service is operational.

**Response:**
```json
{
  "status": "healthy",
  "chatbot_service": "operational",
  "documentation_loaded": true,
  "sections_available": 24,
  "timestamp": "2024-05-21T10:30:00"
}
```

---

## 🎯 Example Questions

### Frontend Questions
- "What is the Next.js version used in the client?"
- "How do I set up the development environment?"
- "What CSS framework is used for styling?"
- "How does the canvas editor work?"
- "What payment methods are supported?"

### Backend Questions
- "What is the FastAPI banner generation endpoint?"
- "How do I configure environment variables?"
- "What AI models are used in the system?"
- "How does the image generation streaming work?"

### General Questions
- "What are the main features of Spandoek?"
- "How is the project structured?"
- "What technologies are in the tech stack?"
- "How do I deploy the application?"

---

## 💻 JavaScript/TypeScript Client Example

### Basic Usage

```javascript
// Simple question with fetch
async function askChatbot(question) {
  const response = await fetch('http://localhost:8000/api/chatbot/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      temperature: 0.7,
      max_tokens: 500
    })
  });
  
  const data = await response.json();
  console.log('Answer:', data.answer);
  console.log('Sources:', data.sources);
  console.log('Confidence:', data.confidence);
}

// Usage
await askChatbot("What are the key features of Spandoek?");
```

### Streaming Response

```javascript
async function askChatbotStreaming(question) {
  const response = await fetch('http://localhost:8000/api/chatbot/ask/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const text = decoder.decode(value);
    const lines = text.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const json = JSON.parse(line.slice(6));
        
        if (json.type === 'content') {
          process.stdout.write(json.data);
        } else if (json.type === 'done') {
          console.log('\n[Confidence:', json.confidence, ']');
        }
      }
    }
  }
}

// Usage
await askChatbotStreaming("How do I install the project?");
```

### React Hook

```javascript
import { useState, useCallback } from 'react';

export function useChatbot() {
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState([]);
  const [error, setError] = useState(null);
  
  const askQuestion = useCallback(async (question) => {
    setLoading(true);
    setError(null);
    setAnswer('');
    
    try {
      const response = await fetch('/api/chatbot/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, max_tokens: 800 })
      });
      
      if (!response.ok) throw new Error('Network response was not ok');
      
      const data = await response.json();
      setAnswer(data.answer);
      setSources(data.sources);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);
  
  return { answer, loading, sources, error, askQuestion };
}

// Usage in component
function ChatWidget() {
  const { answer, loading, askQuestion } = useChatbot();
  const [input, setInput] = useState('');
  
  return (
    <div>
      <input 
        value={input} 
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask about the platform..."
      />
      <button onClick={() => askQuestion(input)} disabled={loading}>
        {loading ? 'Thinking...' : 'Ask'}
      </button>
      {answer && <div className="answer">{answer}</div>}
    </div>
  );
}
```

---

## 🐍 Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/chatbot"

def ask_chatbot(question: str):
    """Ask chatbot a question"""
    response = requests.post(
        f"{BASE_URL}/ask",
        json={
            "question": question,
            "temperature": 0.7,
            "max_tokens": 500
        }
    )
    
    data = response.json()
    print(f"Answer: {data['answer']}")
    print(f"Sources: {', '.join(data['sources'])}")
    print(f"Confidence: {data['confidence']}")
    return data

def stream_answer(question: str):
    """Stream answer in real-time"""
    response = requests.post(
        f"{BASE_URL}/ask/stream",
        json={"question": question},
        stream=True
    )
    
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode().replace('data: ', ''))
            if data['type'] == 'content':
                print(data['data'], end='', flush=True)
            elif data['type'] == 'done':
                print(f"\n[Confidence: {data['confidence']}]")

def search_docs(query: str):
    """Search documentation"""
    response = requests.get(
        f"{BASE_URL}/documentation/search",
        params={"query": query}
    )
    
    data = response.json()
    print(f"Found sections: {data['sections_found']}")
    print(f"Context:\n{data['context']}")
    return data

# Usage
if __name__ == "__main__":
    ask_chatbot("What are the main technologies used?")
    stream_answer("How do I get started?")
    search_docs("authentication")
```

---

## � Frontend Integration

Your Next.js frontend can use the API endpoints directly. See the `chatbot_test.html` for an example web interface.

### Prerequisites
```bash
# Ensure Python 3.10+ and OpenAI API key
export OPENAI_API_KEY="sk-..."
```

### Installation
The chatbot module is automatically loaded when you start the FastAPI server.

```bash
# Install dependencies (if needed)
pip install -r requirements.txt

# Start the server
python main.py
```

The chatbot will:
1. Load documentation from `README.md` on startup
2. Parse it into searchable sections
3. Be ready to answer questions at `/api/chatbot/ask`

---

## 🎨 Architecture

### Components

1. **`chatbot_schema.py`** - Pydantic models for requests/responses
2. **`chatbot_utils.py`** - Documentation loading & context extraction
3. **`chatbot_service.py`** - Core AI logic using OpenAI
4. **`chatbot_router.py`** - FastAPI routes & endpoints

### Flow

```
User Question
    ↓
[chatbot_router.py] - Receive request
    ↓
[chatbot_service.py] - Process with AI
    ↓
[chatbot_utils.py] - Extract relevant docs
    ↓
OpenAI API
    ↓
Generate Answer
    ↓
Return Response (or Stream)
```

---

## 🚀 Advanced Features

### Multi-turn Conversations

```json
{
  "question": "Tell me more about the pricing",
  "conversation_history": [
    {
      "role": "user",
      "content": "What features does Spandoek have?"
    },
    {
      "role": "assistant",
      "content": "Spandoek has advanced banner editor, AI generation..."
    }
  ]
}
```

### Fine-tune Response Quality

- **Lower temperature** (0.3-0.5): More factual, consistent
- **Higher temperature** (0.8-1.0): More creative, diverse
- **Longer max_tokens**: More detailed answers
- **Shorter max_tokens**: Quick summaries

---

## 📝 Notes

- Documentation is loaded on **startup** for performance
- Manual reload available at `/api/chatbot/reload-docs`
- All responses are **confidence-scored** (0-1)
- **Sources** show which docs were referenced
- Supports **streaming** for real-time responses
- **CORS enabled** for all origins

---

## ❓ FAQ

**Q: How is documentation loaded?**
A: Automatically from `README.md` and other files on startup. Can be reloaded manually.

**Q: Can I use different AI models?**
A: Yes, edit `model = "gpt-4-turbo"` in `chatbot_service.py` to use `gpt-3.5-turbo`, etc.

**Q: How accurate are the answers?**
A: Accuracy depends on documentation quality. Confidence score indicates reliability.

**Q: Can I store conversation history?**
A: Yes, use `conversation_history` parameter for multi-turn conversations.

**Q: How much does it cost?**
A: OpenAI charges per API call. See their pricing page for details.

---

## 🔗 Related Endpoints

- **Banner Generation**: `POST /generate`
- **Image Serving**: `GET /images/{filename}`
- **Health Check**: `GET /health`
- **Chatbot Health**: `GET /api/chatbot/health`

---

**Version**: 1.0.0  
**Last Updated**: May 2024  
**Status**: ✅ Production Ready
