"""
Test script for Feature 4: Evidence-Aware Answers with Chunk Citations

This script validates that:
1. Citation IDs are generated correctly
2. Citations are passed through the pipeline
3. API returns citations in response
4. Answer includes inline citation links
"""

import json
import re
from typing import Dict, Any

def test_citation_format(answer: str) -> bool:
    """Test that answer contains valid citation format [C1], [C2], etc."""
    citation_pattern = r'\[C\d+\]'
    citations = re.findall(citation_pattern, answer)
    
    if citations:
        print(f"✅ Found {len(citations)} citations in answer")
        print(f"   Citations: {set(citations)}")
        return True
    else:
        print("⚠️  No citations found in answer (expected [C1], [C2], etc.)")
        return False


def test_citations_dict_structure(citations: Dict[str, dict]) -> bool:
    """Test that citations dict has correct structure."""
    if not citations:
        print("⚠️  No citations dict in response")
        return False
    
    required_fields = {"page", "snippet", "source", "full_content"}
    
    for citation_id, metadata in citations.items():
        # Check citation ID format
        if not re.match(r'^C\d+$', citation_id):
            print(f"❌ Invalid citation ID format: {citation_id}")
            return False
        
        # Check required fields
        missing_fields = required_fields - set(metadata.keys())
        if missing_fields:
            print(f"❌ Citation {citation_id} missing fields: {missing_fields}")
            return False
        
        # Check field types
        if not isinstance(metadata["page"], (int, str)):
            print(f"❌ Citation {citation_id} 'page' should be int or str")
            return False
        
        if not isinstance(metadata["source"], str):
            print(f"❌ Citation {citation_id} 'source' should be str")
            return False
    
    print(f"✅ Citations dict has correct structure")
    print(f"   Citations: {list(citations.keys())}")
    return True


def test_citation_consistency(answer: str, citations: Dict[str, dict]) -> bool:
    """Test that all citations in answer exist in citations dict."""
    citation_pattern = r'\[C(\d+)\]'
    answer_citations = set(re.findall(citation_pattern, answer))
    dict_citations = set([int(cid[1:]) for cid in citations.keys()])
    
    missing_in_dict = answer_citations - dict_citations
    if missing_in_dict:
        print(f"❌ Citations in answer but not in dict: {missing_in_dict}")
        return False
    
    unused_in_answer = dict_citations - answer_citations
    if unused_in_answer:
        print(f"⚠️  Unused citations in dict: {unused_in_answer}")
    
    print(f"✅ All citations in answer have corresponding metadata")
    return True


def validate_api_response(response: Dict[str, Any]) -> bool:
    """Validate complete API response structure."""
    print("\n" + "="*60)
    print("VALIDATING FEATURE 4: EVIDENCE-AWARE ANSWERS")
    print("="*60 + "\n")
    
    # Check required fields
    required_fields = {"answer", "context", "citations"}
    missing_fields = required_fields - set(response.keys())
    if missing_fields:
        print(f"❌ Response missing fields: {missing_fields}")
        return False
    
    print("✅ Response has required fields (answer, context, citations)")
    
    answer = response.get("answer", "")
    citations = response.get("citations", {})
    context = response.get("context", "")
    
    # Test answer format
    print("\n📝 Testing Answer Citations...")
    test1 = test_citation_format(answer)
    
    # Test citations dict
    print("\n📚 Testing Citations Dict Structure...")
    test2 = test_citations_dict_structure(citations) if citations else True
    
    # Test consistency
    print("\n🔗 Testing Citation Consistency...")
    test3 = test_citation_consistency(answer, citations) if citations else True
    
    # Test context format
    print("\n📄 Testing Context Format...")
    if context and "[C" in context:
        print("✅ Context contains citation IDs [C1], [C2], etc.")
        test4 = True
    else:
        print("⚠️  Context does not contain citation IDs (context_with_citations may not be used)")
        test4 = False
    
    # Overall summary
    print("\n" + "="*60)
    all_passed = test1 and test2 and test3 and test4
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*60)
    
    return all_passed


def print_response_preview(response: Dict[str, Any]):
    """Pretty print a preview of the API response."""
    print("\n" + "="*60)
    print("API RESPONSE PREVIEW")
    print("="*60 + "\n")
    
    print("📝 ANSWER:")
    print("-" * 60)
    print(response.get("answer", "N/A")[:500])
    if len(response.get("answer", "")) > 500:
        print("...")
    
    print("\n📚 CITATIONS:")
    print("-" * 60)
    citations = response.get("citations", {})
    if citations:
        for cid, meta in list(citations.items())[:3]:
            print(f"\n{cid}: {meta['source']} (Page {meta['page']})")
            print(f"  Snippet: {meta['snippet'][:100]}...")
        if len(citations) > 3:
            print(f"\n  ... and {len(citations) - 3} more citations")
    else:
        print("No citations in response")


if __name__ == "__main__":
    # Example usage:
    # response = await test_qa_endpoint()
    # validate_api_response(response)
    
    print("\n" + "="*60)
    print("Feature 4 Test Script")
    print("="*60)
    print("\nUsage:")
    print("1. Run the API: uvicorn src.app.api:app --reload")
    print("2. Run tests: python test_feature_4.py")
    print("3. Or import: from test_feature_4 import validate_api_response")
    print("\nExample test response structure:")
    
    example_response = {
        "answer": "HNSW provides fast approximate search [C1][C2]. LSH uses hash functions [C4].",
        "context": "[C1] Chunk from page 5: HNSW...\n[C2] Chunk from page 6: ...",
        "citations": {
            "C1": {
                "page": 5,
                "snippet": "HNSW (Hierarchical Navigable Small World) provides...",
                "source": "vector_db_paper.pdf",
                "full_content": "..."
            },
            "C2": {
                "page": 6,
                "snippet": "The hierarchical structure allows...",
                "source": "vector_db_paper.pdf",
                "full_content": "..."
            },
            "C4": {
                "page": 7,
                "snippet": "Locality-Sensitive Hashing (LSH)...",
                "source": "vector_db_paper.pdf",
                "full_content": "..."
            }
        }
    }
    
    print_response_preview(example_response)
    validate_api_response(example_response)
