#!/usr/bin/env python3
"""
Test script to parse the actual PDF file and see how many colleges are detected.
"""

from pdf_parser import EnhancedCollegeParser
import os

def test_real_pdf():
    """Test the parser with the actual PDF file."""
    
    pdf_path = "cutoff.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return None
    
    print(f"🚀 Testing parser with real PDF: {pdf_path}")
    print(f"📁 File size: {os.path.getsize(pdf_path) / (1024*1024):.2f} MB")
    
    # Initialize parser
    parser = EnhancedCollegeParser()
    
    # Parse the PDF
    print("\n🔄 Parsing PDF...")
    result = parser.parse_pdf(pdf_path)
    
    if result.get("parsing_success"):
        print("✅ Parsing successful!")
        print(f"📊 Results:")
        print(f"  - Total Colleges: {result['total_colleges']}")
        print(f"  - Total Branches: {result['total_branches']}")
        print(f"  - Total Cutoff Entries: {result['total_cutoffs']}")
        
        print(f"\n📚 Colleges found:")
        for i, college in enumerate(result['colleges'][:5], 1):  # Show first 5 colleges
            print(f"  {i}. {college['college_name']} ({college['college_code']})")
            print(f"     Branches: {college['total_branches']}")
            if college['branches']:
                sample_branch = college['branches'][0]
                print(f"     Sample branch: {sample_branch['branch_name']} ({len(sample_branch['cutoff_data'])} cutoffs)")
            print()
        
        if len(result['colleges']) > 5:
            print(f"  ... and {len(result['colleges']) - 5} more colleges")
        
        # Save to JSON for inspection
        output_file = "real_pdf_parsed.json"
        parser.save_to_json(result, output_file)
        print(f"💾 Full results saved to {output_file}")
        
        return result
    else:
        print("❌ Parsing failed!")
        print(f"Error: {result.get('error')}")
        return None

if __name__ == "__main__":
    test_real_pdf()
