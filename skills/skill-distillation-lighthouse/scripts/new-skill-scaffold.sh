#!/usr/bin/env bash
# new-skill-scaffold.sh —— 一键生成技能仓骨架
#
# 把「沉淀规范」变成可执行的：一条命令产出合规的最小骨架，
# 之后你只需要往里填内容。
#
# 用法：
#   bash new-skill-scaffold.sh --target ./my-skill-repo --name my-skill \
#        --description "把 X 做成 Y 的实战流程，凡是用户提到 Z 都要用本技能" \
#        [--template generic|metrics|ops]
#
# 产出后必做：
#   1. 填 skills/<name>/SKILL.md 的正文与 references/
#   2. 按 references/desensitization.md 脱敏
#   3. python3 tools/check_repo.py    # 必须退出码 0
set -uo pipefail

TARGET=""
NAME=""
DESCRIPTION=""
TEMPLATE="generic"

usage() {
  cat <<'EOF'
用法: new-skill-scaffold.sh --target <dir> --name <skill-name> --description <desc> [选项]
  --target       目标目录（不存在则创建）
  --name         技能名（将成为 skills/<name>/ 的目录名，frontmatter name 必须一致）
  --description  技能描述（frontmatter description，建议含中英触发词）
  --template     附加模板：generic（默认）| metrics | ops
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --target)      TARGET="${2:-}"; shift 2 ;;
    --name)        NAME="${2:-}"; shift 2 ;;
    --description) DESCRIPTION="${2:-}"; shift 2 ;;
    --template)    TEMPLATE="${2:-}"; shift 2 ;;
    -h|--help)     usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage; exit 2 ;;
  esac
done

if [ -z "$TARGET" ] || [ -z "$NAME" ] || [ -z "$DESCRIPTION" ]; then
  echo "错误: --target / --name / --description 必填" >&2
  usage
  exit 2
fi

case "$NAME" in
  *[!a-z0-9-]*) echo "错误: --name 只能用小写字母、数字和连字符" >&2; exit 2 ;;
esac

SKILL_DIR="$TARGET/skills/$NAME"
mkdir -p "$SKILL_DIR"/{references,scripts} \
         "$TARGET"/{field-reports,tools,tests} \
         "$TARGET"/.claude-plugin \
         "$TARGET"/.github/workflows

# ── SKILL.md ────────────────────────────────────────────────────────────────
cat > "$SKILL_DIR/SKILL.md" <<'EOF'
---
name: __NAME__
license: MIT
description: __DESCRIPTION__
---

# __TITLE__

<一段话：这个技能解决什么问题，来自哪次真实实战，覆盖哪些范围>

## 什么时候不要用本技能

- <场景 A：此时应该用别的方案>
- <场景 B：此时不值得做成技能>

## 第 0 步 · <先确认前提>

<先确认什么；用什么命令确认；确认结果长什么样>

## 第 1 步 · <主流程第一步>

<做什么；做完怎么验>

## 排障入口

| 现象 | 先看 | 大概率原因 |
|---|---|---|
| | | |

## 边界：这些动作一律先问用户

- <会改变业务行为 / 不可逆的动作>

## 配套文件

| 文件 | 内容 |
|---|---|
| `references/pitfalls.md` | 坑表：现象 → 原因 → 处理 |
| `scripts/` | 可执行判定 |

## 来源与可信度

<来源；用 ✅ 标注「实测确认」、📄 标注「推断」；明确不覆盖的范围>
EOF

# ── references ──────────────────────────────────────────────────────────────
cat > "$SKILL_DIR/references/pitfalls.md" <<'EOF'
# 坑表：现象 → 原因 → 处理

> 来自真实执行。✅ = 实测复现 · 📄 = 据源码/文档推断

## 1. ✅ <一句话现象>

- **现象**：<用户能认出来的样子>
- **原因**：<为什么>
- **处理**：<可直接执行的动作>

---

## 新坑怎么进来

1. 按 `field-reports/TEMPLATE.md` 写一份脱敏报告
2. 判断：会再遇到 → 写进本文；能自动检测 → 加进 `scripts/`；只是特例 → 只留报告
3. 在报告里标 `状态：promoted → pitfalls.md #N`
4. 更新 `CHANGELOG.md` 的 `[Unreleased]`
EOF

# ── field-reports ───────────────────────────────────────────────────────────
cat > "$TARGET/field-reports/TEMPLATE.md" <<'EOF'
---
date: YYYY-MM-DD
environment: <环境与版本>
result: success | partial | failed
duration_hours: <数字>
skill_version: <版本>
operator: agent | human
---

# <一句话标题：做了什么、结果如何>

> 脱敏报告。真实 IP → `10.0.0.x`；内网域名 → `example.com`；
> 真实命名空间 / uid / 私有仓库地址 / 人名 → 一律替换。

## 1. 开工前的状态

| 项 | 状态 |
|---|---|

## 2. 遇到的问题（按发生顺序）

### 问题 1：<现象>

- **现象**：
- **第一反应**（当时怀疑什么）：
- **实际原因**：
- **处理**：
- **怎么确认的**（做了哪个对照实验 / 看了哪条日志）：

## 3. 结果

| 项 | 结果 |
|---|---|

## 4. 没做的事（以及为什么）

## 5. 状态提升

| 问题 | 去向 |
|---|---|
| | `pitfalls.md` #N |
EOF

cat > "$TARGET/field-reports/README.md" <<'EOF'
# 实战报告索引

> 每次**真实执行**（不论成败）都写一份**脱敏**报告。
> 报告是原始素材，`references/pitfalls.md` 是提炼后的结论 —— 两边都要有。

| 日期 | 报告 | 结果 | 覆盖 |
|---|---|---|---|
| | | | |

## 写报告的规矩

1. 用 `TEMPLATE.md` 的 frontmatter 字段
2. **脱敏**：真实 IP → `10.0.0.x`；内网域名 → `example.com`；真实 ns / uid / 人名 → 替换
3. **失败样本比成功样本值钱** —— 记清楚「当时为什么判断错了」
4. 报告里标 `状态：promoted → pitfalls.md #N`
5. 新增报告后**必须同步更新这个索引表**（自检会验）
EOF

# ── 治理文件 ────────────────────────────────────────────────────────────────
cat > "$TARGET/AGENTS.md" <<'EOF'
# AGENTS.md — 给维护本仓库的 AI Agent

本仓库主要由 AI agent 阅读、执行、改进和沉淀经验。人类维护者负责审核与决策。
**开始任何工作前请先读完本文件。**

## 使命

<一句话：这个仓库要帮谁解决什么问题>

## 仓库地图

| 路径 | 作用 | 什么时候改 |
|---|---|---|
| `skills/<name>/SKILL.md` | 技能主流程（保持 < 500 行，细节放 references） | 流程/原则变化 |
| `skills/.../references/pitfalls.md` | 坑：现象 → 原因 → 处理 | 每遇到一个新问题 |
| `skills/.../scripts/` | 可执行判定 | 判定规则变化 |
| `field-reports/` | 每次真实执行的脱敏报告 | **每次真实执行后必写** |
| `tools/check_repo.py` | 仓库自检 | 新规则 |
| `tests/` | 扫描器测试 | 扫描规则变化 |
| `.claude-plugin/` | 插件与 marketplace 清单 | 发版时改版本号 |

## 铁律

1. **绝不提交敏感信息**：真实 IP、域名、账号、口令、密钥、内部 uid。
   示例统一用 `10.0.0.x`、`example.com`。提交前必须 `python3 tools/check_repo.py` 通过。
2. **诚实标注验证状态**：只在真实跑通过的才写「已验证」。
3. **SKILL.md 只放主流程**：正文 < 500 行，细节一律进 `references/`。
4. **能自动判的别让人肉比对**：写成脚本。
5. **改行为的事由人决定**：向用户确认，不自动执行。

## 沉淀经验的工作流

1. 写脱敏报告 → 2. 四选一判断（坑表 / 脚本 / 只留报告）→ 3. 标 `promoted` → 4. 更新 CHANGELOG

## 本地自检

```bash
python3 tools/check_repo.py
python3 -m unittest discover -s tests
```

## 提交与发版

- 分支 + PR；Conventional Commits；squash 合并
- 发版要同步四处版本号：plugin.json / marketplace.json×2 / CHANGELOG
EOF

cat > "$TARGET/CHANGELOG.md" <<'EOF'
# CHANGELOG

## [Unreleased]

### 待办

- 

## [0.1.0] - __DATE__

首个版本。

### 新增

- 技能主流程 `skills/__NAME__/SKILL.md`
- 坑表 `skills/__NAME__/references/pitfalls.md`
- 实战报告 `field-reports/`
- 仓库自检 `tools/check_repo.py` + `tests/`
EOF

cat > "$TARGET/CONTRIBUTING.md" <<'EOF'
# 贡献指南

## 硬性要求

1. **先写实战报告，再写结论。**
2. **脱敏。** 提交前 `python3 tools/check_repo.py` 必须退出码 0。
3. **标注验证状态。** 实测 / 推断 / 未测，不要把推测写成结论。
4. **每个断言都要能被复现。**

## 提交信息

Conventional Commits：`feat:` `fix:` `docs:` `pitfall:` `report:` `ci:`

## 加一个新坑

1. 写 `field-reports/YYYY-MM-DD-<topic>.md`（脱敏）
2. 在 `references/pitfalls.md` 加「现象 → 原因 → 处理」
3. 报告里标 `状态：promoted → pitfalls.md #N`
4. **能自动检测的** → 在 `scripts/` 加判定，并补 `tests/`
5. 更新 `field-reports/README.md` 索引 + `CHANGELOG.md`
6. 跑 `python3 tools/check_repo.py` 与 `python3 -m unittest discover -s tests`
EOF

cat > "$TARGET/SECURITY.md" <<'EOF'
# 安全策略

本仓库是**公开仓**，内容会被公开索引。因此真实 IP、域名、账号、口令、
私钥、内部 uid、私有仓库地址**一律不允许出现**。示例统一用
`10.0.0.x` 与 `example.com`。

## 怎么防

1. `tools/check_repo.py` —— 提交前本地扫
2. CI 的 gitleaks —— 兜底扫历史提交

> 第一道防线只扫**当前工作区**。已经推到远端的内容，改文件不等于删除历史
> —— 泄露了要**轮换凭据**。

## 报告安全问题

**不要开公开 issue**，请私下联系维护者。
EOF

cat > "$TARGET/README.md" <<'EOF'
# __TITLE__

<一句话说清这个仓库解决什么问题>

## 快速开始

```bash
git clone https://github.com/__OWNER__/__REPO__.git
```

## 目录结构

```text
skills/__NAME__/
  SKILL.md
  references/
  scripts/
field-reports/
tools/
tests/
```

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。核心要求：
**先写脱敏报告，再把结论提炼进 `references/pitfalls.md`**，
提交前 `python3 tools/check_repo.py` 必须退出码 0。

## 许可

[MIT](LICENSE)
EOF

cat > "$TARGET/.gitignore" <<'EOF'
__pycache__/
*.py[cod]
.DS_Store
*.swp
*.log
dashboard*.json
*.import.json
*.key
*.pem
.env
.env.*
!.env.example
EOF

cat > "$TARGET/.gitattributes" <<'EOF'
* text=auto eol=lf
*.sh text eol=lf
*.py text eol=lf
*.md text eol=lf
*.yml text eol=lf
*.json text eol=lf
*.png binary
*.jpg binary
*.pdf binary
EOF

cat > "$TARGET/LICENSE" <<'EOF'
MIT License

Copyright (c) 2026 __OWNER__

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# ── 插件清单 ────────────────────────────────────────────────────────────────
cat > "$TARGET/.claude-plugin/plugin.json" <<'EOF'
{
  "name": "__NAME__",
  "version": "0.1.0",
  "description": "__DESCRIPTION__",
  "author": {
    "name": "__OWNER__"
  },
  "license": "MIT",
  "keywords": []
}
EOF

cat > "$TARGET/.claude-plugin/marketplace.json" <<'EOF'
{
  "name": "__REPO__",
  "owner": {
    "name": "__OWNER__"
  },
  "metadata": {
    "description": "__DESCRIPTION__",
    "version": "0.1.0"
  },
  "plugins": [
    {
      "name": "__NAME__",
      "source": "./",
      "version": "0.1.0",
      "description": "__DESCRIPTION__",
      "author": {
        "name": "__OWNER__"
      },
      "license": "MIT",
      "keywords": []
    }
  ]
}
EOF

cat > "$TARGET/.github/workflows/ci.yml" <<'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  self-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: 结构与脱敏自检
        run: python3 tools/check_repo.py
      - name: 单元测试
        run: python3 -m unittest discover -s tests -v
      - name: shell 语法检查
        run: |
          find . -name '*.sh' -not -path './.git/*' -print0 | xargs -0 -r -n1 bash -n

  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
EOF

# ── 占位符替换 ──────────────────────────────────────────────────────────────
REPO="$(basename "$TARGET")"
OWNER="${OWNER:-$(git config --global user.name 2>/dev/null || echo skill-author)}"
TITLE="$NAME"

for f in "$SKILL_DIR/SKILL.md" "$TARGET/CHANGELOG.md" "$TARGET/README.md" \
         "$TARGET/AGENTS.md" "$TARGET/CONTRIBUTING.md" "$TARGET/SECURITY.md" \
         "$TARGET/LICENSE" "$TARGET/.claude-plugin/plugin.json" \
         "$TARGET/.claude-plugin/marketplace.json"; do
  [ -f "$f" ] || continue
  sed -i "s/__NAME__/$NAME/g; s/__DESCRIPTION__/$DESCRIPTION/g; s/__TITLE__/$TITLE/g; \
          s/__OWNER__/$OWNER/g; s/__REPO__/$REPO/g; s/__DATE__/$(date +%Y-%m-%d)/g" "$f"
done

# ── 自检工具（从本仓复制一份，改成本仓的规则）──────────────────────────────
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
if [ -f "$REPO_ROOT/tools/check_repo.py" ]; then
  cp "$REPO_ROOT/tools/check_repo.py" "$TARGET/tools/check_repo.py"
  cp "$REPO_ROOT/tests/test_check_repo.py" "$TARGET/tests/test_check_repo.py" 2>/dev/null || true
  chmod +x "$TARGET/tools/check_repo.py"
fi
if [ -f "$HERE/scan-sensitive.py" ]; then
  cp "$HERE/scan-sensitive.py" "$TARGET/skills/$NAME/scripts/scan-sensitive.py"
  chmod +x "$TARGET/skills/$NAME/scripts/scan-sensitive.py"
fi
if [ -f "$HERE/verify-structure.py" ]; then
  cp "$HERE/verify-structure.py" "$TARGET/skills/$NAME/scripts/verify-structure.py"
  chmod +x "$TARGET/skills/$NAME/scripts/verify-structure.py"
fi

echo "✅ 已生成技能仓骨架: $TARGET"
echo
echo "目录："
find "$TARGET" -type f | sed "s|$TARGET|.|" | sort | sed 's/^/  /'
echo
echo "下一步："
echo "  1. 填 $SKILL_DIR/SKILL.md 正文（主流程 + 判断标准 + 排障入口 + 边界）"
echo "  2. 往 $SKILL_DIR/references/ 写细节（正文超 500 行就往这拆）"
echo "  3. 往 $TARGET/field-reports/ 写脱敏实战报告"
echo "  4. 按 references/desensitization.md 脱敏"
echo "  5. cd $TARGET && python3 tools/check_repo.py   # 必须退出码 0"
echo "  6. git init && git add -A && git commit -m 'feat: 首个版本'"
