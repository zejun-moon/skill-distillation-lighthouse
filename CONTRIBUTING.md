# 贡献指南

这个仓库的价值全在**内容的真实性**上 —— 贡献的门槛不在代码，在「你有没有真的跑过」。

## 硬性要求

1. **先写实战报告，再写结论。**
   提交一个坑之前，先按 `field-reports/TEMPLATE.md` 写一份脱敏报告，
   记录：现象、当时的第一反应、实际原因、处理、**怎么确认的**。
2. **脱敏。** 按 `references/desensitization.md` 的替换表逐类过一遍。
   提交前 `python3 tools/check_repo.py` 必须退出码 0。
3. **规范文档本身也不能含真实标识。** 要脱敏的具体账号名只能出现在
   `scan-sensitive.py` 的规则定义里（自带 `# scan: allow` 豁免标记）。
4. **标注验证状态。** 实测的写「实测」，据源码/文档推断的写「推断」，
   没验证的写「未测」。**不要把推测写成结论。**
5. **每个断言都要能被复现。** 写进文档的命令、配置片段，
   要能说明为什么这样写、怎么验证它对。

## 提交信息

Conventional Commits，squash 合并：

| 前缀 | 用途 |
|---|---|
| `feat:` | 新增能力（脚本 / 章节 / 工具） |
| `fix:` | 修 bug |
| `docs:` | 文档调整 |
| `pitfall:` | **新增坑条目**（最常用） |
| `report:` | 新增/更新实战报告 |
| `ci:` | 流水线与自检工具 |

PR 描述要写清：改了什么、为什么改、**验证状态**（实测 / 推断 / 未测）。

## 改扫描规则（最容易出事的地方）

`scripts/scan-sensitive.py` 的规则一改，**必须同时**改 `tests/test_check_repo.py`：

- 加一条规则 → 补**阳性**样本（必须命中）
- 放宽规则 → 补**阴性**样本（不得误报）

并且要跑**阳性对照**：

```bash
# 拿**未脱敏**的真实素材喂扫描器 → 必须有命中
python3 skills/skill-distillation-lighthouse/scripts/scan-sensitive.py \
     --root <你的真实工作区> --quiet
```

命中数为 0 → 扫描器是摆设，**必须修**。

> 一个扫不出东西的扫描器比没有扫描器更危险：
> 误报天天打扰你（你会习惯并忽略），漏报永远没人发现。

## 加一个新坑

1. 写 `field-reports/YYYY-MM-DD-<主题>.md`（脱敏）
2. 在 `references/pitfalls.md` 加一条「现象 → 原因 → 处理」
3. 在报告里标 `状态：promoted → pitfalls.md #N`
4. **能自动检测的** → 在 `scripts/` 里加判定，并补 `tests/`
5. 更新 `field-reports/README.md` 的索引表
6. 更新 `CHANGELOG.md` 的 `[Unreleased]`
7. 跑 `python3 tools/check_repo.py` 与 `python3 -m unittest discover -s tests`

## 不要做的事

- ❌ 不要提交任何真实环境信息（哪怕是"无害"的域名）
- ❌ 不要在规范文档里写出要脱敏的具体标识（规范本身就是泄露源）
- ❌ 不要把 `SKILL.md` 写成 500 行以上（细节放 `references/`）
- ❌ 不要在文档里写「正确但没信息量」的内容
- ❌ 不要在 SKILL.md 里写「自动执行会改变业务行为的动作」——
  发布到公网、删远端资源、轮换凭据，一律写成「向用户确认」
- ❌ 不要只改当前文件就算脱敏完成 —— 公开仓的 git 历史里每一版都在
