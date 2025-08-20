#!/usr/bin/env python3
"""
Test script for the PDF parser functionality.
This script tests the parser with sample text data to ensure it works correctly.
"""

import json
from pdf_parser import EnhancedCollegeParser
from database import CollegeDatabase

def test_parser_with_sample_data():
    """Test the parser with sample text data that mimics the PDF structure."""
    
    # Sample text that mimics the PDF structure from the image
    sample_text = """
01002 - Government College of Engineering, Amravati

0100219110 - Civil Engineering
Status: Government Autonomous
State Level
Stage I
GOPENS: 33717 (88.6037289)
GSCS: 61041 (78.5613347)
GNT3S: 67451 (76.1358545)
GSEBCS: 83123 (69.7604398)
LSCS: 50493 (82.7086811)
LVJS: 52977 (81.7098306)
EWS: 115797 (53.7424491)

Stage I-Non PWD
PWDOPENS: 33345 (88.6997043)
ORPHAN: 33876 (88.5551879)

0100224210 - Computer Science and Engineering
Status: Government Autonomous
State Level
Stage I
GSCS: 11323 (96.2437396)
GSEBCS: 17059 (94.3331807)
LOPENS: 7985 (97.3461799)
LSEBCS: 21791 (92.7108008)
TFWS: 9964 (96.7229568)
PWDROBCS: 96341 (63.2687832)
EWS: 15308 (94.8964961)

0100224610 - Information Technology
Status: Government Autonomous
State Level
Stage I
GOBCS: 8917 (97.0497898)
GSEBCS: 24057 (91.9492948)
LOPENS: 11969 (96.0392321)
LSEBCS: 24708 (91.7849899)
TFWS: 13259 (95.6320635)
EWS: 19241 (93.6359026)

Stage VII
ORPHAN: 11764 (96.1353059)

0100229310 - Electrical Engineering
Status: Government Autonomous
State Level
Stage I
GOPENS: 24135 (91.9393058)
GNT2S: 50339 (82.7086811)
LNT1S: 44865 (84.5731157)
TFWS: 12755 (95.7978793)
EWS: 75966 (72.7750912)
"""
    
    # Create a mock PDF parser that works with text
    class MockPDFParser(EnhancedCollegeParser):
        def extract_text_from_pdf(self, pdf_path):
            # Return our sample text instead of reading from PDF
            return sample_text
    
    # Test the parser
    parser = MockPDFParser()
    
    # Parse the sample data
    result = parser.parse_pdf("mock_path.pdf")
    
    if result.get("parsing_success"):
        print("✅ Parsing successful!")
        print(f"College: {result['college_name']}")
        print(f"College Code: {result['college_code']}")
        print(f"Total Branches: {result['total_branches']}")
        
        print("\n📚 Branches found:")
        for branch in result['branches']:
            print(f"  - {branch['branch_name']} ({branch['branch_code']})")
            print(f"    Status: {branch['status']}")
            print(f"    Cutoff data entries: {len(branch['cutoff_data'])}")
            
            # Show some sample cutoff data
            if branch['cutoff_data']:
                print("    Sample cutoff data:")
                for cutoff in branch['cutoff_data'][:3]:  # Show first 3 entries
                    print(f"      Stage {cutoff['stage']} - {cutoff['category']}: {cutoff['rank']} ({cutoff['percentage']}%)")
            print()
        
        # Save to JSON for inspection
        parser.save_to_json(result, "test_output.json")
        print("💾 Test output saved to test_output.json")
        
        return result
    else:
        print("❌ Parsing failed!")
        print(f"Error: {result.get('error')}")
        return None

def test_database_functionality():
    """Test the database functionality."""
    print("\n🧪 Testing database functionality...")
    
    try:
        # Initialize database
        db = CollegeDatabase("test_college_cutoffs.db")
        
        # Get initial stats
        initial_stats = db.get_database_stats()
        print(f"Initial database stats: {initial_stats}")
        
        # Test with sample data
        sample_data = {
            "college_code": "01002",
            "college_name": "Government College of Engineering, Amravati",
            "branches": [
                {
                    "branch_code": "0100219110",
                    "branch_name": "Civil Engineering",
                    "status": "Government Autonomous",
                    "cutoff_data": [
                        {
                            "stage": "I",
                            "category": "GOPENS",
                            "rank": 33717,
                            "percentage": 88.6037289
                        }
                    ]
                }
            ],
            "total_branches": 1,
            "parsing_success": True
        }
        
        # Store the sample data
        success = db.store_parsed_data(sample_data)
        if success:
            print("✅ Sample data stored successfully!")
            
            # Get updated stats
            updated_stats = db.get_database_stats()
            print(f"Updated database stats: {updated_stats}")
            
            # Retrieve the stored data
            college_data = db.get_college_data(college_code="01002")
            if college_data:
                print("✅ Data retrieved successfully!")
                print(f"Retrieved college: {college_data['college_name']}")
                print(f"Branches: {len(college_data['branches'])}")
            else:
                print("❌ Failed to retrieve data")
        else:
            print("❌ Failed to store sample data")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    finally:
        # Clean up test database
        try:
            import os
            if os.path.exists("test_college_cutoffs.db"):
                os.remove("test_college_cutoffs.db")
                print("🧹 Test database cleaned up")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting PDF Parser Tests...\n")
    
    # Test 1: Parser functionality
    print("=" * 50)
    print("TEST 1: PDF Parser Functionality")
    print("=" * 50)
    parsed_data = test_parser_with_sample_data()
    
    # Test 2: Database functionality
    print("\n" + "=" * 50)
    print("TEST 2: Database Functionality")
    print("=" * 50)
    test_database_functionality()
    
    print("\n🎉 All tests completed!")
    
    if parsed_data:
        print("\n📊 Summary:")
        print(f"  - College: {parsed_data['college_name']}")
        print(f"  - Branches: {parsed_data['total_branches']}")
        print(f"  - Total cutoff entries: {sum(len(b['cutoff_data']) for b in parsed_data['branches'])}")
