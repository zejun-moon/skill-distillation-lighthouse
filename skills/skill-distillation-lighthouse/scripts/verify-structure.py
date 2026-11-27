#!/usr/bin/env python3
"""verify-structure.py —— 技能仓结构校验（可拷到任何仓库直接用）

检查五类问题：
  1. 技能结构：每个 skills/<name>/ 必须有 SKILL.md；frontmatter 存在、
     name == 目录名、description 存在且 <= 1024 字符且中英双触发词、
     正文 < 500 行
  2. 引用完整性：SKILL.md 里提到的每个 scripts/ references/ assets/ 路径真实存在
  3. 脚本规范：所有 .sh/.bash 有 shebang 且带可执行位
  4. 版本一致：.claude-plugin/plugin.json == marketplace.json（metadata + plugins[0]）
     == CHANGELOG.md 最新版本号
  5. 报告索引：field-reports/ 每份报告 frontmatter 键齐全，且都被 README 索引

用法：
    python3 verify-structure.py [--root .] [--json report.json]
退出码 = 问题数（0 = 干净）。
Python 3.6+，只用标准库。
"""
import argparse
import json
import os
import re
import sys

problems = []
warnings = []


def bad(msg):
    problems.append(msg)
    print("  x " + msg)


def warn(msg):
    warnings.append(msg)
    print("  ! " + msg)


def ok(msg):
    print("  o " + msg)


def rel(path, root):
    return os.path.relpath(path, root).replace("\\", "/")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def check_skills(root):
    print("[1] 技能结构")
    skills_dir = os.path.join(root, "skills")
    if not os.path.isdir(skills_dir):
        bad("skills/ 目录不存在")
        return
    names = []
    for name in sorted(os.listdir(skills_dir)):
        sd = os.path.join(skills_dir, name)
        if not os.path.isdir(sd):
            continue
        names.append(name)
        sk = rel(os.path.join(sd, "SKILL.md"), root)
        if not os.path.exists(os.path.join(root, sk)):
            bad("%s 缺失" % sk)
            continue
        text = read(os.path.join(root, sk))
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        if not m:
            bad("%s: 缺少 YAML frontmatter" % sk)
            continue
        fm, body = m.group(1), m.group(2)

        fname = re.search(r"^name:\s*(.+)$", fm, re.M)
        desc = re.search(r"^description:\s*(.+)$", fm, re.M)
        if not fname or fname.group(1).strip() != name:
            bad("%s: frontmatter name 必须等于目录名 '%s'" % (sk, name))
        else:
            ok("%s: name == 目录名" % sk)

        if not desc or not desc.group(1).strip():
            bad("%s: frontmatter 缺 description" % sk)
        else:
            d = desc.group(1).strip()
            if len(d) > 1024:
                bad("%s: description 过长 (%d > 1024 字符)" % (sk, len(d)))
            else:
                ok("%s: description %d 字符 (<=1024)" % (sk, len(d)))
            has_cn = bool(re.search(r"[\u4e00-\u9fff]", d))
            has_en = bool(re.search(r"[A-Za-z]{3,}", d))
            if not (has_cn and has_en):
                bad("%s: description 建议同时含中英触发词（当前 cn=%s en=%s）"
                    % (sk, has_cn, has_en))
            else:
                ok("%s: description 含中英触发词" % sk)

        body_lines = len(body.split("\n"))
        if body_lines > 500:
            bad("%s: 正文 %d 行，超过 500 行（细节请拆到 references/）" % (sk, body_lines))
        else:
            ok("%s: 正文 %d 行 (<500)" % (sk, body_lines))

    print("[2] 引用完整性")
    total_refs = 0
    for name in names:
        sk_rel = "skills/%s/SKILL.md" % name
        sk_abs = os.path.join(root, sk_rel)
        if not os.path.exists(sk_abs):
            continue
        body = read(sk_abs)
        refs = set()
        for pm in re.finditer(r"`((?:scripts|references|assets)/[A-Za-z0-9_.\-/]+)`", body):
            refs.add(pm.group(1))
        for pm in re.finditer(
                r"\]\((?:\./)?((?:skills/[^)]*?/)?(?:scripts|references|assets)/[^)]+)\)",
                body):
            refs.add(pm.group(1))
        missing = []
        for r in sorted(refs):
            total_refs += 1
            cands = [os.path.join(root, r),
                     os.path.join(root, "skills", name, r)]
            if not any(os.path.exists(c) for c in cands):
                missing.append(r)
        for r in missing:
            bad("%s: 引用了不存在的路径 %s" % (sk_rel, r))
        if refs and not missing:
            ok("%s: 引用的 %d 个路径全部存在" % (sk_rel, len(refs)))
    if total_refs == 0:
        bad("没有任何技能声明过 scripts/references 路径 —— 检查是否写全了")

    print("[3] 脚本规范")
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "__pycache__", "node_modules"}]
        for f in sorted(filenames):
            if not f.endswith((".sh", ".bash")):
                continue
            sp = os.path.join(dirpath, f)
            srel = rel(sp, root)
            with open(sp, encoding="utf-8", errors="replace") as fh:
                first = fh.readline()
            if not first.startswith("#!"):
                bad("%s: 缺少 shebang" % srel)
            elif not os.access(sp, os.X_OK):
                bad("%s: 缺少可执行位（chmod +x）" % srel)
            else:
                ok("%s: shebang + 可执行位正常" % srel)


def check_versions(root):
    print("[4] 版本一致")
    versions = {}
    plugin_json = os.path.join(root, ".claude-plugin", "plugin.json")
    market_json = os.path.join(root, ".claude-plugin", "marketplace.json")
    changelog = os.path.join(root, "CHANGELOG.md")

    if os.path.exists(plugin_json):
        try:
            versions["plugin.json"] = json.load(
                open(plugin_json, encoding="utf-8")).get("version")
        except Exception as e:
            bad("plugin.json 解析失败: %s" % e)
    else:
        bad(".claude-plugin/plugin.json 缺失")

    if os.path.exists(market_json):
        try:
            mk = json.load(open(market_json, encoding="utf-8"))
            versions["marketplace.json:metadata"] = (mk.get("metadata") or {}).get("version")
            plugs = mk.get("plugins") or []
            versions["marketplace.json:plugins[0]"] = plugs[0].get("version") if plugs else None
        except Exception as e:
            bad("marketplace.json 解析失败: %s" % e)
    else:
        bad(".claude-plugin/marketplace.json 缺失")

    if os.path.exists(changelog):
        m = re.search(r"^##\s*\[?v?(\d+\.\d+\.\d+)\]?", read(changelog), re.M)
        if m:
            versions["CHANGELOG.md"] = m.group(1)
        else:
            bad("CHANGELOG.md 里找不到版本号标题")
    else:
        bad("CHANGELOG.md 缺失")

    vals = [v for v in versions.values() if v]
    if vals and len(set(vals)) == 1:
        ok("版本一致: %s" % vals[0])
    elif vals:
        bad("版本不一致: %s" % ", ".join(
            "%s=%s" % (k, v) for k, v in sorted(versions.items())))


def check_field_reports(root):
    print("[5] 报告索引")
    fr_dir = os.path.join(root, "field-reports")
    if not os.path.isdir(fr_dir):
        print("  - field-reports/ 不存在（无实战报告的技能仓可忽略）")
        return
    reports = sorted(f for f in os.listdir(fr_dir)
                     if f.endswith(".md") and f not in ("README.md", "TEMPLATE.md"))
    if not reports:
        # 新仓还没做过实战 → 合法状态，只是提醒（--strict 下升级为错误）
        warn("field-reports/ 下还没有报告 —— 第一次真实执行后必须补一份")
        return
    index_path = os.path.join(fr_dir, "README.md")
    index_text = read(index_path) if os.path.exists(index_path) else ""
    for r in reports:
        text = read(os.path.join(fr_dir, r))
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            bad("field-reports/%s: 缺少 frontmatter" % r)
            continue
        fm = m.group(1)
        missing = [k for k in ("date", "environment", "result")
                   if not re.search(r"^%s:\s*\S" % k, fm, re.M)]
        if missing:
            bad("field-reports/%s: frontmatter 缺 %s" % (r, ", ".join(missing)))
        if r not in index_text:
            bad("field-reports/%s 没有被 field-reports/README.md 索引" % r)
        else:
            ok("field-reports/%s: frontmatter 齐全且已索引" % r)


def main():
    ap = argparse.ArgumentParser(description="技能仓结构校验")
    ap.add_argument("--root", default=".", help="仓库根目录（默认当前目录）")
    ap.add_argument("--json", default="", help="把结果写成 JSON 到该路径")
    ap.add_argument("--strict", action="store_true",
                    help="把警告也算作错误（例：CI 里要求必须有实战报告）")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    check_skills(root)
    check_versions(root)
    check_field_reports(root)

    print()
    print("=" * 50)
    if args.strict and warnings:
        problems.extend(warnings)
    if problems:
        print("发现 %d 个问题：" % len(problems))
        for p in problems:
            print("  - %s" % p)
    else:
        print("结构检查通过")
    if warnings:
        print("（%d 条警告，见上方 ! 行）" % len(warnings))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"root": root, "problems": problems,
                       "warnings": warnings,
                       "problem_count": len(problems)},
                      f, ensure_ascii=False, indent=2)

    return len(problems)


if __name__ == "__main__":
    sys.exit(main())
