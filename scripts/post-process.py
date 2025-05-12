import re

def clean_and_markdown(text):
    # 1️⃣ 앞뒤 불필요한 부분 제거
    start_idx = text.find('1. 일반사항')
    end_idx = text.find('집필위원')
    core_text = text[start_idx:end_idx]

    # 2️⃣ 챕터 번호별로 Markdown 헤딩 부여
    lines = core_text.split('\n')
    result_lines = []
    for line in lines:
        line = line.strip()
        if re.match(r'^\d+\.\d+\.\d+', line):
            line = '### ' + line
        elif re.match(r'^\d+\.\d+', line):
            line = '## ' + line
        elif re.match(r'^\d+\.', line):
            line = '# ' + line
        elif line.startswith('부록'):
            line = '# ' + line
        result_lines.append(line)

    # 3️⃣ 결과 합치기
    return '\n'.join(result_lines)

# 텍스트 불러오기
with open('142024.md', 'r', encoding='utf-8') as f:
    raw_text = f.read()

# 변환 실행
md_text = clean_and_markdown(raw_text)

# Markdown 파일로 저장
with open('142024.md', 'w', encoding='utf-8') as f:
    f.write(md_text)
