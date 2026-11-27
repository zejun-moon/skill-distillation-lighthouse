# 仓库结构与发布

> 骨架沿用 `*-lighthouse` 系列（一个主题一个仓）的结构。
> 下面每一项都标了「为什么」，没写理由的项不要照抄。

---

## 1. 标准骨架

```text
<repo-name>/
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md                 # 入口：主流程 + 判断标准 + 排障入口 + 边界
│       ├── references/              # 按需加载的细节（主流程 < 500 行）
│       │   ├── pitfalls.md          #   坑表：现象 → 原因 → 处理
│       │   └── <topic>.md           #   某个子领域的详细配方
│       └── scripts/                 # 可执行判定（能自动判的别让人肉比对）
├── field-reports/                   # 每次真实执行的脱敏报告
│   ├── README.md                    #   索引（自检会验每份报告都被索引）
│   ├── TEMPLATE.md                  #   报告模板
│   └── YYYY-MM-DD-<topic>.md
├── tools/
│   └── check_repo.py                # 仓库自检（结构/版本/索引/敏感信息）
├── tests/
│   └── test_check_repo.py           # 扫描器的阳性 + 阴性样本
├── .claude-plugin/
│   ├── plugin.json                  # 版本 / 描述 / 关键词
│   └── marketplace.json              # 版本 / 插件清单
├── .github/workflows/ci.yml         # 自检 + 单测 + 语法 + 冒烟 + 密钥扫描
├── AGENTS.md                        # 给维护本仓的 AI agent（地图 + 铁律 + 工作流）
├── CLAUDE.md                        # 插件形态的本地开发说明
├── CHANGELOG.md                     # 变更记录（三处版本一致）
├── CONTRIBUTING.md                  # 贡献门槛（先写报告，再提炼）
├── SECURITY.md                      # 什么不能公开 + 泄露了怎么办
├── ROADMAP.md                       # 下一步做什么 + 已知缺口
├── README.md / README.en.md         # 双语入口
├── LICENSE                          # MIT
├── .gitignore / .gitattributes
```

### 为什么要这些

| 目录 | 存在的理由 |
|---|---|
| `skills/<name>/` | **一仓一技能**时最简单；一仓多技能时按主题分目录。`name` 必须 == 目录名 |
| `references/` | AI 只在需要时才读细节。主流程保持可扫读 |
| `scripts/` | 把「对/错」二元判定自动化，输出即通过条件 |
| `field-reports/` | 原始素材 + 失败样本。**报告是坑表的证据来源** |
| `tools/check_repo.py` | 把纪律变成**门禁**：提交前跑，CI 再跑 |
| `tests/` | 扫描器的阳性/阴性样本。**改规则必须同时改测试** |
| `.claude-plugin/` | 让 Claude Code 能 `plugin install`，而不是手工拷目录 |

---

## 2. 版本号三处一致

| 位置 | 字段 |
|---|---|
| `.claude-plugin/plugin.json` | `version` |
| `.claude-plugin/marketplace.json` | `metadata.version` |
| `.claude-plugin/marketplace.json` | `plugins[0].version` |
| `CHANGELOG.md` | 最新发布版本的标题行 |

**自检必须校验这四处一致**，否则插件管理器会读到错版本。

发版流程：

1. 同步改上面 4 处 + `CHANGELOG.md` 的 `[Unreleased]` → 新版本号
2. 跑 `python3 tools/check_repo.py`（会校验一致性）
3. 提 PR → CI 通过 → 合并
4. 打 `vX.Y.Z` 标签

> **标签不要手工乱打**（改了版本号却没打标签 = 用户装不到新版）。

---

## 3. CI 该跑什么

```yaml
jobs:
  self-check:   # 结构 / 版本 / 报告索引 / 敏感信息
    - python3 tools/check_repo.py
  unit-tests:   # 扫描器的阳性 + 阴性样本
    - python3 -m unittest discover -s tests -v
  shell-syntax: # 所有 .sh 的语法
    - find . -name '*.sh' -not -path './.git/*' -print0 | xargs -0 -r -n1 bash -n
  smoke:        # 生成器能跑、产物符合预期
    - python3 skills/.../scripts/gen-dashboard.py --output /tmp/d.json
  gitleaks:     # 兜底扫历史提交里的密钥
```

**smoke 这一步别省**：结构校验只能证明 JSON 合法，证明不了生成器能跑通。
让 smoke 断言**产物的不变量**（面板数、id 连续、某些字段不存在），
这样改脚本时出错能立刻被 CI 拦住。

---

## 4. 自检工具该检查什么（至少四类）

| # | 类别 | 具体项 |
|---|---|---|
| 1 | **技能结构** | frontmatter 存在且 `name` == 目录名 · `description` 存在且 ≤1024 字符 · 正文 <500 行 · **SKILL.md 引用的每个路径真实存在** · shell 脚本有 shebang + 可执行位 |
| 2 | **版本一致** | 四处版本号一致 |
| 3 | **报告索引** | 每份报告 frontmatter 键齐全 · 都被 `field-reports/README.md` 索引 |
| 4 | **敏感信息** | 见 [`desensitization.md`](desensitization.md) §5 |

> 第 1 类里的「**引用的路径都存在**」是最容易被忽略、但最有用的一条：
> SKILL.md 里写了个不存在的 reference，AI 会照着找，然后卡死或幻觉。

---

## 5. 发布到公网

| 项 | 做法 |
|---|---|
| 仓库可见性 | **public**（公开仓才谈得上「AI 直接读」） |
| 许可 | MIT（技能类内容基本都用它） |
| 克隆 | `git clone https://github.com/<owner>/<repo>.git` |
| 作为插件 | `claude plugin install ./<repo>` |
| 作为技能 | 把 `skills/<name>/` 放进 skills 目录 |

### 发布后必做：回读校验

**「接口返回成功」≠「内容正确」。** 发布完逐文件回读并比对：

```python
# 逐文件 sha256 比对远端与本地
remote = get_file_contents(owner, repo, path)   # 内容
local  = open(path).read()
assert sha256(remote) == sha256(local)
```

同时用**递归 tree** 比对文件清单（只看根目录会漏掉子目录里的文件）。

> ⚠️ **逐文件推 + 部分失败 = 半成品仓。** 回读校验能把这件事当场抓出来。

---

## 6. 嵌套 git 仓的注意事项

技能仓通常放在某个工作区里，而那个工作区自己也是个 git 仓：

- 给技能仓加进**外层仓的 `.gitignore`**（否则外层仓会把它当 gitlink 或重复跟踪）
- 技能仓自己的 `.git` 目录**不提交**
- 备份放**仓外**（如 `/var/backups/<用途>-<日期>/`，权限 700）
- 产物不要落在 `/root` 根目录（多人/多 Agent 共用）

---

## 7. 一个仓 vs 多个技能

| 场景 | 建议 |
|---|---|
| 一个主题一套完整流程（如"系统原地升级"） | **一仓一技能**（lighthouse 模式） |
| 一堆互不相干的小技能（"怎么用某个 CLI"） | **一仓多技能**（skills 目录下并列） |
| 技能之间强依赖（共享脚本/坑表） | 一仓多技能 |
| 技能会独立演化、版本独立 | 一仓一技能 |

判断口径：**能独立发版、独立被 clone、独立被别人引用** → 一仓一技能。

---

## 8. 发布前最后确认

- [ ] `python3 tools/check_repo.py` 退出码 **0**
- [ ] `python3 -m unittest discover -s tests` 全绿
- [ ] **阳性对照**跑过（未脱敏素材 → 扫描器有命中）
- [ ] 人工复核过「语义性泄露」（规模、弱点、组织信息）
- [ ] README 里的 clone 地址、徽章、命令**都是真的**
- [ ] 文档声称存在的东西**真的存在**（CI 文件、脚本、插件清单）
- [ ] 版本号四处一致
- [ ] CHANGELOG 写了这一版
- [ ] **远端回读校验**：文件清单 + 内容 sha256 全部一致
