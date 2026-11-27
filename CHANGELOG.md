# CHANGELOG

本文件记录本仓库的所有重要变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 待办

- 扫描器增加「**语义性泄露**」的启发式检查（规模数字、内部弱点措辞）——目前只能人工复核
- `new-skill-scaffold.sh` 支持 `--from <已有仓>` 增量迁移
- 给 `scan-sensitive.py` 加 `--baseline` 模式：只报相对上次新增的命中（适合进 CI 卡增量）

## [0.1.0] - 2026-11-27

首个版本：从一次真实的「把内网实战经验做成公开技能仓」的产出中提炼。

### 新增

- **技能主流程** `skills/skill-distillation-lighthouse/SKILL.md`
  —— 七步流程（划边界 → 收素材 → 写脱敏报告 → 四选一提炼 → 写主流程 → 机器门禁 → 发布）
  + 知识库 vs 技能仓的判断口径 + 排障入口 + 边界声明
- **脱敏规范** `references/desensitization.md`
  —— 威胁模型（9 类）、逐类替换表（16 种形态）、七条硬规则、豁免机制、
    机器门禁的三条工程纪律、提交前清单、**语义性泄露**的处理、泄露后的处置顺序
- **写作规范** `references/skill-authoring.md`
  —— frontmatter 与 description 触发词写法、正文四段结构、每步要有可执行通过条件、
    <500 行拆分原则、内容四要素（结论/判据/可复现动作/失败样本）、诚实标注、边界声明
- **仓库规范** `references/repo-layout.md`
  —— 标准骨架（每项写明理由）、版本号四处一致、发版流程、CI 该跑什么、
    自检四类检查、发布与回读校验、嵌套 git 仓注意事项、一仓一技能 vs 一仓多技能
- **流程坑表** `references/pitfalls.md` —— 9 条实测坑（做技能仓这件事本身）
- **评审清单** `references/review-checklist.md` —— 提交前 / 合并前 / 发版前三张清单
- **三个通用工具**（均可拷到其他仓库直接用）
  - `scripts/scan-sensitive.py` —— 脱敏扫描器：可配置规则、行内豁免、JSON 报告、
    校验 IPv4 八位组
  - `scripts/verify-structure.py` —— 结构校验器：frontmatter / 引用完整性 / 脚本规范 /
    版本一致 / 报告索引
  - `scripts/new-skill-scaffold.sh` —— 一键生成合规骨架
- **本仓自检** `tools/check_repo.py`（编排上面两个工具，不重复实现规则）
- **扫描器测试** `tests/test_check_repo.py` —— 阳性 + 阴性样本（样本运行时拼接，
  避免自指误报与 gitleaks 误判）
- **实战沉淀** `field-reports/2026-11-27-first-public-skill-repo.md`
- **工程化** `.claude-plugin/`（Claude Code 插件清单）· `.github/workflows/ci.yml`
  （结构 + 脱敏 + 单测 + shell 语法 + gitleaks）· `AGENTS.md` / `CLAUDE.md` /
  `CONTRIBUTING.md` / `SECURITY.md` / `ROADMAP.md` / 双语 README
