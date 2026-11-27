# AGENTS.md — 给维护本仓库的 AI Agent

本仓库主要由 AI agent 阅读、执行、改进和沉淀经验。人类维护者负责审核与决策。
**开始任何工作前请先读完本文件（约 4 分钟）。**

## 使命

让任何 AI 助手在**不踩坑**的前提下，把真实运维经验沉淀成**可公开、可复现、可被自动调用**的技能仓，
并且**不会泄露内网信息**。所有改动都服务于这三点：

1. **准确**：规范来自实测与事故，不来自想象
2. **可执行**：规范要能变成脚本，而不是停留在"要小心"
3. **安全**：脱敏是**机器门禁**，不是口头承诺

## 仓库地图

| 路径 | 作用 | 什么时候改 |
|---|---|---|
| `skills/skill-distillation-lighthouse/SKILL.md` | 技能主流程（被 AI 加载） | 流程/原则变化（保持 < 500 行，细节放 references） |
| `skills/.../references/desensitization.md` | **脱敏规范（核心）** | 威胁模型或规则变化 |
| `skills/.../references/skill-authoring.md` | 写作规范：frontmatter / 拆分 / 标注 / 边界 | 规范变化 |
| `skills/.../references/repo-layout.md` | 目录结构 / 版本一致 / 发版 / CI | 结构变化 |
| `skills/.../references/pitfalls.md` | 做技能仓本身的坑 | 每遇到一个新问题 |
| `skills/.../references/review-checklist.md` | 三张评审清单 | 评审流程变化 |
| `skills/.../scripts/scan-sensitive.py` | **通用脱敏扫描器**（可拷到任何仓用） | 新规则 / 新豁免机制 |
| `skills/.../scripts/verify-structure.py` | **结构校验器**（可拷到任何仓用） | 新校验项 |
| `skills/.../scripts/new-skill-scaffold.sh` | 骨架生成器 | 模板变化 |
| `field-reports/` | 每次真实执行的脱敏报告 | **每次真实执行后必写** |
| `tools/check_repo.py` | 本仓自检（编排上面两个工具） | 新检查项 |
| `tests/test_check_repo.py` | 扫描器阳性/阴性样本 | **扫描规则变化时必须同时改** |
| `.claude-plugin/` | Claude Code 插件与 marketplace 清单 | 发版时改版本号 |
| `CHANGELOG.md` | 变更记录 | 每个 PR |

## 铁律

1. **绝不提交敏感信息**：真实 IP、域名、账号、口令、密钥、内部 uid、私有仓库地址。
   示例统一用 `10.0.0.x`、`example.com`。
   提交前必须 `python3 tools/check_repo.py` 通过（CI 还有 gitleaks）。
2. **规范文档本身也不能包含真实标识**：要脱敏的具体账号名只能出现在
   `scan-sensitive.py` 的规则定义里（自带 `# scan: allow` 豁免标记）——
   否则规范文档本身就成了泄露源。
3. **诚实标注验证状态**：只在真实跑通过的才写"已验证"；区分 `实测` / `推断` / `未测`。
4. **改扫描规则必须同时改测试**，并补**阳性**样本（必须命中）；放宽规则要补**阴性**样本。
5. **每次改规则跑阳性对照**：拿**未脱敏**的真实素材喂扫描器，
   命中数为 0 → 扫描器是摆设，**必须修**。
6. **不写没用的东西**：每个段落都要能帮人**做出判断**。
7. **会改变外部状态的事由人决定**：发布到公网、删远端仓库、轮换凭据 → 先向用户确认。
8. **`SKILL.md` 只放主流程**：正文 < 500 行，细节一律进 `references/`。

## 沉淀经验的工作流（最重要）

每次真实执行（无论成败）：

1. 按 `field-reports/TEMPLATE.md` 写 `field-reports/YYYY-MM-DD-<主题>.md`（脱敏），
   并更新 `field-reports/README.md` 的索引表
2. 对报告里每个新问题做**四选一**判断：
   - 以后还会遇到 → 写进 `references/pitfalls.md`（现象 → 原因 → 处理）
   - 能自动检测 → 在 `scripts/` 里加判定，并补 `tests/`
   - 能自动修复 → 改脚本 + 补测试
   - 只是这次的特例 → 只留在报告里
3. 在报告里标注 `状态：promoted → pitfalls.md #N`
4. 更新 `CHANGELOG.md` 的 `[Unreleased]` 段

## 本地自检

```bash
python3 tools/check_repo.py                       # 结构 + 脱敏（编排两个通用工具）
python3 -m unittest discover -s tests             # 扫描器阳性/阴性样本
find . -name '*.sh' -not -path './.git/*' -print0 | xargs -0 -r -n1 bash -n
# 骨架生成器烟测
bash skills/skill-distillation-lighthouse/scripts/new-skill-scaffold.sh \
     --target /tmp/scaffold-test --name demo-skill \
     --description "demo" >/dev/null && \
  (cd /tmp/scaffold-test && python3 tools/check_repo.py)
```

## 提交与发版

- 分支 + PR；Conventional Commits（`feat:`、`fix:`、`docs:`、`pitfall:`、`report:`、`ci:`）；squash 合并
- PR 描述说清楚：改了什么、为什么改、**验证状态**（实测 / 推断 / 未测）
- 发版（semver）：同步修改 `.claude-plugin/plugin.json` 的 `version`、
  `marketplace.json` 的 `metadata.version` 与 `plugins[0].version`、以及 `CHANGELOG.md`
- `check_repo.py` 会校验这几处一致
- 分支：仓库只长期保留 `main`；main 有保护，必须通过 CI

## 常见任务 → 去哪里

| 任务 | 入口 |
|---|---|
| 要做某个主题的技能仓 | 先读 `SKILL.md`，再跑 `new-skill-scaffold.sh` |
| 不知道什么算敏感 | `references/desensitization.md` §1 威胁模型 + §2 替换表 |
| 扫自己的仓 | `scripts/scan-sensitive.py --root <仓>` |
| 规则误报了 | 改 `scan-sensitive.py` + **同时**改 `tests/` + 跑阳性对照 |
| 规则漏报了 | 同上，**先加阳性样本**再改规则 |
| 写 SKILL.md 的 description | `references/skill-authoring.md` §1 |
| 评审别人的 PR | `references/review-checklist.md` |
