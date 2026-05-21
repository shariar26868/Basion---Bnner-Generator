# 🚀 Chatbot Quick Start Guide - Python Version

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
```bash
# Option A: Run Python examples
python examples_chatbot.py

# Option B: Open HTML interface in browser
Open: chatbot_test.html

# Option C: Check API status
curl http://localhost:8000/api/chatbot/health
```

---

## 📋 What Gets Created

The chatbot module adds 4 new files to `app/service/chatbot/`:

| File | Purpose |
|------|---------|
| `chatbot_schema.py` | Data models & request/response structures |
| `chatbot_utils.py` | Documentation loading & context extraction |
| `chatbot_service.py` | AI logic & OpenAI integration |
| `chatbot_router.py` | 6 API endpoints |

Plus utility files in project root:
- `CHATBOT_API_CLEAN.md` - Python-focused API documentation
- `examples_chatbot.py` - Complete Python examples
- `chatbot_test.html` - Web test interface

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

## 🐍 Python Client Integration Examples

### Simple Question

```python
import requests

response = requests.post(
    'http://localhost:8000/api/chatbot/ask',
    json={'question': 'What is Basione?'}
)
data = response.json()
print(f"Answer: {data['answer']}")
print(f"Confidence: {data['confidence']}")
```

### With Parameters

```python
import requests

response = requests.post(
    'http://localhost:8000/api/chatbot/ask',
    json={
        'question': 'How do I install the project?',
        'temperature': 0.5,
        'max_tokens': 300
    }
)
data = response.json()
print(data['answer'])
```

### Streaming Response

```python
import json
import requests

response = requests.post(
    'http://localhost:8000/api/chatbot/ask/stream',
    json={'question': 'What features exist?'},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode().replace('data: ', ''))
        if data['type'] == 'content':
            print(data['data'], end='', flush=True)
        elif data['type'] == 'done':
            print(f"\n[Confidence: {data['confidence']}]")
```

### Search Documentation

```python
import requests

response = requests.get(
    'http://localhost:8000/api/chatbot/documentation/search',
    params={'query': 'authentication'}
)
data = response.json()
print(f"Found sections: {data['sections_found']}")
```

### Multi-turn Conversation

```python
import requests

# First question
response1 = requests.post(
    'http://localhost:8000/api/chatbot/ask',
    json={'question': 'What is Basione?'}
)
answer1 = response1.json()['answer']

# Follow-up with history
response2 = requests.post(
    'http://localhost:8000/api/chatbot/ask',
    json={
        'question': 'Tell me more about the features',
        'conversation_history': [
            {'role': 'user', 'content': 'What is Basione?'},
            {'role': 'assistant', 'content': answer1}
        ]
    }
)
print(response2.json()['answer'])
```

### Using asyncio (Async)

```python
import aiohttp
import asyncio

async def ask_chatbot(question: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:8000/api/chatbot/ask',
            json={'question': question}
        ) as response:
            data = await response.json()
            return data['answer']

# Usage
answer = asyncio.run(ask_chatbot("What is the tech stack?"))
print(answer)
```

### Complete Example Script

```python
#!/usr/bin/env python3
"""
Complete example of using the chatbot API
"""

import requests
import json
from typing import Optional, List

class ChatbotClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/chatbot"):
        self.base_url = base_url
    
    def ask(
        self,
        question: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        history: Optional[List[dict]] = None
    ) -> dict:
        """Ask a question"""
        payload = {
            "question": question,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "conversation_history": history
        }
        
        response = requests.post(f"{self.base_url}/ask", json=payload)
        return response.json()
    
    def search(self, query: str) -> dict:
        """Search documentation"""
        response = requests.get(
            f"{self.base_url}/documentation/search",
            params={"query": query}
        )
        return response.json()
    
    def get_summary(self) -> dict:
        """Get documentation summary"""
        response = requests.get(f"{self.base_url}/documentation/summary")
        return response.json()
    
    def health_check(self) -> dict:
        """Check service status"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Usage
if __name__ == "__main__":
    client = ChatbotClient()
    
    # Simple question
    result = client.ask("What are the main features?")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
    
    # Search docs
    search_result = client.search("authentication")
    print(f"\nFound: {search_result['sections_found']}")
    
    # Check health
    health = client.health_check()
    print(f"\nStatus: {health['status']}")
```

---

## 🧪 Testing

### Option 1: Run Python Examples
```bash
python examples_chatbot.py
```

### Option 2: Use Interactive Shell
```bash
python

>>> import requests
>>> r = requests.post('http://localhost:8000/api/chatbot/ask', 
...                   json={'question': 'What is Basione?'})
>>> print(r.json()['answer'])
```

### Option 3: cURL Commands
```bash
# Simple question
curl -X POST http://localhost:8000/api/chatbot/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this platform?"}'

# With options
curl -X POST http://localhost:8000/api/chatbot/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I install?","temperature":0.5}'

# Search docs
curl "http://localhost:8000/api/chatbot/documentation/search?query=feature"

# Health check
curl http://localhost:8000/api/chatbot/health
```

### Option 4: HTML Web Interface
```bash
# Open in browser
chatbot_test.html
```

---

## 🔧 Installation & Setup

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

## 📊 Performance Tips

1. **Reduce context size** for faster responses:
   ```python
   # In chatbot_utils.py
   get_relevant_context(query, max_chars=2000)  # from 3000
   ```

2. **Use gpt-3.5-turbo** instead of gpt-4:
   ```python
   # In chatbot_service.py
   self.model = "gpt-3.5-turbo"  # 10x cheaper, still good
   ```

3. **Cache responses** for common questions

4. **Limit conversation history** to last 5 messages

---

## 🐛 Troubleshooting

### "OpenAI API Error"
```bash
# Check API key is set
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# If empty, set it:
export OPENAI_API_KEY=sk-...
```

### "Documentation not loaded"
```bash
# Reload docs
curl -X POST http://localhost:8000/api/chatbot/reload-docs
```

### "Connection refused"
```bash
# Make sure server is running
python main.py
```

### "Answer quality is poor"
- Check docs are loaded: `/api/chatbot/documentation/summary`
- Try rephrasing question
- Reduce temperature for more factual answers (0.3-0.5)
- Increase `max_tokens` for more detailed answers

---

## 🔐 Security Notes

- OpenAI API key in environment variables (not hardcoded) ✅
- CORS enabled (add auth if needed for production)
- Input validation on all requests ✅
- Error handling & logging ✅
- No conversation history stored by default

---

## 🚀 Next Steps

1. ✅ Test with examples: `python examples_chatbot.py`
2. ✅ Integrate into your Python backend
3. ✅ Customize response parameters
4. ✅ Add user authentication if needed
5. ✅ Store conversation history in database
6. ✅ Add semantic search with vector embeddings

---

## 📚 More Resources

- Full API docs: See `CHATBOT_API_CLEAN.md`
- Python examples: See `examples_chatbot.py`
- OpenAI docs: https://platform.openai.com/docs/guides/gpt
- FastAPI docs: https://fastapi.tiangolo.com/

---

**Version**: 1.0.0  
**Last Updated**: May 2024  
**Status**: ✅ Python-Only, Production Ready
