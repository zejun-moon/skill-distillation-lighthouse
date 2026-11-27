---
name: skill-distillation-lighthouse
license: MIT
description: 把一次真实的运维/开发实战沉淀成 AI 可直接加载调用的技能仓——实战脱敏报告 → 坑表提炼 → 判定脚本化 → SKILL.md 主流程 → 版本化发布，并配套一套机器可执行的脱敏规范与自检门禁。凡是用户提到「把经验沉淀成技能」「写一个 skill」「做脱敏」「敏感信息扫描」「发布到 GitHub 给 AI 用」「技能仓怎么组织」「怎么让 AI 读仓库调用技能」「代码/文档要不要脱敏才能公开」「仓库自检怎么写」等场景，都要用本技能——即使用户没说「技能」而只说「这个经验能不能复用」「怎么把踩过的坑留下来」「发布到 GitHub 会不会泄露内网信息」。Distill real operations experience into AI-loadable skill repositories: desensitized field reports, pitfall tables, executable verification scripts, SKILL.md structure, and a machine-enforced redaction standard.
---

# 从一次实战到一个技能仓

一套**已经被真实跑过一遍**的沉淀流程：从「刚做完一次排障」到「GitHub 上一个 AI 能自动加载的技能仓」。

本技能沉淀自一次真实产出（把内网 K8s 环境的「Spring Boot 指标接入」经验做成公开技能仓），
全程含 **9 条流程坑**与一整套**脱敏规范**。

## 什么时候不要用本技能

- 只是想**记一条笔记** → 用知识库/笔记，别过度工程化（见 §「知识库 vs 技能仓」）
- 内容**不能公开**且不打算发 GitHub → 只需做脱敏，不必做技能仓结构
- 经验只有**一次性**价值（纯临时故障、很快会变的配置） → 写进事故记录，不进技能仓
- 已有成熟技能仓只是**加一个面板/一条坑** → 直接改，别走全流程

---

## 核心判断：知识库 vs 技能仓

先问一句：**这条经验会不会被重复用？**

| | 知识库 / 笔记 | 技能仓 |
|---|---|---|
| 形态 | 长篇散文 | 可执行脚本 + 判据表 |
| AI 怎么用 | 全文捞关键词，容易漏 | 按步骤走，每步有**通过条件** |
| 可验证性 | 说不清哪句是对的 | 每条标注 **实测 / 推断 / 未测** |
| 失败样本 | 通常不写 | **专门记**（当时为什么判断错） |
| 更新 | 靠人记得改 | `CHANGELOG` + CI + 语义化版本 |
| 保密 | 容易夹带真实信息 | 机器扫描门禁 + CI 密钥扫描 |

**判断口径**：经验要满足「**下次遇到同类问题能直接照做**」，才值得做成技能仓；
只是「需要知道有这么回事」，写知识库。

---

## 第 1 步 · 划定边界（决定做不做、做到哪）

先明确三件事，写进 `spec.md`：

| 项 | 要回答的问题 | 反例 |
|---|---|---|
| **目标** | 沉淀后 AI/人要能完成什么动作？ | 「记录一下 Prometheus 的坑」 |
| **范围** | 做 / **明确不做** | 不写「大概都搞一下」 |
| **可发布性** | 能不能公开？哪些内容**必须**脱敏？ | 默认「先发出去再说」 |

> ⚠️ **先判可发布性再动手写。** 做到一半才发现核心证据不能公开，返工成本最高。

---

## 第 2 步 · 收集实战素材（只收真实发生过的）

素材来源优先级：**实测记录 > 现场日志 > 源码 > 官方文档 > 记忆**。

每条素材必须能回答：**「我怎么知道这是真的？」**

- ✅ 「Prometheus `/api/v1/targets` 显示该 job 的 `lastError` 为 404」——可复现
- ❌ 「听说 ServiceMonitor 不加标签会不生效」——不可复现，是二手信息

**同时收集失败样本**：当时第一次判断错在哪、后来靠什么证据纠正的。
这是整个技能仓里**最值钱的部分**——知识库不会写，但下一个人一定会再犯同样的错。

---

## 第 3 步 · 写脱敏实战报告（`field-reports/`）

每个主题一份，格式见 [`field-reports/TEMPLATE.md`](../../field-reports/TEMPLATE.md)。

报告的 frontmatter 是**机器可校验**的：

```yaml
---
date: 2026-11-27
environment: Kubernetes 1.29 / Prometheus v3.13.0 / Grafana 10.3.3
result: success | partial | failed
duration_hours: 3
skill_version: 0.1.0
operator: agent
---
```

### 脱敏在这一步最关键

报告里最容易夹带真实信息（真实 IP、真实 ns、真实域名、内部 uid）。
**逐类替换表**见 [`references/desensitization.md`](references/desensitization.md) —— 动手前先读它。

三条底线：

1. **真实信息一律替换成占位符**，示例用 `10.0.0.x` / `example.com`
2. **占位符不能"像真的"** —— 写 `10.0.0.1` 而不是 `10.0.0.x`，读者会以为那是真地址 <!-- scan: allow —— 本行是"反例"示范 -->
3. **报告写完立刻跑扫描器**，不要等到提交前

---

## 第 4 步 · 提炼：把报告变成「坑表 + 判定 + 主流程」

对报告里的每个问题做一次**四选一**判断（这是沉淀的核心动作）：

| 判断 | 去处 | 判据 |
|---|---|---|
| 以后还会遇到 | `references/pitfalls.md` | 换个环境/换个人还会踩 |
| **能自动检测** | `scripts/` 里加判定 | 有明确的对/错二元结果 |
| 能自动修复 | 改脚本 + 补测试 | 修复动作可逆且确定 |
| 只是这次的特例 | **只留在报告里** | 换台机器就不成立 |

四选一之后，问题就**不该再只躺在报告里**。每条提炼出来的结论，在报告里标注去向：

```markdown
| 问题 | 去向 |
|---|---|
| ServiceMonitor 漏标签导致静默失效 | `pitfalls.md` #1 |
| target up 但查不到序列 | `scripts/verify-*.sh` |
```

### 坑表的格式：**现象 → 原因 → 处理**

```markdown
### 1. ✅ ServiceMonitor 没打 `release` 标签 → 静默失效
- **现象**：对象存在、无报错，但 target 数 = 0
- **原因**：Prometheus 的 `serviceMonitorSelector` 是 `matchLabels{...}`，不命中直接过滤
- **处理**：给对象补上该 label；先打印选择器实际取值，不要照抄别人的
```

**「现象」要写成能被认出来的样子**（用户在半夜值班时看到的就是「现象」）。
**「原因」要能解释为什么**（否则下次换个场景就不适用了）。
**「处理」要给可直接执行的动作**。

---

## 第 5 步 · 写主流程（`SKILL.md`）

`SKILL.md` 是**入口**，不是手册。它只回答四个问题：

1. **什么时候用 / 什么时候不用**
2. **主流程**：从哪开始、每步做什么、做完怎么验
3. **排障入口**：出错了去哪个 reference 查
4. **边界**：哪些动作**会改变业务行为**，必须向用户确认

### frontmatter 是 AI 的路由依据 —— 必须写好

```yaml
---
name: skill-distillation-lighthouse      # 必须 == 目录名
license: MIT
description: <中英双语 + 触发词枚举，≤ 1024 字符>
---
```

**description 怎么写**（决定 AI 会不会加载它）：

- ✅ **枚举触发场景**：「凡是用户提到 X / Y / Z 场景，都要用本技能」
- ✅ **写同义说法**：「即使用户没说『脱敏』而只说『会不会泄露内网信息』」
- ✅ **中英双语**（团队里两种语言提问时都能命中）
- ❌ 只写一句概括（「一个脱敏工具」）—— AI 命中不了
- ❌ 写成说明书（「本技能包含以下功能」）—— 没有触发词

### 正文 **< 500 行**：细节一律进 `references/`

| 内容 | 放哪 |
|---|---|
| 主流程、判断标准、排障入口、边界 | `SKILL.md` |
| 坑的完整清单 | `references/pitfalls.md` |
| 某个子领域的详细配方 | `references/<topic>.md` |
| 可执行脚本 | `scripts/` |

**超过 500 行就该拆**，不是"写得详细"，是"该拆了"。

---

## 第 6 步 · 机器门禁：把纪律变成脚本

> **人眼不可靠。** 本技能自己的开发过程就撞上了：扫描器把**自己的规则定义**和**测试样本**也扫了出来
> （自指误报），而对真实的 ServiceMonitor 清单却**命中 0 处**（规则过窄，漏了内部 ns 前缀）。
> 这两件事都只有跑对照实验才发现得了。

所以技能仓**必须**带一个自检工具，至少四类检查：

| # | 检查 | 抓什么 |
|---|---|---|
| 1 | **技能结构** | frontmatter 合法、description 长度、正文行数、**引用的路径都真实存在**、脚本有 shebang+可执行位 |
| 2 | **版本一致** | `plugin.json` == `marketplace.json` == `CHANGELOG` 最新版本 |
| 3 | **报告索引** | 每份报告 frontmatter 齐全、都被 README 索引 |
| 4 | **敏感信息** | 真实 IP / 内网域名 / 私有仓库地址 / 内部 uid / 账号 / 口令 / 私钥 / token / 邮箱 |

配套两条工程纪律：

- **改扫描规则必须同时改测试**，并补**阳性**样本（必须命中）
- **每次改规则都跑阳性对照**：拿**未脱敏**的真实素材喂扫描器，
  命中数为 0 → 扫描器是摆设，必须修

工具：`scripts/scan-sensitive.py`（通用版，可直接拷到任何仓）、
`scripts/verify-structure.py`、`tools/check_repo.py`（本仓自检）。

---

## 第 7 步 · 发布

| 项 | 做法 |
|---|---|
| 仓库 | **public**（公开仓才谈得上「AI 直接读」）· MIT |
| 目录 | `skills/<name>/` 一仓一技能，或一仓一主题 |
| 版本 | 三处同步：`plugin.json` / `marketplace.json` / `CHANGELOG` |
| CI | 自检 + 单测 + 脚本语法 + 生成器冒烟 + **gitleaks** |
| 插件 | `.claude-plugin/` 让 Claude Code 能 `plugin install` |
| 安装 | `git clone` 后放进 skills 目录，或作为插件安装 |

发布前的最后一道：**远端内容回读校验**（逐文件 sha256 比对本地）。
「接口返回成功」≠「内容正确」。

---

## 边界：这些动作一律先问用户

- **发布到公网**（新建公开仓、推送、删仓）
- **重建业务镜像 / 改线上配置**
- **删除远端资源**（仓库、文件、目录）
- **任何不可逆的凭据轮换**

---

## 配套文件

| 文件 | 内容 |
|---|---|
| [`references/desensitization.md`](references/desensitization.md) | **脱敏规范（核心）**：威胁模型、逐类替换表、七条硬规则、豁免机制、泄露处置 |
| [`references/skill-authoring.md`](references/skill-authoring.md) | 技能写作规范：frontmatter、description 触发词、正文拆分、诚实标注、边界声明 |
| [`references/repo-layout.md`](references/repo-layout.md) | 目录结构、版本一致、发版流程、CI 该跑什么 |
| [`references/pitfalls.md`](references/pitfalls.md) | **9 条流程坑**（做技能仓本身的坑） |
| [`references/review-checklist.md`](references/review-checklist.md) | 提交前 / 合并前 / 发版前三张清单 |
| [`scripts/scan-sensitive.py`](scripts/scan-sensitive.py) | **通用脱敏扫描器**（可拷到任何仓用） |
| [`scripts/verify-structure.py`](scripts/verify-structure.py) | 技能仓结构校验 |
| [`scripts/new-skill-scaffold.sh`](scripts/new-skill-scaffold.sh) | 一键生成技能仓骨架 |
| [`tools/check_repo.py`](../../tools/check_repo.py) | 本仓自检（四类检查） |
| [`field-reports/`](../../field-reports/) | 脱敏实战报告（做技能仓这件事本身的实战） |

## 来源与可信度

内容来自一次真实产出（2026-11-27 实测）：把内网 K8s 环境的实战经验做成公开技能仓并发布。
坑条目为**实测复现**；用 ✅ 标注「实测确认」、📄 标注「据源码/文档推断」。
本技能**不覆盖**：私有化部署的技能分发、模型训练数据构建、技能效果评测。
