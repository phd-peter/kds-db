import os
import json
import re

INPUT_MD = "markdown-db/142001.md"
OUTPUT_DIR = "output"
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "142001_glossary.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_glossary_terms(md_path):
    doc_id = os.path.splitext(os.path.basename(md_path))[0]
    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()

    glossary = []
    para_idx = 1
    term_re = re.compile(r"^∙([^:：]+)[:：](.*)")

    for line in lines:
        line = line.strip()
        if line.startswith("∙"):
            m = term_re.match(line)
            if m:
                term = m.group(1).strip()
                text = m.group(2).strip()
                glossary.append({
                    "doc_id": doc_id,
                    "para_id": f"{doc_id}_g{para_idx}",
                    "type": "definition",
                    "term": term,
                    "text": text
                })
                para_idx += 1
    return glossary

def main():
    glossary = extract_glossary_terms(INPUT_MD)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(glossary)} glossary terms to {OUTPUT_JSON}")

if __name__ == "__main__":
    main() 