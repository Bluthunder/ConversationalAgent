import json

def merge_jsonl_files(input_paths, output_path):
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for path in input_paths:
            with open(path, 'r', encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)
    print(f"✅ Merged {len(input_paths)} files into {output_path}")
