# memory 初稿生成规则

`init-harness` 默认生成一份单文件汇总型 memory，不自动拆分多个领域 memory。

## 目标

- 快速提供工程地图
- 给出一组可复用的热点路径
- 记录保守的结构级修改规律
- 为后续人工补充术语、已知坑和回写记录留出固定章节

## 扫描原则

- 默认扫描目标目录整体
- 如果用户指定了子目录，子目录只影响 memory 初稿内容，不改变 `docs/ai` 的落盘位置
- 忽略 `node_modules`、`.git`、`dist`、`build`、`coverage`、`.next`、`.nuxt`、`tmp`、`.cache` 等噪音目录
- 优先识别高频工程目录，例如 `src`、`components`、`pages`、`services`、`redux`、`core`、`utils`、`hooks`、`containers`

## 输出约束

- 不编造项目业务术语
- 不编造具体坑位
- 修改规律保持结构级、保守和可复用
- 所有结论以“初始化阶段已观察到”的口径表达
