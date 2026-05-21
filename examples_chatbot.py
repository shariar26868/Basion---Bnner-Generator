"""
Chatbot API Examples - Quick reference for using the Basione chatbot

Run this file with: python examples_chatbot.py
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000/api/chatbot"


async def example_1_simple_question():
    """Example 1: Ask a simple question"""
    print("\n" + "="*60)
    print("Example 1: Simple Question")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "question": "What are the main technologies used in Basione?",
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        async with session.post(f"{BASE_URL}/ask", json=payload) as response:
            data = await response.json()
            
            print(f"\n📝 Question: {payload['question']}")
            print(f"\n✅ Answer:\n{data['answer']}")
            print(f"\n📚 Sources: {', '.join(data['sources'])}")
            print(f"\n🎯 Confidence: {data['confidence']:.2%}")


async def example_2_streaming_response():
    """Example 2: Get streaming response"""
    print("\n" + "="*60)
    print("Example 2: Streaming Response")
    print("="*60)
    
    payload = {"question": "How do I set up the project locally?"}
    
    async with aiohttp.ClientSession() as session:
        print(f"\n📝 Question: {payload['question']}")
        print("\n✅ Answer (streaming):")
        print("-" * 40)
        
        async with session.post(f"{BASE_URL}/ask/stream", json=payload) as response:
            async for line in response.content:
                if line:
                    text = line.decode('utf-8').strip()
                    if text.startswith("data: "):
                        try:
                            data = json.loads(text[6:])
                            if data.get('type') == 'content':
                                print(data.get('data', ''), end='', flush=True)
                        except json.JSONDecodeError:
                            pass
        
        print("\n" + "-" * 40)


async def example_3_search_documentation():
    """Example 3: Search documentation"""
    print("\n" + "="*60)
    print("Example 3: Search Documentation")
    print("="*60)
    
    search_query = "authentication"
    
    async with aiohttp.ClientSession() as session:
        params = {"query": search_query}
        
        async with session.get(
            f"{BASE_URL}/documentation/search",
            params=params
        ) as response:
            data = await response.json()
            
            print(f"\n🔍 Search Query: {search_query}")
            print(f"\n📚 Sections Found:")
            for section in data['sections_found']:
                print(f"  • {section}")
            
            print(f"\n📄 Context Preview:")
            print("-" * 40)
            print(data['context'][:500] + "...")
            print("-" * 40)


async def example_4_documentation_summary():
    """Example 4: Get documentation summary"""
    print("\n" + "="*60)
    print("Example 4: Documentation Summary")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/documentation/summary") as response:
            data = await response.json()
            
            summary = data['summary']
            print(f"\n📊 Documentation Summary:")
            print(f"  • Total Characters: {summary['total_chars']:,}")
            print(f"  • Total Sections: {summary['total_sections']}")
            print(f"  • Loaded Files: {', '.join(summary['loaded_files'])}")
            print(f"  • Last Loaded: {summary['last_loaded']}")
            
            print(f"\n📋 Available Sections:")
            for section in summary['section_names'][:10]:
                print(f"  • {section}")
            if len(summary['section_names']) > 10:
                print(f"  ... and {len(summary['section_names']) - 10} more")


async def example_5_health_check():
    """Example 5: Health check"""
    print("\n" + "="*60)
    print("Example 5: Health Check")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/health") as response:
            data = await response.json()
            
            status_icon = "✅" if data['status'] == 'healthy' else "⚠️"
            print(f"\n{status_icon} Service Status: {data['status']}")
            print(f"  • Chatbot Service: {data['chatbot_service']}")
            print(f"  • Documentation Loaded: {data['documentation_loaded']}")
            print(f"  • Sections Available: {data['sections_available']}")


async def example_6_contextual_question():
    """Example 6: Question with context (conversation history)"""
    print("\n" + "="*60)
    print("Example 6: Contextual Question (Multi-turn)")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        # First question
        payload1 = {
            "question": "What frontend framework is used?",
        }
        
        print(f"\n📝 Question 1: {payload1['question']}")
        
        async with session.post(f"{BASE_URL}/ask", json=payload1) as response:
            data1 = await response.json()
            print(f"✅ Answer: {data1['answer'][:200]}...")
        
        # Follow-up question with context
        payload2 = {
            "question": "What are its main advantages?",
            "conversation_history": [
                {
                    "role": "user",
                    "content": payload1["question"]
                },
                {
                    "role": "assistant",
                    "content": data1['answer'][:500]
                }
            ]
        }
        
        print(f"\n📝 Question 2: {payload2['question']}")
        
        async with session.post(f"{BASE_URL}/ask", json=payload2) as response:
            data2 = await response.json()
            print(f"✅ Answer: {data2['answer'][:200]}...")


async def example_7_custom_parameters():
    """Example 7: Customize response parameters"""
    print("\n" + "="*60)
    print("Example 7: Custom Parameters (Temperature & Tokens)")
    print("="*60)
    
    question = "What is the banner editor?"
    
    async with aiohttp.ClientSession() as session:
        # Low temperature - factual response
        print("\n❄️  Low Temperature (0.2) - Factual:")
        print("-" * 40)
        
        payload = {
            "question": question,
            "temperature": 0.2,
            "max_tokens": 200
        }
        
        async with session.post(f"{BASE_URL}/ask", json=payload) as response:
            data = await response.json()
            print(data['answer'])
        
        # High temperature - creative response
        print("\n\n🔥 High Temperature (0.9) - Creative:")
        print("-" * 40)
        
        payload = {
            "question": question,
            "temperature": 0.9,
            "max_tokens": 200
        }
        
        async with session.post(f"{BASE_URL}/ask", json=payload) as response:
            data = await response.json()
            print(data['answer'])


async def example_8_multiple_questions():
    """Example 8: Ask multiple questions"""
    print("\n" + "="*60)
    print("Example 8: Multiple Questions")
    print("="*60)
    
    questions = [
        "What is Basione?",
        "What backend technology is used?",
        "How do I start development?",
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, question in enumerate(questions, 1):
            payload = {"question": question, "max_tokens": 250}
            
            async with session.post(f"{BASE_URL}/ask", json=payload) as response:
                data = await response.json()
                
                print(f"\n🔹 Question {i}: {question}")
                print(f"✅ Answer: {data['answer'][:300]}...")
                print(f"📚 Sources: {', '.join(data['sources']) if data['sources'] else 'General'}")


async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  🤖 Basione Chatbot API - Usage Examples  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Run all examples
        await example_1_simple_question()
        await example_2_streaming_response()
        await example_3_search_documentation()
        await example_4_documentation_summary()
        await example_5_health_check()
        await example_6_contextual_question()
        await example_7_custom_parameters()
        await example_8_multiple_questions()
        
        print("\n\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60 + "\n")
        
    except aiohttp.ClientConnectorError:
        print("\n❌ ERROR: Could not connect to the API server")
        print("Make sure the server is running at http://localhost:8000")
        print("\nStart server with: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
