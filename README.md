# skill-distillation-lighthouse

🗼 **A lighthouse for turning real experience into AI-loadable skills** ——
把一次真实的运维/开发实战，沉淀成 AI 能自动加载、照着就能做对的技能仓，
并配套一套**机器可执行的脱敏规范**。

```
实战 → 脱敏报告 → 坑表 → 判定脚本 → SKILL.md 主流程 → 版本化发布
                    ↑                                    ↑
              机器扫描门禁                        脱敏自检 + CI
```

## 这个仓回答两个问题

### ① 怎么沉淀成技能

不是"写篇文档"。是一套有明确关卡和通过条件的流程：

| 步 | 做什么 | 通过条件 |
|---|---|---|
| 1 | 划边界 | 明确「做什么 / 不做什么 / 能不能公开」 |
| 2 | 收素材 | 每条素材能回答「我怎么知道这是真的」 |
| 3 | 写脱敏报告 | `field-reports/` + frontmatter 齐全 |
| 4 | **四选一提炼** | 会再遇到 → 坑表；能自动判 → 脚本；只是特例 → 只留报告 |
| 5 | 写主流程 | SKILL.md < 500 行，description 带中英触发词 |
| 6 | 机器门禁 | 扫描器 0 命中 + 阳性对照有牙 |
| 7 | 发布 | 版本四处一致 + **远端回读校验** |

完整说明：[`SKILL.md`](skills/skill-distillation-lighthouse/SKILL.md)

### ② 脱敏怎么规范

不是"我记得删一下"。是一份**威胁模型 + 替换表 + 硬规则 + 机器门禁**：

- **威胁模型**：凭据 / 内网地址 / 私有仓库 / 账号身份 / 内部 uid / 组织信息 / 业务数据 / 截图
- **逐类替换表**：真实 IP → `10.0.0.x`、内网域名 → `example.com`、带前缀的 ns → 去前缀、uid → 参数化
- **七条硬规则**：默认全脱、宁多勿少、占位符要"一眼看出是占位符"……
- **语义性泄露**：机器抓不到的第三类（规模数字、内部弱点、组织信息）怎么处理
- **泄露之后**：不是改代码就完了（先轮换凭据）

完整规范：[`references/desensitization.md`](skills/skill-distillation-lighthouse/references/desensitization.md)

## 三个可以直接拿去用的工具

```bash
# ① 通用脱敏扫描器（可拷到任何仓库直接用）
python3 skills/skill-distillation-lighthouse/scripts/scan-sensitive.py --root /path/to/repo
python3 skills/skill-distillation-lighthouse/scripts/scan-sensitive.py --rules my-rules.json --json out.json

# ② 技能仓结构校验（结构 / 引用完整性 / 版本一致 / 报告索引）
python3 skills/skill-distillation-lighthouse/scripts/verify-structure.py --root /path/to/repo

# ③ 一键生成技能仓骨架（规范即代码）
bash skills/skill-distillation-lighthouse/scripts/new-skill-scaffold.sh \
     --target ./my-skill-repo --name my-skill \
     --description "把 X 做成 Y 的实战流程，凡是用户提到 Z 都要用本技能"
```

## 为什么不是知识库

| | 知识库 / 笔记 | 技能仓 |
|---|---|---|
| 形态 | 长篇散文 | 可执行脚本 + 判据表 |
| AI 怎么用 | 全文捞关键词，容易漏 | 按步骤走，每步有**通过条件** |
| 可验证性 | 说不清哪句是对的 | 每条标 **实测 / 推断 / 未测** |
| 失败样本 | 通常不写 | **专门记**（当时为什么判断错） |
| 更新 | 靠人记得改 | `CHANGELOG` + CI + 语义化版本 |
| 保密 | 容易夹带真实信息 | 机器扫描门禁 + CI 密钥扫描 |

## 目录结构

```text
skills/skill-distillation-lighthouse/
  SKILL.md                              # 主流程（七步 + 判断标准 + 边界）
  references/
    desensitization.md                  # 脱敏规范（核心）
    skill-authoring.md                  # 写作规范（frontmatter / 拆分 / 标注 / 边界）
    repo-layout.md                      # 目录结构 + 版本一致 + 发版 + CI
    pitfalls.md                         # 做技能仓本身的 9 条坑
    review-checklist.md                 # 提交前 / 合并前 / 发版前三张清单
  scripts/
    scan-sensitive.py                   # 通用脱敏扫描器
    verify-structure.py                 # 结构校验器
    new-skill-scaffold.sh               # 骨架生成器
field-reports/                          # 脱敏实战报告
tools/check_repo.py                     # 本仓自检（编排上面两个工具）
tests/                                  # 扫描器阳性/阴性样本
```

## 验证状态

| 项 | 结果 |
|---|---|
| 自检（结构 + 脱敏） | **0 问题** |
| 单元测试 | **全绿**（阳性 + 阴性样本） |
| 阳性对照 | 未脱敏真实素材 → 扫描器**有命中**（证明不是摆设） |
| 脚本语法 | 全部通过 |
| 骨架生成器烟测 | 能生成合规骨架并通过自检 |

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。核心要求：
**先写脱敏报告，再把结论提炼进 `references/pitfalls.md`**，
提交前 `python3 tools/check_repo.py` 必须退出码 0。

## 许可

[MIT](LICENSE)
