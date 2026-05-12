---
name: init-harness
description: 在任意工程中初始化一套中文 Harness 目录、模板和项目级 memory 初稿。适用于用户要在当前目录或指定目录创建 docs/ai 骨架、生成 task brief / verification feedback 模板，并基于目标目录生成一份主 memory。
---

# init-harness

这个 skill 用来在一个工程里直接落地 Harness 初始骨架，而不是只讨论方案。

## 使用时机

在以下场景使用：

- 用户要在一个新工程里初始化 Harness
- 用户要把现有 Harness 范式迁移到其他工程
- 用户希望在当前工程根目录生成 `docs/ai`，并根据当前目录或指定目录生成 memory 初稿
- 用户希望自动生成一份项目级 memory 初稿
- 用户希望同时拿到任务状态机和分层评估模板
- 用户希望同时拿到缺陷回流和渐进式边界控制相关模板
- 用户希望管理外部在线文档、内部组件文档或接口文档的引用记录
- 用户希望在结构重构后，用任务接力的方式继续剩余功能开发
- 用户希望避免任务实例散落，希望按任务目录统一归档

## 默认规则

- 如果用户没有指定目标目录，默认使用当前工作目录
- 如果用户指定了目标目录，只把该目录作为 memory 初稿分析范围；`docs/ai` 仍生成在当前工作目录
- 每次只生成一份主 memory，文件名使用 `<目标目录名>-memory.md`
- 默认生成任务简报、反馈、Code Review、分层评估、缺陷回流、外部资料这六类模板
- README 和任务简报模板默认包含“任务接力 / 路径迁移 / 结构权威来源”规则
- 默认采用“任务实例按任务目录归档”的结构：共享资产放在 `memory / references / templates`，具体任务材料统一放在 `tasks/<task-id>/`
- 默认不写入浏览器 / MCP / Arc 等本机环境细节
- 只有用户明确要求时，才在 README 中附加浏览器侧验证可选章节

## 执行方式

优先使用 `scripts/init_harness.py`，不要手写一套新的目录和模板。

默认命令：

```bash
python3 "<skill-dir>/scripts/init_harness.py"
```

指定目录时：

```bash
python3 "<skill-dir>/scripts/init_harness.py" --target-path "<target-path>"
```

上面的命令会分析 `<target-path>`，但 `docs/ai` 仍创建在当前工作目录下。

需要附加浏览器验证章节时：

```bash
python3 "<skill-dir>/scripts/init_harness.py" --target-path "<target-path>" --include-optional-browser-section
```

## 输出要求

初始化完成后，应明确告诉用户：

- 初始化目标目录
- memory 分析目录
- 创建或保留了哪些 `docs/ai` 子目录
- 生成的主 memory 文件名
- README 中实际采用的 memory 路径
- 是否启用了可选浏览器验证章节
- 哪些已有文件被保留未覆盖

## 何时读取 references

- 如果要理解 memory 初稿是如何生成的，读取 `references/memory-generation.md`
- 如果要理解可选浏览器章节何时启用，读取 `references/optional-browser-section.md`
