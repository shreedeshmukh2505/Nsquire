#!/usr/bin/env python3
"""
Comprehensive test script to parse the entire PDF and see the full results.
"""

from pdf_parser import EnhancedCollegeParser
import os
import time

def test_full_pdf():
    """Test the parser with the entire PDF file."""
    
    pdf_path = "cutoff.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return None
    
    print(f"🚀 Testing Enhanced Parser with Full PDF: {pdf_path}")
    print(f"📁 File size: {os.path.getsize(pdf_path) / (1024*1024):.2f} MB")
    
    # Initialize parser
    parser = EnhancedCollegeParser()
    
    # Parse the entire PDF
    print("\n🔄 Parsing entire PDF (this may take a while for 1400+ pages)...")
    start_time = time.time()
    
    result = parser.parse_pdf(pdf_path)
    
    end_time = time.time()
    parsing_time = end_time - start_time
    
    if result.get("parsing_success"):
        print("✅ Parsing completed successfully!")
        print(f"⏱️  Parsing time: {parsing_time:.2f} seconds")
        print(f"\n📊 Final Results:")
        print(f"  - Total Colleges: {result['total_colleges']}")
        print(f"  - Total Branches: {result['total_branches']}")
        print(f"  - Total Cutoff Entries: {result['total_cutoffs']}")
        
        # Calculate some statistics
        avg_branches_per_college = result['total_branches'] / result['total_colleges'] if result['total_colleges'] > 0 else 0
        avg_cutoffs_per_branch = result['total_cutoffs'] / result['total_branches'] if result['total_branches'] > 0 else 0
        
        print(f"\n📈 Statistics:")
        print(f"  - Average branches per college: {avg_branches_per_college:.1f}")
        print(f"  - Average cutoffs per branch: {avg_cutoffs_per_branch:.1f}")
        
        # Show first few colleges with their data
        print(f"\n📚 Sample Colleges (first 5):")
        for i, college in enumerate(result['colleges'][:5], 1):
            print(f"  {i}. {college['college_name']} ({college['college_code']})")
            print(f"     Branches: {college['total_branches']}")
            
            # Show sample branches
            for branch in college['branches'][:3]:  # Show first 3 branches
                print(f"       - {branch['branch_name']}: {len(branch['cutoff_data'])} cutoff entries")
                if branch['cutoff_data']:
                    # Show first few cutoffs
                    for cutoff in branch['cutoff_data'][:2]:
                        print(f"         Stage {cutoff['stage']} - {cutoff['category']}: {cutoff['rank']} ({cutoff['percentage']}%)")
            print()
        
        if len(result['colleges']) > 5:
            print(f"  ... and {len(result['colleges']) - 5} more colleges")
        
        # Save to JSON for inspection
        output_file = "full_pdf_parsed.json"
        parser.save_to_json(result, output_file)
        print(f"💾 Full results saved to {output_file}")
        
        return result
    else:
        print("❌ Parsing failed!")
        print(f"Error: {result.get('error')}")
        return None

if __name__ == "__main__":
    test_full_pdf()
