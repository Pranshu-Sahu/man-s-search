import os
import sys
import json
import time
import re
from typing import List, Literal, Optional
import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

# Load environment variables
load_dotenv()
sys.stdout.reconfigure(line_buffering=True)


NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    print("Error: NVIDIA_API_KEY is not set in environment or .env file.")
    sys.exit(1)

# API Configuration
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# Primary model and fallbacks for Nemotron
DEFAULT_MODELS = [
    "mistralai/mistral-nemotron",
    "nvidia/llama-3.3-nemotron-super-49b-v1",
    "nvidia/nemotron-3-super-120b-a12b",
    "nvidia/nemotron-mini-4b-instruct"
]
MODEL_NAME = os.getenv("NEMOTRON_MODEL", DEFAULT_MODELS[0])





# File paths
PDF_FILENAME_OPTIONS = ["mans_search_for_meaning.pdf", "Man's Search for Meaning.pdf"]
PROGRESS_FILE = "progress.json"
MASTER_FILE = "vocabulary_master.json"

# Pydantic Schema for Extraction Item
class VocabularyItem(BaseModel):
    page_number: int = Field(..., description="1-indexed page number where the term was extracted from")
    base_form: str = Field(..., description="Standard dictionary lemma")
    text_form: str = Field(..., description="Exact verbatim text form appearing in the document")
    category: Literal["vocabulary", "phrasal_verb", "idiom", "domain_concept"] = Field(
        ..., description="Type of extracted item"
    )
    cefr_level: Literal["C1", "C2", "Specialized"] = Field(
        ..., description="Language proficiency or domain level"
    )
    general_definition: str = Field(..., description="General dictionary definition")
    contextual_definition: str = Field(..., description="Definition in the context of the book text")
    sample_sentence: str = Field(..., description="Exact verbatim sentence from text containing the term")

SYSTEM_INSTRUCTION = """You are a Senior Lexicographer and AI Linguistics Analyst.
Analyze the attached 5-page PDF excerpt from Viktor Frankl's 'Man's Search for Meaning'.

EXTRACTION RULES:
1. VERBATIM GROUNDING: Every extracted term and 'sample_sentence' MUST appear verbatim in the text.
2. JSON QUOTE SAFETY: Replace all inner double quotes inside string fields with single quotes (') to ensure valid JSON syntax.
3. BASE FORM MAPPING: Map inflected words to standard dictionary lemmas (e.g., text_form: 'brought home to' -> base_form: 'bring home to'; text_form: 'scruples' -> base_form: 'scruple').
4. DIFFICULTY FILTER: Only extract C1–C2 vocabulary, phrasal verbs, idioms, and domain concepts (psychology, logotherapy, camp history). Exclude basic A1–B2 words.
5. NO MULTI-WORD SPLITTING: Do not split phrasal verbs or idioms into single individual words (extract 'bear up under' as a single entry).

OUTPUT FORMAT:
Respond with ONLY a raw JSON array of objects. Do not include markdown code block formatting or introductory text.
Each object in the array MUST strictly follow this JSON schema:
[
  {
    "page_number": <INTEGER>,
    "base_form": "<STRING>",
    "text_form": "<STRING>",
    "category": "<vocabulary | phrasal_verb | idiom | domain_concept>",
    "cefr_level": "<C1 | C2 | Specialized>",
    "general_definition": "<STRING>",
    "contextual_definition": "<STRING>",
    "sample_sentence": "<STRING>"
  }
]"""

def get_pdf_path() -> str:
    """Find and return valid PDF file path."""
    for fn in PDF_FILENAME_OPTIONS:
        if os.path.exists(fn):
            return fn
    raise FileNotFoundError(f"Could not find PDF file. Looked for: {PDF_FILENAME_OPTIONS}")

def load_progress() -> int:
    """Load last completed page number from progress.json."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("last_completed_page", 0)
        except Exception as e:
            print(f"Warning: Could not read {PROGRESS_FILE} ({e}). Starting from page 0.")
    return 0

def save_progress(last_completed_page: int, total_pages: int, total_terms: int) -> None:
    """Save progress atomically to progress.json."""
    data = {
        "last_completed_page": last_completed_page,
        "total_pages": total_pages,
        "total_terms_extracted": total_terms,
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    temp_file = f"{PROGRESS_FILE}.tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(temp_file, PROGRESS_FILE)

def load_master_vocabulary() -> List[dict]:
    """Load existing extracted terms from vocabulary_master.json."""
    if os.path.exists(MASTER_FILE):
        try:
            with open(MASTER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not read {MASTER_FILE} ({e}). Starting with empty list.")
    return []

def save_master_vocabulary(master_list: List[dict]) -> None:
    """Save vocabulary master list atomically to vocabulary_master.json."""
    temp_file = f"{MASTER_FILE}.tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(master_list, f, indent=2, ensure_ascii=False)
    os.replace(temp_file, MASTER_FILE)

def extract_pdf_chunk_text(pdf_doc: fitz.Document, start_page: int, end_page: int) -> str:
    """
    Slices pages (1-indexed start_page to end_page) from PDF document
    and returns formatted text content per page.
    """
    chunk_text_parts = []
    # fitz is 0-indexed
    for page_idx in range(start_page - 1, end_page):
        page_num = page_idx + 1
        page = pdf_doc[page_idx]
        text = page.get_text("text").strip()
        chunk_text_parts.append(f"--- START PAGE {page_num} ---\n{text}\n--- END PAGE {page_num} ---")
    return "\n\n".join(chunk_text_parts)

def clean_json_response(raw_text: str) -> str:
    """Strip markdown backticks or preambles to parse pure JSON string."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    # Extract JSON array using regex if surrounded by additional prose
    match = re.search(r'\[\s*\{.*\}\s*\]', cleaned, re.DOTALL)
    if match:
        return match.group(0)
    return cleaned

def call_nemotron_api(chunk_text: str, start_page: int, end_page: int, max_retries: int = 5) -> List[dict]:
    """
    Call Nemotron API with exponential backoff for handling rate limits (HTTP 429),
    automatic model fallback, and response validation.
    """
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    user_prompt = f"""Here is the 5-page text excerpt covering Pages {start_page} to {end_page}:

{chunk_text}

Extract all matching C1-C2 vocabulary, phrasal verbs, idioms, and domain concepts adhering strictly to all extraction rules. Output raw JSON array only."""

    for model_name in DEFAULT_MODELS:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 4096
        }

        retry_delay = 5  # Initial backoff delay in seconds

        for attempt in range(1, max_retries + 1):
            try:
                print(f"  [API Call] Pages {start_page}-{end_page} using '{model_name}' (Attempt {attempt}/{max_retries})...")
                response = requests.post(API_URL, headers=headers, json=payload, timeout=90)

                if response.status_code == 429:
                    print(f"  [HTTP 429 Rate Limit] Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue

                if response.status_code in (404, 401):
                    print(f"  [HTTP {response.status_code}] Model '{model_name}' unavailable. Trying next model...")
                    break  # Break inner retry loop to try next model in DEFAULT_MODELS

                if response.status_code != 200:
                    print(f"  [HTTP {response.status_code} Error]: {response.text[:200]}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue

                res_json = response.json()
                choices = res_json.get("choices", [])
                if not choices:
                    raise ValueError("API returned response with empty choices list.")

                content = choices[0].get("message", {}).get("content", "")
                cleaned_json_str = clean_json_response(content)

                if not cleaned_json_str:
                    return []

                raw_items = json.loads(cleaned_json_str)
                if not isinstance(raw_items, list):
                    raise ValueError(f"Expected JSON array, got {type(raw_items)}")

                # Validate each item using Pydantic schema
                validated_items = []
                for item in raw_items:
                    try:
                        p_num = item.get("page_number")
                        if not isinstance(p_num, int) or p_num < start_page or p_num > end_page:
                            item["page_number"] = start_page

                        validated_obj = VocabularyItem.model_validate(item)
                        validated_items.append(validated_obj.model_dump())
                    except ValidationError as ve:
                        print(f"  [Validation Warning] Skipping item due to schema mismatch: {ve}")

                return validated_items

            except (requests.RequestException, json.JSONDecodeError, ValueError) as err:
                print(f"  [Attempt {attempt} Failed] Error: {err}")
                if attempt == max_retries:
                    print(f"  [Error] Reached max retries for model '{model_name}'. Trying next model...")
                else:
                    time.sleep(retry_delay)
                    retry_delay *= 2

    print(f"  [Error] All candidate models failed for Pages {start_page}-{end_page}.")
    return []


def main():
    pdf_path = get_pdf_path()
    print(f"=== Starting Nemotron Extraction Pipeline ===")
    print(f"PDF Source: {pdf_path}")

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"Total Pages in PDF: {total_pages}")

    last_completed_page = load_progress()
    print(f"Resuming from last completed page: {last_completed_page}")

    master_vocab = load_master_vocabulary()
    print(f"Currently loaded master vocabulary items: {len(master_vocab)}")

    while last_completed_page < total_pages:
        start_page = last_completed_page + 1
        end_page = min(start_page + 4, total_pages)

        print(f"\n--- Processing Batch: Pages {start_page} to {end_page} of {total_pages} ---")
        
        # 1. Extract 5-page text excerpt using PyMuPDF
        chunk_text = extract_pdf_chunk_text(doc, start_page, end_page)

        if not chunk_text.strip():
            print(f"  [Notice] Pages {start_page}-{end_page} produced empty text. Skipping API call.")
            batch_items = []
        else:
            # 2. Call Nemotron API with retry logic & Pydantic validation
            batch_items = call_nemotron_api(chunk_text, start_page, end_page)

        print(f"  Extracted {len(batch_items)} valid vocabulary entries from Pages {start_page}-{end_page}.")

        # 3. Append to master list & save continuously
        master_vocab.extend(batch_items)
        save_master_vocabulary(master_vocab)

        # 4. Update progress state
        last_completed_page = end_page
        save_progress(last_completed_page, total_pages, len(master_vocab))
        print(f"  Saved progress. Total vocabulary entries collected so far: {len(master_vocab)}.")

        if last_completed_page < total_pages:
            print("  Sleeping 4 seconds before next batch...")
            time.sleep(4)

    doc.close()
    print("\n==================================================")
    print(f"SUCCESS: Pipeline completed for all {total_pages} pages!")
    print(f"Total extracted terms saved in '{MASTER_FILE}': {len(master_vocab)}")
    print("==================================================")

if __name__ == "__main__":
    main()
