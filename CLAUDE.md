# CLAUDE.md

本仓库是 **Claude Code 插件**形态的技能包。

- 技能入口：`skills/skill-distillation-lighthouse/SKILL.md`
- 插件清单：`.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`
- 维护规则见根目录 [`AGENTS.md`](AGENTS.md)（**开始工作前先读它**）

## 本地开发

```bash
# 结构 + 版本 + 报告索引 + 脱敏（提交前必跑）
python3 tools/check_repo.py

# 单元测试（扫描器阳性/阴性样本）
python3 -m unittest discover -s tests

# 插件清单校验
claude plugin validate .
```

## 三个工具可单独拿去用

```bash
# 脱敏扫描器（拷到任何仓直接跑）
python3 skills/skill-distillation-lighthouse/scripts/scan-sensitive.py --root <仓>

# 结构校验器
python3 skills/skill-distillation-lighthouse/scripts/verify-structure.py --root <仓>

# 骨架生成器
bash skills/skill-distillation-lighthouse/scripts/new-skill-scaffold.sh \
     --target ./new-repo --name new-skill --description "..."
```

## 改扫描规则的三步（缺一不可）

1. 改 `scripts/scan-sensitive.py`
2. **同时**改 `tests/test_check_repo.py`，补阳性样本（必须命中）
3. 跑**阳性对照**：拿未脱敏的真实素材喂扫描器，确认有命中

> 漏报永远没人发现，误报天天打扰你 —— 所以第 3 步不能省。

## 发布

改版本号要同步四处：`plugin.json` 的 `version`、`marketplace.json` 的
`metadata.version` 与 `plugins[0].version`、`CHANGELOG.md` 的版本标题。
`tools/check_repo.py` 会校验一致性。
