#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".next",
    ".nuxt",
    ".cache",
    ".turbo",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "tmp",
    "temp",
    "__pycache__",
    ".venv",
    "venv",
}

ROOT_PRIORITY = [
    "src",
    "components",
    "pages",
    "services",
    "redux",
    "store",
    "core",
    "utils",
    "hooks",
    "containers",
    "packages",
    "apps",
    "server",
    "api",
    "scripts",
    "docs",
    "tests",
]

STRUCTURE_RULES = [
    ({"schema", "const", "form", "validate"}, "涉及复杂配置链路时，优先检查 schema / const / form / validate 是否需要联动调整。"),
    ({"services", "api"}, "涉及接口接入时，优先确认 service 层封装、调用参数和返回结构是否一致。"),
    ({"components", "hooks"}, "涉及复杂交互时，优先拆分组件渲染逻辑与状态同步逻辑，避免在单个组件内堆积分支。"),
    ({"pages", "components"}, "涉及页面级功能时，先明确页面入口，再反查相关组件、状态和数据流。"),
    ({"redux", "store"}, "涉及全局状态时，先确认状态归属和更新路径，再修改组件层表现。"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize docs/ai Harness structure for a project.")
    parser.add_argument(
        "--target-path",
        default=".",
        help="Directory to analyze for the initial memory draft. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--project-name",
        default=None,
        help="Optional project name override. Defaults to the target directory name.",
    )
    parser.add_argument(
        "--include-optional-browser-section",
        action="store_true",
        help="Include the optional browser validation section in README.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_if_missing(path: Path, content: str, created: list[str], skipped: list[str]) -> None:
    if path.exists():
        skipped.append(str(path))
        return
    path.write_text(content, encoding="utf-8")
    created.append(str(path))


def iter_relative_paths(target: Path) -> Iterable[Path]:
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        root_path = Path(root)
        for file_name in files:
            if file_name.startswith("."):
                continue
            yield (root_path / file_name).relative_to(target)


def get_top_level_entries(target: Path) -> list[str]:
    result: list[str] = []
    for name in ROOT_PRIORITY:
        if (target / name).exists():
            result.append(name)
    return result


def get_hotspot_paths(target: Path) -> list[str]:
    candidates = [
        "README.md",
        "package.json",
        "pnpm-lock.yaml",
        "package-lock.json",
        "yarn.lock",
        "tsconfig.json",
        "src",
        "src/components",
        "src/pages",
        "src/services",
        "src/redux",
        "src/core",
        "src/utils",
        "src/hooks",
        "src/containers",
        "components",
        "pages",
        "services",
        "redux",
        "core",
        "utils",
        "hooks",
        "containers",
        "scripts",
        "docs",
    ]
    found: list[str] = []
    for candidate in candidates:
        if (target / candidate).exists():
            found.append(candidate)
    return found[:12]


def detect_term_mapping(target: Path) -> list[str]:
    basename_set = {p.parent.name.lower() for p in iter_relative_paths(target)}
    mappings: list[str] = []
    if "services" in basename_set or (target / "services").exists() or (target / "src/services").exists():
        mappings.append("- 服务层：通常指接口封装、请求参数和返回结构处理所在目录。")
    if "components" in basename_set or (target / "components").exists() or (target / "src/components").exists():
        mappings.append("- 组件层：通常指页面拼装中可复用的 UI 与交互片段。")
    if "pages" in basename_set or (target / "pages").exists() or (target / "src/pages").exists():
        mappings.append("- 页面层：通常指功能入口、路由承载和页面级状态组织。")
    if "redux" in basename_set or (target / "redux").exists() or (target / "src/redux").exists():
        mappings.append("- 状态层：通常指全局状态、action、reducer 或 store 相关实现。")
    return mappings


def detect_structure_rules(target: Path) -> list[str]:
    basename_set = {part.lower() for path in iter_relative_paths(target) for part in path.parts}
    results: list[str] = []
    for required_parts, rule in STRUCTURE_RULES:
        if required_parts.issubset(basename_set):
            results.append(f"- {rule}")
    if not results:
        results.extend(
            [
                "- 初始化阶段优先按“入口页面 / 组件 / 服务 / 状态 / 校验”这些结构层次定位代码。",
                "- 修改前先确认功能入口和数据流，不要只根据命名猜测目录职责。",
            ]
        )
    return results


def build_engineering_map(target: Path) -> list[str]:
    entries = get_top_level_entries(target)
    descriptions = {
        "src": "主要源码目录，通常包含页面、组件、服务、状态和基础能力。",
        "components": "组件目录，通常承载可复用 UI 和交互逻辑。",
        "pages": "页面目录，通常是功能入口和路由承载位置。",
        "services": "服务目录，通常封装接口请求、DTO 和数据转换。",
        "redux": "状态目录，通常包含 action、reducer、store 等全局状态实现。",
        "store": "状态目录，通常包含全局状态容器和状态切片。",
        "core": "核心能力目录，通常放基础引擎、平台层能力或底层抽象。",
        "utils": "工具目录，通常放复用函数和轻量辅助逻辑。",
        "hooks": "Hooks 目录，通常放状态编排和可复用交互逻辑。",
        "containers": "容器目录，通常用于连接页面、组件和状态。",
        "packages": "子包目录，通常表示多包仓或模块化拆分结构。",
        "apps": "应用目录，通常表示多应用或多端入口结构。",
        "server": "服务端目录，通常放后端接口、脚本或本地服务实现。",
        "api": "接口目录，通常放 API 定义、调用层或协议相关内容。",
        "scripts": "脚本目录，通常放工程脚本、构建脚本或辅助工具。",
        "docs": "文档目录，通常存放规范、设计说明和开发文档。",
        "tests": "测试目录，通常存放单测、集成测试或测试资源。",
    }
    result = []
    for entry in entries:
        result.append(f"- `{entry}/`：{descriptions[entry]}")
    if not result:
        result.append("- 初始化阶段未扫描到典型工程目录，后续应在首轮任务中人工补充工程地图。")
    return result


def build_memory(project_name: str, target: Path) -> str:
    engineering_map = "\n".join(build_engineering_map(target))
    hotspot_paths = get_hotspot_paths(target)
    hotspot_text = "\n".join(f"- `{path}`" for path in hotspot_paths) if hotspot_paths else "- 初始化阶段尚未识别出稳定热点路径，后续在首轮任务后补充。"
    term_mapping = detect_term_mapping(target)
    term_text = "\n".join(term_mapping) if term_mapping else "- 初始化阶段未从代码结构中稳定提取出统一术语，后续在首轮任务中补充。"
    rule_text = "\n".join(detect_structure_rules(target))

    return f"""<!-- Generated by init-harness -->
# {project_name} 长期记忆

开始任何单任务前，先阅读本文件。单任务细节不要写在这里，应写入任务简报，参考 [任务简报模板](../templates/task-brief.template.md)。验证中发现的问题应先进入 [人工反馈模板](../templates/verification-feedback.template.md) 对应的反馈记录，再决定是否回写到这里。

## 使用原则

- 这里只记录跨任务稳定事实、热点入口、修改规律和已知坑。
- 每次任务结束最多补充 3 条可复用结论，避免长期记忆膨胀。
- 只写已经确认的结论，不写推测，不写过程，不写临时讨论。
- 每条尽量控制在两行内，便于后续快速扫读。

## 工程地图

{engineering_map}

## 热点路径

{hotspot_text}

## 术语对照

{term_text}

## 修改规律

{rule_text}

## 已知坑

- 初始化阶段不编造坑位；后续应在真实任务中只沉淀被反复验证过的风险点。

## 回写记录

- {current_date()}：首版长期记忆建立，初始化阶段已完成主目录扫描和骨架生成。
"""


def current_date() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d")


def render_template(template_path: Path, **kwargs: str) -> str:
    return read_text(template_path).format(**kwargs)


def main() -> int:
    args = parse_args()
    analysis_target = Path(args.target_path).expanduser().resolve()
    if not analysis_target.exists() or not analysis_target.is_dir():
        raise SystemExit(f"分析目录不存在或不是目录：{analysis_target}")

    output_root = Path.cwd().resolve()
    project_name = args.project_name or analysis_target.name
    memory_file_name = f"{project_name}-memory.md"

    skill_root = Path(__file__).resolve().parent.parent
    template_dir = skill_root / "assets" / "templates"

    ai_dir = output_root / "docs" / "ai"
    memory_dir = ai_dir / "memory"
    templates_dir = ai_dir / "templates"
    tasks_dir = ai_dir / "tasks"
    references_dir = ai_dir / "references"

    for path in (memory_dir, templates_dir, tasks_dir, references_dir):
        path.mkdir(parents=True, exist_ok=True)

    optional_browser_section = ""
    if args.include_optional_browser_section:
        optional_browser_section = render_template(template_dir / "optional-browser-section.md.tmpl")

    created: list[str] = []
    skipped: list[str] = []

    readme_content = render_template(
        template_dir / "README.md.tmpl",
        project_name=project_name,
        memory_file_name=memory_file_name,
        optional_browser_section=optional_browser_section,
    )
    task_brief_content = render_template(
        template_dir / "task-brief.template.md.tmpl",
        memory_file_name=memory_file_name,
    )
    verification_content = render_template(
        template_dir / "verification-feedback.template.md.tmpl",
        memory_file_name=memory_file_name,
    )
    review_content = render_template(
        template_dir / "code-review.template.md.tmpl",
        memory_file_name=memory_file_name,
    )
    evaluation_content = render_template(
        template_dir / "evaluation.template.md.tmpl",
        memory_file_name=memory_file_name,
    )
    defect_loop_content = render_template(
        template_dir / "defect-loop.template.md.tmpl",
        memory_file_name=memory_file_name,
    )
    external_reference_content = render_template(
        template_dir / "external-reference.template.md.tmpl",
        memory_file_name=memory_file_name,
    )
    memory_content = build_memory(project_name=project_name, target=analysis_target)

    write_if_missing(ai_dir / "README.md", readme_content, created, skipped)
    write_if_missing(templates_dir / "task-brief.template.md", task_brief_content, created, skipped)
    write_if_missing(
        templates_dir / "verification-feedback.template.md",
        verification_content,
        created,
        skipped,
    )
    write_if_missing(
        templates_dir / "code-review.template.md",
        review_content,
        created,
        skipped,
    )
    write_if_missing(
        templates_dir / "evaluation.template.md",
        evaluation_content,
        created,
        skipped,
    )
    write_if_missing(
        templates_dir / "defect-loop.template.md",
        defect_loop_content,
        created,
        skipped,
    )
    write_if_missing(
        templates_dir / "external-reference.template.md",
        external_reference_content,
        created,
        skipped,
    )
    write_if_missing(memory_dir / memory_file_name, memory_content, created, skipped)

    print("Harness 初始化完成")
    print(f"- Harness 落盘目录：{output_root}")
    print(f"- memory 分析目录：{analysis_target}")
    print(f"- 主 memory 文件：docs/ai/memory/{memory_file_name}")
    print(f"- README memory 路径：./memory/{memory_file_name}")
    print(f"- 可选浏览器验证章节：{'已启用' if args.include_optional_browser_section else '未启用'}")
    print(f"- 任务根目录：docs/ai/tasks/（建议每个任务创建独立子目录）")
    print(f"- 外部资料目录：docs/ai/references/")
    if created:
        print("- 新创建文件：")
        for item in created:
            print(f"  - {item}")
    if skipped:
        print("- 已存在且保留未覆盖的文件：")
        for item in skipped:
            print(f"  - {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
