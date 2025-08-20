#!/usr/bin/env python3
"""
Test script for the enhanced EDI chatbot with college database integration and Llama 3 local support.
"""

import requests
import json

def test_enhanced_chatbot():
    """Test the enhanced chatbot with various types of queries."""
    
    base_url = "http://localhost:5002"
    
    # Test queries
    test_queries = [
        # College search queries
        "Find colleges in Pune",
        "Search for engineering colleges",
        "Which colleges offer Computer Science?",
        
        # Cutoff queries
        "What is the cutoff for COEP Computer Science?",
        "Tell me about PICT cutoff for IT branch",
        "What rank do I need for VIT?",
        
        # College info queries
        "Tell me about COEP",
        "Give me information about PICT",
        "What are the details of VIT Pune?",
        
        # Branch queries
        "What branches are available at COEP?",
        "Tell me about Computer Science at PICT",
        "What courses does VIT offer?",
        
        # General queries (will use Llama 3 local)
        "What is artificial intelligence?",
        "How to prepare for engineering entrance exams?",
        "What are the benefits of studying engineering?",
        "Tell me a joke",
        "What's the weather like today?"
    ]
    
    print("🚀 Testing Enhanced EDI Chatbot...")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"message": query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {result['response'][:200]}...")
                if len(result['response']) > 200:
                    print(f"   ... (truncated, full length: {len(result['response'])} characters)")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        print()
    
    print("🎉 Testing completed!")

def test_college_database_endpoints():
    """Test the college database endpoints."""
    
    base_url = "http://localhost:5002"
    
    print("\n🔍 Testing College Database Endpoints...")
    print("=" * 60)
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            health_data = response.json()
            print(f"   Features: {', '.join(health_data['features'])}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test database stats
    try:
        response = requests.get(f"{base_url}/database-stats")
        if response.status_code == 200:
            print("✅ Database stats retrieved")
            stats = response.json()
            print(f"   Colleges: {stats.get('total_colleges', 'N/A')}")
            print(f"   Branches: {stats.get('total_branches', 'N/A')}")
            print(f"   Cutoffs: {stats.get('total_cutoffs', 'N/A')}")
        else:
            print(f"❌ Database stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Database stats error: {e}")
    
    # Test college search
    try:
        response = requests.get(f"{base_url}/colleges?search=COEP")
        if response.status_code == 200:
            print("✅ College search working")
            colleges = response.json().get('colleges', [])
            print(f"   Found {len(colleges)} colleges matching 'COEP'")
            if colleges:
                print(f"   First result: {colleges[0]['college_name']}")
        else:
            print(f"❌ College search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ College search error: {e}")

if __name__ == "__main__":
    print("🧪 Enhanced EDI Chatbot Test Suite")
    print("=" * 60)
    
    # First test the endpoints
    test_college_database_endpoints()
    
    # Then test the chatbot
    test_enhanced_chatbot()
    
    print("\n🎯 Test Summary:")
    print("   - College database endpoints tested")
    print("   - Chatbot functionality tested")
    print("   - Various query types tested")
    print("\n💡 To use the chatbot:")
    print("   1. Make sure the enhanced server is running on port 5002")
    print("   2. Send POST requests to /chat with JSON: {'message': 'your question'}")
    print("   3. The chatbot will automatically:")
    print("      - Classify your query type")
    print("      - Search the college database if relevant")
    print("      - Use Llama 3 local for general questions")
    print("      - Fall back to Cohere if needed")
