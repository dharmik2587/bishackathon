#!/usr/bin/env python3
"""
BIS Standards RAG Engine - Inference Script
Entry point for automated evaluation
Reads input JSON queries, retrieves standards, outputs results
"""

import json
import argparse
import sys
import time
import re
from pathlib import Path
from typing import List, Dict, Tuple


class BISRAGEngine:
    """RAG engine for BIS standards retrieval using keyword + TF-IDF-like scoring"""
    
    def __init__(self, standards_file: str):
        self.standards = self._load_standards(standards_file)
        self.standard_map = {std['id']: std for std in self.standards}
        self._build_indexes()
    
    def _load_standards(self, standards_file: str) -> List[Dict]:
        """Load standards from JSON file"""
        with open(standards_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_indexes(self):
        """Build inverted index for fast lookup"""
        self.inverted_index = {}  # word -> list of (std_index, field_weight)
        
        for idx, std in enumerate(self.standards):
            # Index title words (highest weight)
            title_words = self._tokenize(std.get('title', ''))
            for word in title_words:
                if word not in self.inverted_index:
                    self.inverted_index[word] = []
                self.inverted_index[word].append((idx, 5.0))
            
            # Index standard number
            code_words = self._tokenize(std.get('standardNumber', ''))
            for word in code_words:
                if word not in self.inverted_index:
                    self.inverted_index[word] = []
                self.inverted_index[word].append((idx, 4.0))
            
            # Index keywords (high weight)
            for keyword in std.get('keywords', []):
                kw = keyword.lower().strip()
                if kw not in self.inverted_index:
                    self.inverted_index[kw] = []
                self.inverted_index[kw].append((idx, 3.0))
            
            # Index category
            cat_words = self._tokenize(std.get('category', ''))
            for word in cat_words:
                if word not in self.inverted_index:
                    self.inverted_index[word] = []
                self.inverted_index[word].append((idx, 1.5))
            
            # Index section
            sec_words = self._tokenize(std.get('section', ''))
            for word in sec_words:
                if word not in self.inverted_index:
                    self.inverted_index[word] = []
                self.inverted_index[word].append((idx, 1.0))
            
            # Index description (low weight)
            desc_words = self._tokenize(std.get('description', ''))
            for word in desc_words:
                if word not in self.inverted_index:
                    self.inverted_index[word] = []
                self.inverted_index[word].append((idx, 0.5))
            
            # Index contextChunks
            for chunk in std.get('contextChunks', []):
                chunk_words = self._tokenize(chunk)
                for word in chunk_words:
                    if word not in self.inverted_index:
                        self.inverted_index[word] = []
                    self.inverted_index[word].append((idx, 0.8))
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into meaningful words with basic stemming"""
        if not text:
            return []
        text_lower = text.lower()
        # Split on non-alphanumeric chars
        words = re.findall(r'[a-z]{3,}', text_lower)
        # Filter stopwords
        stopwords = {
            'the', 'and', 'for', 'with', 'from', 'this', 'that', 'are', 'was',
            'has', 'have', 'been', 'will', 'which', 'their', 'used', 'shall',
            'not', 'but', 'its', 'also', 'into', 'can', 'may', 'all', 'any',
            'our', 'use', 'per', 'than', 'both', 'each', 'how', 'what', 'when',
            'where', 'who', 'why', 'other', 'about', 'more', 'most', 'some',
            'such', 'only', 'same', 'very', 'just', 'over', 'under', 'between',
            'through', 'during', 'before', 'after', 'above', 'below', 'being',
        }
        result = []
        for w in words:
            if w in stopwords:
                continue
            # Basic stemming - strip common suffixes
            stemmed = self._stem(w)
            result.append(stemmed)
        return result
    
    def _stem(self, word: str) -> str:
        """Very basic stemming for construction domain"""
        # Keep short words as-is
        if len(word) <= 4:
            return word
        # Handle common plural/verb endings
        if word.endswith('ies') and len(word) > 5:
            return word[:-3] + 'y'
        if word.endswith('es') and len(word) > 4 and word[-3] not in 'aeiou':
            return word[:-2]
        if word.endswith('s') and not word.endswith('ss') and len(word) > 4:
            return word[:-1]
        if word.endswith('ing') and len(word) > 5:
            return word[:-3]
        if word.endswith('ed') and len(word) > 4:
            return word[:-2]
        return word
    
    def _expand_query(self, query_words: List[str]) -> List[str]:
        """Expand query with synonyms and related terms"""
        synonyms = {
            'supersulphat': ['sulphat', 'super', 'sulphate'],
            'sulphat': ['supersulphat', 'sulphate'],
            'marine': ['sea', 'aggressive'],
            'decorat': ['architectural', 'white', 'ornamental'],
            'architectural': ['decorat', 'white'],
            'lightweight': ['light', 'weight'],
            'precast': ['cast'],
            'reinforc': ['rebar'],
            'corrugat': ['sheet'],
            'cladding': ['roofing', 'sheet', 'cover'],
            'hollow': ['solid', 'block'],
            'mortar': ['masonry', 'cement', 'plaster'],
            'aggregat': ['sand', 'gravel', 'coarse', 'fine'],
            'pozzolana': ['pozzolan', 'fly', 'ash', 'calcin', 'clay'],
            'calcin': ['clay', 'pozzolana'],
            'slag': ['portland', 'granulat', 'blast'],
        }
        
        expanded = list(query_words)
        for word in query_words:
            if word in synonyms:
                expanded.extend(synonyms[word])
        
        return expanded
    
    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """
        Retrieve top K standard codes for a query
        Returns list of standard numbers like ["IS 269: 1989", "IS 383: 1970", ...]
        """
        query_words = self._tokenize(query)
        expanded_words = self._expand_query(query_words)
        
        # Score accumulation per standard index
        scores = {}
        
        # Phase 1: Inverted index lookup with expanded query
        for word in expanded_words:
            if word in self.inverted_index:
                for std_idx, weight in self.inverted_index[word]:
                    if std_idx not in scores:
                        scores[std_idx] = 0.0
                    scores[std_idx] += weight
        
        # Phase 2: Direct matching with scoring boosts
        query_lower = query.lower()
        query_words_set = set(query_words)
        
        for idx, std in enumerate(self.standards):
            title_lower = std.get('title', '').lower()
            title_words = set(self._tokenize(title_lower))
            
            # Strong boost for multi-word overlap between query and title
            overlap = title_words & query_words_set
            if len(overlap) >= 2:
                if idx not in scores:
                    scores[idx] = 0.0
                scores[idx] += len(overlap) * 3.0
            
            # Substring matching for compound words (e.g., "supersulphated" contains "sulphated")
            for qword in query_words:
                if len(qword) > 4:
                    for tword in title_words:
                        if len(tword) > 4 and (qword in tword or tword in qword) and qword != tword:
                            if idx not in scores:
                                scores[idx] = 0.0
                            scores[idx] += 3.0
            
            # Exact substring match in full title
            for word in query_words:
                if len(word) > 4 and word in title_lower:
                    if idx not in scores:
                        scores[idx] = 0.0
                    scores[idx] += 2.0
            
            # Penalize when title has very different focus
            # E.g., if query is about "cement" but title is about "blocks/units" 
            # give less bonus than a direct "cement" title
            if 'cement' in query_words_set and 'cement' in title_words:
                if idx not in scores:
                    scores[idx] = 0.0
                scores[idx] += 4.0  # Extra boost for cement-cement match
        
        # Sort by score descending
        sorted_standards = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top K standard numbers
        results = []
        for std_idx, score in sorted_standards[:top_k]:
            if score > 0:
                results.append(self.standards[std_idx]['standardNumber'])
        
        return results


def process_batch(input_file: str, output_file: str, standards_file: str) -> bool:
    """
    Process batch of queries and write results
    Returns True on success, False on failure
    """
    
    try:
        # Load input queries
        with open(input_file, 'r', encoding='utf-8') as f:
            queries = json.load(f)
        
        if not isinstance(queries, list):
            print("Error: Input JSON must be an array of queries")
            return False
        
        print(f"Loaded {len(queries)} queries from {input_file}")
        
        # Initialize RAG engine
        print(f"Initializing RAG engine with {standards_file}...")
        rag_engine = BISRAGEngine(standards_file)
        print(f"Loaded {len(rag_engine.standards)} standards")
        
        # Process each query
        results = []
        total_latency = 0.0
        
        for idx, query_obj in enumerate(queries, 1):
            # Validate query structure
            if not isinstance(query_obj, dict) or 'id' not in query_obj or 'query' not in query_obj:
                print(f"  Skipping invalid query at index {idx}")
                continue
            
            # Measure latency
            start_time = time.time()
            
            # Retrieve standards
            retrieved_standards = rag_engine.retrieve(
                query_obj['query'],
                top_k=5
            )
            
            latency = time.time() - start_time
            total_latency += latency
            
            # Create result object - include expected_standards for eval
            result = {
                "id": query_obj['id'],
                "query": query_obj['query'],
                "retrieved_standards": retrieved_standards,
                "latency_seconds": round(latency, 3)
            }
            
            # Pass through expected_standards if present (needed by eval_script.py)
            if 'expected_standards' in query_obj:
                result["expected_standards"] = query_obj["expected_standards"]
            
            results.append(result)
            
            # Progress indicator
            status = "OK" if len(retrieved_standards) > 0 else "WARN"
            print(f"  [{idx:3d}] {status} {query_obj['id']}: "
                  f"{len(retrieved_standards)} standards ({latency:.3f}s)"
                  f" -> {retrieved_standards[:3]}")
        
        if not results:
            print("Error: No valid queries to process")
            return False
        
        # Write results to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        # Calculate and print statistics
        avg_latency = total_latency / len(results)
        max_latency = max(r['latency_seconds'] for r in results)
        min_latency = min(r['latency_seconds'] for r in results)
        successful = sum(1 for r in results if len(r['retrieved_standards']) > 0)
        
        print(f"\n{'='*50}")
        print(f"Results written to {output_file}")
        print(f"{'='*50}")
        print(f"Statistics:")
        print(f"  Queries processed: {len(results)}")
        print(f"  Successful retrievals: {successful}/{len(results)}")
        print(f"  Average latency: {avg_latency:.3f}s")
        print(f"  Min latency: {min_latency:.3f}s")
        print(f"  Max latency: {max_latency:.3f}s")
        print(f"  Total time: {total_latency:.2f}s")
        print(f"{'='*50}\n")
        
        return True
        
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='BIS Standards RAG Engine - Inference',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python inference.py --input public_test_set.json --output results.json --standards data/standards.json
  python inference.py --input queries.json --output output.json
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input JSON file with queries (array of {id, query})'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Path to output JSON file for results'
    )
    
    parser.add_argument(
        '--standards',
        type=str,
        default='data/standards.json',
        help='Path to standards JSON file (default: data/standards.json)'
    )
    
    args = parser.parse_args()
    
    # Validate files exist
    if not Path(args.input).exists():
        print(f"Input file not found: {args.input}")
        sys.exit(1)
    
    if not Path(args.standards).exists():
        print(f"Standards file not found: {args.standards}")
        print(f"  Run: python src/pdf_extractor.py --input dataset.pdf --output data/standards.json")
        sys.exit(1)
    
    # Process batch
    success = process_batch(args.input, args.output, args.standards)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
