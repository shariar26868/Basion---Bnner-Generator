# 🚀 Chatbot Quick Start Guide

## ⚡ 30-Second Setup

### 1. Ensure Requirements Met
```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key
```bash
# Windows
set OPENAI_API_KEY=sk-...

# macOS/Linux
export OPENAI_API_KEY=sk-...
```

### 3. Start Server
```bash
python main.py
```

### 4. Test Chatbot
Open one of these in your browser:
- **Web UI**: Open `chatbot_test.html` in browser
- **API Endpoint**: `http://localhost:8000/api/chatbot/health`

---

## 📋 What Gets Created

The chatbot module adds 4 new files to `app/service/chatbot/`:

| File | Purpose |
|------|---------|
| `chatbot_schema.py` | Data models & request/response structures |
| `chatbot_utils.py` | Documentation loading & context extraction |
| `chatbot_service.py` | AI logic & OpenAI integration |
| `chatbot_router.py` | 6 API endpoints |

Plus 3 utility files in project root:
- `CHATBOT_API.md` - Complete API documentation
- `chatbot_test.html` - Interactive web test interface
- `examples_chatbot.py` - Python examples

---

## 🎯 Core Endpoints

### `POST /api/chatbot/ask`
```bash
curl -X POST http://localhost:8000/api/chatbot/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main features?",
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### `POST /api/chatbot/ask/stream`
Real-time streaming response (SSE format)

### `GET /api/chatbot/documentation/summary`
Get loaded documentation stats

### `GET /api/chatbot/documentation/search?query=...`
Search documentation by keyword

### `POST /api/chatbot/reload-docs`
Force reload documentation from disk

### `GET /api/chatbot/health`
Check service status

---

## 💡 How It Works

```
Documentation Loading (Startup)
  ↓
README.md + other files are read
  ↓
Parsed into searchable sections
  ↓
Stored in memory (fast)

User Question
  ↓
[Relevant docs extracted based on keywords]
  ↓
[Sent to OpenAI with system prompt]
  ↓
[AI generates answer using doc context]
  ↓
[Response returned with sources & confidence]
```

---

## 🔧 Configuration Options

### Change AI Model
Edit `app/service/chatbot/chatbot_service.py`:
```python
self.model = "gpt-3.5-turbo"  # Faster, cheaper
# or
self.model = "gpt-4"          # More intelligent
```

### Adjust Default Temperature
Edit `chatbot_schema.py`:
```python
temperature: Optional[float] = Field(
    default=0.5,  # Change this (0=factual, 1=creative)
    description="Response creativity level"
)
```

### Change Documentation Max Length
Edit `chatbot_utils.py`:
```python
def get_relevant_context(self, query: str, max_chars: int = 3000) -> ...
    # Increase 3000 for more context
```

---

## 📱 Frontend Integration Examples

### React Component
```jsx
import { useState } from 'react';

export function Chatbot() {
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState('');

  const handleAsk = async () => {
    setLoading(true);
    const res = await fetch('/api/chatbot/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, max_tokens: 800 })
    });
    const data = await res.json();
    setAnswer(data.answer);
    setLoading(false);
  };

  return (
    <div>
      <input 
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={handleAsk} disabled={loading}>
        {loading ? 'Thinking...' : 'Ask'}
      </button>
      {answer && <p>{answer}</p>}
    </div>
  );
}
```

### Vanilla JavaScript
```javascript
async function askChatbot(question) {
  const response = await fetch('/api/chatbot/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });
  const data = await response.json();
  console.log(data.answer);
  return data;
}

// Usage
askChatbot("What is Basione?");
```

### Vue.js
```vue
<template>
  <div>
    <input v-model="question" @keyup.enter="askQuestion" />
    <button @click="askQuestion" :disabled="loading">
      {{ loading ? 'Thinking...' : 'Ask' }}
    </button>
    <div v-if="answer">{{ answer }}</div>
  </div>
</template>

<script>
export default {
  data() {
    return { question: '', answer: '', loading: false };
  },
  methods: {
    async askQuestion() {
      this.loading = true;
      const res = await fetch('/api/chatbot/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: this.question })
      });
      const data = await res.json();
      this.answer = data.answer;
      this.loading = false;
    }
  }
};
</script>
```

---

## 🧪 Testing

### Option 1: Web UI (Recommended for beginners)
```bash
# Open in browser:
file:///path/to/chatbot_test.html
```

### Option 2: Python Script
```bash
python examples_chatbot.py
```

### Option 3: cURL
```bash
curl -X POST http://localhost:8000/api/chatbot/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this platform?"}'
```

### Option 4: Python Requests
```python
import requests

response = requests.post(
    'http://localhost:8000/api/chatbot/ask',
    json={'question': 'What features exist?'}
)
print(response.json())
```

---

## 🐛 Troubleshooting

### "OpenAI API Error"
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Or on Windows:
echo %OPENAI_API_KEY%
```

### "Documentation not loaded"
```bash
# Reload documentation
curl -X POST http://localhost:8000/api/chatbot/reload-docs
```

### "Connection refused"
```bash
# Make sure server is running
python main.py
```

### "Answer quality is poor"
- Check documentation is loaded: `/api/chatbot/documentation/summary`
- Try rephrasing question
- Reduce temperature for more factual answers
- Increase `max_tokens` for more detailed answers

---

## 📊 Performance Tips

1. **Reduce context size** for faster responses:
   ```python
   get_relevant_context(query, max_chars=2000)  # from 3000
   ```

2. **Use gpt-3.5-turbo** instead of gpt-4:
   ```python
   self.model = "gpt-3.5-turbo"  # 10x cheaper, still good
   ```

3. **Cache responses** on frontend for common questions

4. **Limit conversation history** to last 5 messages

---

## 🔐 Security Notes

- Documentation is loaded on **startup** (not per-request)
- All API endpoints are **open to CORS** - add auth if needed
- OpenAI API key is read from **environment variables**
- No conversation history stored in database yet

---

## 🚀 Next Steps

1. ✅ Test in browser (`chatbot_test.html`)
2. ✅ Integrate into your frontend
3. ✅ Customize response parameters
4. ✅ Add user authentication if needed
5. ✅ Store conversation history in database
6. ✅ Add semantic search (vector embeddings) for better context

---

## 📚 More Resources

- Full API docs: See `CHATBOT_API.md`
- Python examples: See `examples_chatbot.py`
- OpenAI docs: https://platform.openai.com/docs/guides/gpt
- FastAPI docs: https://fastapi.tiangolo.com/

---

**Version**: 1.0.0  
**Last Updated**: May 2024  
**Status**: ✅ Production Ready
