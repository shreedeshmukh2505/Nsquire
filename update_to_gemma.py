#!/usr/bin/env python3
"""
Script to update model names from deepseek-r1:1.5b to gemma3:1b
"""

import os

def update_file(file_path, old_string, new_string):
    """Update a file by replacing old_string with new_string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_string in content:
            content = content.replace(old_string, new_string)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"⚠️  No changes needed in {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all files."""
    print("🔧 Updating model names from deepseek-r1:1.5b to gemma3:1b")
    print("=" * 60)
    
    old_model = "deepseek-r1:1.5b"
    new_model = "gemma3:1b"
    
    files_to_update = [
        "EDI_project_enhanced.py",
        "install_ollama.sh", 
        "ENHANCED_CHATBOT_README.md"
    ]
    
    updated_count = 0
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            if update_file(file_path, old_model, new_model):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("\n" + "=" * 60)
    print(f"🎉 Update complete! Updated {updated_count} files.")
    print("\n📝 Changes made:")
    print(f"   - {old_model} → {new_model}")
    print("\n🚀 Next steps:")
    print("   1. Pull the new model: ollama pull gemma3:1b")
    print("   2. Test the model: ollama run gemma3:1b 'Hello!'")
    print("   3. Restart enhanced chatbot: python3 EDI_project_enhanced.py")
    print("   4. Test integration: python3 test_enhanced_chatbot.py")

if __name__ == "__main__":
    main()
