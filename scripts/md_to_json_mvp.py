import os
import json
import re

INPUT_MD = "markdown-db/142001.md"
OUTPUT_DIR = "output"
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "142001.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_markdown(md_path):
    doc_id = os.path.splitext(os.path.basename(md_path))[0]
    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()

    results = []
    para_idx = 1
    buffer = []
    header_re = re.compile(r"^(#+) (.*)")

    def flush_paragraph():
        nonlocal para_idx, buffer
        if buffer:
            text = " ".join([l.strip() for l in buffer if l.strip()])
            if text:
                results.append({
                    "doc_id": doc_id,
                    "para_id": f"{doc_id}_{para_idx}",
                    "type": "paragraph",
                    "text": text
                })
                para_idx += 1
            buffer = []

    for line in lines:
        m = header_re.match(line)
        if m:
            flush_paragraph()
            level = len(m.group(1))
            text = m.group(2).strip()
            results.append({
                "doc_id": doc_id,
                "para_id": f"{doc_id}_{para_idx}",
                "type": "header",
                "level": level,
                "text": text
            })
            para_idx += 1
        elif line.strip() == "":
            flush_paragraph()
        else:
            buffer.append(line)
    flush_paragraph()
    return results

def main():
    json_data = parse_markdown(INPUT_MD)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(json_data)} items to {OUTPUT_JSON}")

if __name__ == "__main__":
    main() 