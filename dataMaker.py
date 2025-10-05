import json
import re
import os
import sys
import time
import random
import requests
import csv
from io import StringIO
from urllib.parse import urljoin, urlparse

from langchain_text_splitters import RecursiveCharacterTextSplitter 

# --- CONFIGURATION (Ensure Input File Exists) ---
INPUT_FILENAME = "scraped_publications_FULL_DATA.json"  
OUTPUT_FILENAME = "vectorization_chunks_FINAL.jsonl" 

# Setting this high ensures all documents are processed (change if needed)
RUN_LIMIT = 1000 
# -----------------------------------------------

# --- SEMANTIC CHUNKING UTILITY ---
def create_semantic_chunks(full_text):
    """
    1. Filters out boilerplate text appearing before the Abstract.
    2. Splits the remaining document text using a hierarchical and overlapping strategy.
    """
    
    # 1. PRE-PROCESSING FILTER: Find the start of the content at "Abstract"
    # Find the first occurrence of "Abstract" (case-insensitive) followed by any whitespace.
    abstract_match = re.search(r'\bAbstract\b\s*', full_text, re.IGNORECASE)
    
    if abstract_match:
        # Start the text from the beginning of the match (where 'Abstract' starts)
        text_to_chunk = full_text[abstract_match.start():]
    else:
        # If 'Abstract' is not found, chunk the whole text (low confidence result)
        text_to_chunk = full_text.strip()
    
    # Check if we have any text left to process
    if not text_to_chunk:
        return []

    # 2. CHUNKING LOGIC
    # Define the splitter with the hierarchical separators and optimal sizes
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " "], # Split by paragraph, line, sentence, word
        chunk_size=950,                      # Max chunk size
        chunk_overlap=120,                   # Overlap size (context buffer)
        length_function=len,                 
        is_separator_regex=False, 
    )
    
    # Create the chunks
    chunks = text_splitter.create_documents([text_to_chunk])
    
    # Extract just the text content for vectorization
    chunk_texts = [chunk.page_content for chunk in chunks]
    
    return chunk_texts

# --- MAIN PROCESSING FUNCTION ---
def process_scraped_data():
    """Reads the scraped JSON, processes each document, and writes the new JSONL file."""
    
    if not os.path.exists(INPUT_FILENAME):
        print(f"Error: Input file '{INPUT_FILENAME}' not found. Please run the scraper first.")
        return

    try:
        sys.stdout.reconfigure(encoding='utf-8') 
        with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
            
    except json.JSONDecodeError:
        print(f"\nError: Could not decode JSON from '{INPUT_FILENAME}'. Check file format.")
        return
    except Exception as e:
        print(f"\nAn unexpected error occurred while reading the input file: {e}")
        return
    
    processed_documents = []
    data_to_process = scraped_data[:RUN_LIMIT]
    total_docs = len(data_to_process)
    
    print(f"-> Starting Hybrid Semantic Chunking for {total_docs} documents.")
    print("-" * 70)

    for i, doc in enumerate(data_to_process):
        doc_id = i + 1
        
        full_content = doc.get('full_content', '')
        
        if not full_content or doc.get('status') != 'Success':
            sys.stdout.write(f"  Doc {doc_id}/{total_docs}: SKIPPED (Content missing or scrape failed).\r")
            sys.stdout.flush()
            continue
            
        # Apply the semantic split logic (includes pre-abstract cleanup)
        split_chunks = create_semantic_chunks(full_content)
        chunk_count = len(split_chunks)
        
        # Confirmation check and printing
        status_color = "SUCCESS" if chunk_count > 0 else "ERROR"
        
        sys.stdout.write(
            f"  Doc {doc_id}/{total_docs}: Chunks={chunk_count:<3} -> {status_color:<10} \r")
        sys.stdout.flush()
        
        # Create the new structured object
        new_doc_structure = {
            "id": doc_id,
            "title": doc.get('title'),
            "url": doc.get('url'),
            "entire_content": full_content, # Keep full content for reference
            "split_content": split_chunks  # The list of chunks ready for embedding
        }
        
        processed_documents.append(new_doc_structure)

    # Write the output to a new JSON Lines file
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            for doc in processed_documents:
                json_line = json.dumps(doc, ensure_ascii=False)
                f.write(json_line + '\n')

        print("\n" + "-" * 70)
        print(f"Success! Processed {len(processed_documents)} documents.")
        print(f"Output saved to {OUTPUT_FILENAME} (JSON Lines format).")
        
    except Exception as e:
        print(f"\nError writing output file: {e}")

if __name__ == "__main__":
    process_scraped_data()