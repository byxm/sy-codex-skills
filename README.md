# sy-codex-skills

这是一个用于沉淀和分发 Codex Skills 的仓库，采用可持续扩展的 monorepo 结构。

仓库中的每个 skill 都放在固定路径下，支持按路径单独安装。当前首个公开 skill 是 `git-sync-delivery`。

## 仓库结构

所有 skill 统一放在：

```text
skills/<skill-name>/
```

当前已收录的 skill：

- `git-sync-delivery`

对应安装路径：

- `skills/git-sync-delivery`

## 安装方式

使用 Codex skill installer，通过仓库名和路径安装：

```bash
scripts/install-skill-from-github.py --repo byxm/sy-codex-skills --path skills/git-sync-delivery
```

也可以直接使用 GitHub URL 安装：

```bash
scripts/install-skill-from-github.py --url https://github.com/byxm/sy-codex-skills/tree/main/skills/git-sync-delivery
```

安装完成后，重启 Codex 使新 skill 生效。

## 当前 Skill

### git-sync-delivery

用于代码改动完成后的交付流程自动化，主要覆盖：

- commit message 生成与确认
- 目标合并分支推理与确认
- 基于远程最新目标分支的预合并检查
- GitLab MR 创建
- 多分支 cherry-pick 同步交付

适用于需要将改动同步到多个版本分支的前端交付场景。

## 后续扩展

如果后续要新增 skill，继续按下面的目录规则添加即可：

```text
skills/<new-skill-name>/
```

每个 skill 建议至少包含：

- `SKILL.md`
- `agents/openai.yaml`（如果需要 UI 展示信息）

按需再补充以下可选目录：

- `scripts/`
- `references/`
- `assets/`

这样可以保证：

- 每个 skill 保持自包含，便于单独安装
- 仓库整体结构稳定，后续新增 skill 不需要重构
- 安装路径长期一致，便于团队共享和维护
