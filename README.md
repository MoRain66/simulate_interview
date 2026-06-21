---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 6b83376620b183f1d97ad5b5334a1efd_54535bbd6d4711f18805525400d9a7a1
    ReservedCode1: RBpS92TsMpcDWHH/0HiToyXWxdZ6/EG847L4bP4Hz0jm1vY7b98PQj8Retveyo820reE8ptoSaMKkE7h4jRxg06yoZWB1uJWGZK+RxstPi8LESRbx5X/kNmIMhLbDF9hwWlJDs+G6gBkngjMWhIRXOd5ZIPdzrDCB44uA5uKMDVW64CyNf+CUpZliJg=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 6b83376620b183f1d97ad5b5334a1efd_54535bbd6d4711f18805525400d9a7a1
    ReservedCode2: RBpS92TsMpcDWHH/0HiToyXWxdZ6/EG847L4bP4Hz0jm1vY7b98PQj8Retveyo820reE8ptoSaMKkE7h4jRxg06yoZWB1uJWGZK+RxstPi8LESRbx5X/kNmIMhLbDF9hwWlJDs+G6gBkngjMWhIRXOd5ZIPdzrDCB44uA5uKMDVW64CyNf+CUpZliJg=
---

<p align="center"><img src="morain-logo.jpeg" alt="Morain Logo" width="120"></p>

# Simulate Interview — 模拟面试

## 概述

Simulate Interview 是一个 AI 模拟面试 Skill，根据你的个人简历自动生成口语化面试问题，在你回答后逐题评估打分，汇总错误问题并给出改进建议，最后生成可视化报告网页。

核心思路：**不写标准答案，模拟真实 HR 的压力追问**。AI 扮演资深 HR，依据简历中的学历、技能、项目经历等信息，生成口语化、带施压语气的问题（禁止书面语/论文腔），并在评估时绑定你的原始回答给出可照搬的改进方案。

---

## 解决问题

| 痛点 | 本 Skill 的解决方式 |
|------|-------------------|
| 不知道面试会被问什么 | 按维度自动生成 9~17 题，覆盖学历/薪资/技能/项目/情境 |
| 答完不知道好坏 | 每题按四维度打分（完整性30%/深度30%/逻辑性25%/一致性15%），给出亮点+问题+改进建议 |
| 同样的错误反复犯 | 历史错题自动回顾，下一轮面试中替换部分常规问题，逼你再答一次 |
| 看不到整体趋势 | 自动生成 report.html，折线图展示各轮分数变化，饼图展示错误维度分布 |

---

## 适合场景

- 求职前模拟面试，提前暴露回答短板
- 同一份简历反复练习（多轮面试，历史错题自动回顾）
- 多人简历对比评估（不同日期序号文件夹互不干扰）
- 面试经验复盘——回顾历史 EvaluateQuestions 和 WrQuestions，看自己进步轨迹

---

## 安装方法

将整个 `simulate_interview` 文件夹放置到以下路径：

```
你的工作目录\.claude\skills\simulate_interview\
```

目录结构：

```
simulate_interview/
├── SKILL.md                               # 核心工作流定义
├── scripts/
│   └── generate_report.py                 # 自动生成 report.html
└── references/
    ├── InterviewQuestions-format.md       # 问题生成格式模板
    ├── EvaluateQuestions-format.md        # 评估格式模板（四维度加权）
    ├── WrQuestions-format.md              # 错题汇总格式模板
    └── TRIGGER-RULES.md                   # 条件触发规则（施压追问）
```

Skill 加载后，Agent 会自动读取 SKILL.md 并遵循其中定义的两阶段工作流。

---

## 使用方法

### 基本流程

<p align="center"><img src="微信图片_20260621132329_128_26.png" alt="启动模拟面试命令" width="80%"></p>

1. **上传简历**：把你的简历文件发送给 Agent
2. **说一句触发词**：如「给我模拟面试」「根据我的简历生成面试问题」

<p align="center"><img src="微信图片_20260620232610_126_26.png" alt="面试问题概览" width="80%"></p>

3. **回答问题**：Agent 生成 InterviewQuestions.md 后，在文件中每个 `> 回答：___（待用户填写）___` 区域填入你的答案
4. **告诉 Agent 继续**：填完后回复「好了」「继续」，Agent 进入 Phase2 自动评估
5. **查看结果**：打开 `my-interview/report.html` 查看分数趋势图表

### 多轮面试

同一份简历可以反复面试。系统自动在同一天创建递增序号文件夹（`20260621_1`、`20260621_2`……），每轮独立储存。

多轮面试的核心特性是**历史错题回顾**：上一轮得分 <50 的题目会自动混入本轮，以「回顾」标记重新提问，确保你不会在同一个坑里掉两次。

---

## 框架介绍

### 两阶段工作流

```
Phase 1：生成问题
  读取简历 → 提取关键信息（学历/学校/薪资/技能/项目）→
  检查历史错题 → 按规则生成问题 + 条件触发施压追问 →
  写入 InterviewQuestions.md → 等待用户回答

Phase 2：评估 + 报告
  读取 InterviewQuestions.md → 逐题四维度评分 →
  记录错题（<50分）→ 合并历史错题 →
  产出 EvaluateQuestions.md + WrQuestions.md →
  自动执行 generate_report.py → 生成 report.html
```

### 条件触发规则

简历信息命中以下条件时，AI 会自动追加施压/追问类问题：

| 条件 | 触发动作 |
|------|---------|
| 学历为硕士以下 | 追问学历天花板 |
| 学校非 985/211/双一流 | 追问学校背书问题 |
| 期望薪资高于行业均值 | 施压「你凭什么值这个价」 |
| 个人优点仅抽象描述 | 追问具体证据 |
| 个人缺点过于圆滑 | 追问真实短板 |
| 项目经历偏宏观缺个人贡献 | 追问具体角色 |
| 技能列表含「精通」等绝对词 | 追问深度（10分自评） |

### 评估标准：四维度加权

<p align="center"><img src="微信图片_20260620232752_127_26.png" alt="AI评估标准展示" width="80%"></p>

每题 0~100 分，计算公式：

**总分 = 完整性 × 0.3 + 深度 × 0.3 + 逻辑性 × 0.25 + 一致性 × 0.15**

| 维度 | 权重 | 评估要点 |
|------|------|---------|
| 完整性 | 30% | 是否覆盖问题所有要点，有无关键信息遗漏 |
| 深度 | 30% | 是否有具体细节支撑（数据/步骤/案例），还是停留在表面 |
| 逻辑性 | 25% | 回答结构是否清晰，因果关系是否合理 |
| 一致性 | 15% | 前后回答是否矛盾，是否与简历信息一致 |

<p align="center"><img src="文科专业-新闻学-评估.png" alt="评估维度参考标准" width="80%"></p>

### 文件结构

```
my-interview/
├── report.html                    # 自动生成的可视化报告
├── 20260621_1/
│   ├── InterviewQuestions.md      # 本轮面试问题
│   ├── EvaluateQuestions.md       # 逐题评估结果
│   └── WrQuestions.md             # 错误问题汇总
├── 20260621_2/
│   └── ...
└── 20260621_3/
    └── ...
```

---

## 产出物介绍

<p align="center"><img src="微信图片_20260621132720_129_26.png" alt="模拟面试交互界面" width="80%"></p>

| 文件 | 内容 | 用途 |
|------|------|------|
| `InterviewQuestions.md` | 9~17 道口语化面试题，含简历摘要 | 填写答案的题目本 |
| `EvaluateQuestions.md` | 逐题四维度评分 + 亮点/问题/改进建议 + 整体建议 | 查看自己每道题的得分和短板 |
| `WrQuestions.md` | 得分 <50 的错题汇总表 + 参考答案 | 重点复盘，下轮面试自动回顾 |
| `report.html` | 折线图（分数趋势）+ 饼图（错题维度分布） | 一目了然看进步轨迹 |

<p align="center"><img src="微信图片_20260621133254_130_26.png" alt="逐题评估反馈" width="80%"></p>

<p align="center"><img src="微信图片_20260621153429_139_26.png" alt="分数变化趋势折线图" width="80%"></p>

<p align="center"><img src="微信图片_20260621142411_137_26.png" alt="错题维度分布饼图" width="80%"></p>

<p align="center"><img src="微信图片_20260621153436_140_26.png" alt="专业技能错题分布" width="80%"></p>

---

## 注意事项

1. **一切问题与答案均由 AI 生成**，仅供个人能力评测和练习参考，**不作为标准答案或面试通过保证**。AI 的判断可能存在偏差，最终以真实面试官的反馈为准。
2. 本 Skill 设计用于模拟真实 HR 的压力追问风格，部分问题可能带有轻度施压语气，仅用于训练临场应变能力，请勿误解为人身攻击。
3. 历史错题的参考答案同样由 AI 生成，虽已尽量绑定你的简历信息，但仍需你结合自身实际情况调整，不可照搬。
4. 单次面试（Phase 1 + Phase 2）约消耗 **15,000 ~ 22,000 Token**，具体取决于简历信息量、生成题目数量（9~17 题）以及用户回答的长度。其中 Phase 2 评估是消耗大头，因为逐题评估需要绑定原回答内容进行对比分析。

*（内容由AI生成，仅供参考）*
