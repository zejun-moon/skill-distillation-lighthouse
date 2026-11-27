#!/usr/bin/env python3
"""check_repo.py —— 本仓自检（提交前本地跑，CI 也会跑）。

编排两个通用工具，**不重复实现规则**：

  1. `skills/<skill>/scripts/verify-structure.py` —— 结构 / 引用完整性 / 脚本规范 /
     版本一致 / 报告索引
  2. `skills/<skill>/scripts/scan-sensitive.py` —— 敏感信息扫描

两个工具都能**独立拷到其他仓库直接用**，本脚本只是把它们串起来。

用法：
    python3 tools/check_repo.py
退出码 = 问题数（0 = 干净）。
Python 3.6+，只用标准库。
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills")


def find_script(name):
    """在 skills/*/scripts/ 下找到指定工具。"""
    if not os.path.isdir(SKILLS_DIR):
        return None
    for skill in sorted(os.listdir(SKILLS_DIR)):
        p = os.path.join(SKILLS_DIR, skill, "scripts", name)
        if os.path.isfile(p):
            return p
    return None


def run(label, script, extra_args):
    if not script:
        print("[%s] ⚠️  找不到 %s，跳过" % (label, os.path.basename(script or "")))
        return 0
    print("=" * 60)
    print("▶ %s" % label)
    print("=" * 60)
    r = subprocess.run([sys.executable, script] + extra_args,
                       cwd=ROOT, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    print(out.rstrip())
    print()
    return r.returncode


def main():
    struct = run("结构校验", find_script("verify-structure.py"), ["--root", ROOT])
    redact = run("敏感信息扫描", find_script("scan-sensitive.py"),
                 ["--root", ROOT, "--quiet"])
    total = struct + redact

    print("=" * 60)
    if total:
        print("发现 %d 个问题（结构 %d + 脱敏 %d）" % (total, struct, redact))
        print("脱敏豁免：在该行加 `# scan: allow` 并写清理由。")
        return total
    print("✅ 全部检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
