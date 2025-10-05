import json
import os

# --- CONFIGURATION ---
INPUT_FILENAME = "backend/vectorization_chunks_FINAL.jsonl"
# ---------------------

def get_all_chunks_as_list(input_file):
    """
    Reads the JSON Lines file and returns a single, flattened Python list
    containing all text chunks ('split_content') from every document.
    """
   
    if not os.path.exists(input_file):
        print(f"🚨 Error: Input file '{input_file}' not found. Cannot proceed.")
        return []

    all_chunks = []
    documents_processed = 0
    output_data = []

    # print(f"-> Reading and consolidating chunks from {input_file}...")

    try:
        # Use a for loop to read the file line by line (efficient for large files)
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue

                # Load each line as a JSON object
                doc_data = json.loads(line)
               
                # Extract the list of chunk strings and add them to the main list
                # The 'extend' method flattens the list of lists into one big list of strings.
                title = doc_data.get("title", f"{documents_processed+1}")
                chunks_list = doc_data.get('split_content', [])
                all_chunks.extend(chunks_list)
                for chunk in chunks_list:
                        output_data.append({
                            "title": title,
                            "chunk": chunk
                        })
                documents_processed += 1

        print(f"Total number of chunks stored in the list: {len(output_data)}.")

        with open("backend/dataChunks.json", "w") as file:
            json.dump(output_data, file, indent=4)

        # return all_chunks

    except Exception as e:
        print(f"\n🚨 Critical error during file processing: {e}")
        return []

# --- Example Usage ---
if __name__ == "__main__":
   
    # This variable now holds the single, large Python list of all your text chunks
    final_list_of_chunks = get_all_chunks_as_list(INPUT_FILENAME)
   
    # if final_list_of_chunks:
        # print("\n--- List successfully created in memory ---")
        # print(f"The resulting Python list contains {len(final_list_of_chunks)} strings.")
        # print("This list is now ready to be passed directly to your vectorization function.")