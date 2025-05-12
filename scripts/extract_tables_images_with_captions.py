from pyhwpx import Hwp
import os
import json

hwp_path = "input.hwp"  # 처리할 HWP 파일 경로
output_dir = "output"
tables_dir = os.path.join(output_dir, "tables")
images_dir = os.path.join(output_dir, "images")
os.makedirs(tables_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

hwp = Hwp(visible=False)
hwp.open(hwp_path)

# 표 추출 + 캡션
tables_meta = []
table_idx = 0
while True:
    try:
        hwp.get_into_nth_table(table_idx)
        csv_path = os.path.join(tables_dir, f"table_{table_idx+1:03d}.csv")
        hwp.table_to_csv(filename=csv_path)
        # 캡션 추출 (표 바로 아래/위 문단 등에서 추출, pyhwpx는 get_into_table_caption 제공)
        caption = ""
        try:
            if hwp.get_into_table_caption():
                _, caption = hwp.get_text()
        except Exception:
            pass
        tables_meta.append({
            "table_idx": table_idx+1,
            "csv_path": csv_path,
            "caption": caption.strip()
        })
        print(f"표 {table_idx+1} → {csv_path} (캡션: {caption.strip()})")
        table_idx += 1
    except Exception:
        break

with open(os.path.join(tables_dir, "tables_meta.json"), "w", encoding="utf-8") as f:
    json.dump(tables_meta, f, ensure_ascii=False, indent=2)

# 이미지 추출 + 캡션
images_meta = []
hwp.save_all_pictures(save_path=images_dir)
ctrls = hwp.ctrl_list
img_idx = 1
for ctrl in ctrls:
    info = hwp.get_image_info(ctrl)
    caption = ""
    # 실제 캡션 추출은 문서 구조에 따라 커스텀 구현 필요
    images_meta.append({
        "img_idx": img_idx,
        "file": info.get("path", ""),
        "size": info.get("size", []),
        "caption": caption.strip()
    })
    print(f"이미지 {img_idx} → {info.get('path', '')} (캡션: {caption.strip()})")
    img_idx += 1

with open(os.path.join(images_dir, "images_meta.json"), "w", encoding="utf-8") as f:
    json.dump(images_meta, f, ensure_ascii=False, indent=2)

hwp.quit() 