import os
import re
import json
import sys

LINE_PARSE_RE = re.compile(r'^(?P<prefix>(?:\|   |    )*)(?P<edge>\|--|\+--)?\s*(?P<body>.+)$')
BODY_RE = re.compile(r'^(?P<name>[^\s(<>!=~]+)\s*(?P<spec>[<>=!~][^()]*)?\s*\((?P<installed>[^)]+)\)\s*$')

def parse_pip_dependencies(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {"dependencies": []}

    dependencies = []
    stack = []

    def depth_from_prefix(prefix, edge):
        groups = re.findall(r'(?:\|   |    )', prefix)
        return len(groups) + (1 if edge else 0)

    def create_dep(body):
        m = BODY_RE.match(body.strip())
        if m:
            return {
                "package_name": m.group("name").strip(),
                "installed_version": m.group("installed").strip(),
                "required_version": (m.group("spec") or "Any").strip(),
                "dependencies": []
            }
        return {
            "package_name": body.strip(),
            "installed_version": "",
            "required_version": "Any",
            "dependencies": []
        }

    for line in lines:
        line = line.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith(". "):
            continue

        m = LINE_PARSE_RE.match(line)
        if not m:
            continue

        prefix, edge, body = m.group("prefix"), m.group("edge"), m.group("body")
        dep = create_dep(body)
        depth = depth_from_prefix(prefix, edge)

        while stack and stack[-1]["depth"] >= depth:
            stack.pop()

        if stack:
            stack[-1]["node"]["dependencies"].append(dep)
        else:
            dependencies.append(dep)

        stack.append({"depth": depth, "node": dep})

    return {"dependencies": dependencies}


def convert_txt_to_json(txt_file="dets.txt", json_file="dets.json"):
    if not os.path.exists(txt_file):
        print(f"{txt_file} not found.")
        return
    data = parse_pip_dependencies(txt_file)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"{json_file} saved successfully.")
