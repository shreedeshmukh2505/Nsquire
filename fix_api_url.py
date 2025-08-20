#!/usr/bin/env python3
"""
Script to fix the API URL in Chatbot.jsx from port 5001 to port 5002
"""

def fix_api_url():
    """Fix the API URL in Chatbot.jsx file."""
    
    file_path = "src/components/Chatbot.jsx"
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the old API URL with the new one
        old_url = "http://localhost:5001/chat"
        new_url = "http://localhost:5002/chat"
        
        if old_url in content:
            content = content.replace(old_url, new_url)
            
            # Write the updated content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Successfully updated {file_path}")
            print(f"   Changed: {old_url} → {new_url}")
            return True
        else:
            print(f"⚠️  No changes needed in {file_path}")
            print(f"   Expected URL '{old_url}' not found")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Main function."""
    print("🔧 Fixing API URL in Chatbot.jsx...")
    print("=" * 50)
    
    success = fix_api_url()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 API URL fix completed!")
        print("\n📝 What was changed:")
        print("   - Chatbot.jsx now connects to port 5002")
        print("   - Your enhanced chatbot endpoint")
        print("\n🚀 Next steps:")
        print("   1. Your React frontend should now work")
        print("   2. Test by asking questions in the chat")
        print("   3. Both college and general questions will work")
    else:
        print("⚠️  No changes were made")
        print("   Check if the file exists and has the expected content")

if __name__ == "__main__":
    main()
