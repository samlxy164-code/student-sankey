"""Explore study time, absences and grades in an interactive Sankey diagram."""

import argparse
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


PROJECT_DIR = Path(__file__).resolve().parent
STUDY_LABELS = ["<2 hours", "2–5 hours", "5–10 hours", ">10 hours"]
ABSENCE_LABELS = ["0 absences", "1–5 absences", "6–10 absences", "11+ absences"]
GRADE_LABELS = ["0–9 points", "10–14 points", "15–20 points"]
STAGES = {
    "study_group": STUDY_LABELS,
    "absence_group": ABSENCE_LABELS,
    "grade_group": GRADE_LABELS,
}
NODE_COLORS = [
    "#2F5F98", "#4C83B5", "#77A6C8", "#ACCBDD",
    "#507C79", "#6C9992", "#99BBB1", "#C5D7C8",
    "#CF8F7C", "#D7C8A4", "#609989",
]
LINK_COLORS = {
    "study_group": "rgba(76,131,181,0.32)",
    "absence_group": "rgba(108,153,146,0.32)",
}


def load_and_prepare(csv_path):
    """保留合法的零分和相同特征组合，每行仍代表一条学生记录。"""
    # AI 辅助：CSV 读取和基础 DataFrame 操作的语法。
    raw = pd.read_csv(csv_path, sep=None, engine="python")
    raw.columns = raw.columns.str.strip()
    required = ["studytime", "absences", "G3"]
    missing = set(required) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")

    # 人工设计：保留有效的零分及重复特征组合，校验编码、整数和取值范围。
    data = raw[required].apply(pd.to_numeric, errors="coerce")
    valid = (
        data.notna().all(axis=1)
        & data["studytime"].isin([1, 2, 3, 4])
        & data["absences"].between(0, 93)
        & data["absences"].eq(data["absences"].round())
        & data["G3"].between(0, 20)
        & data["G3"].eq(data["G3"].round())
    )
    data = data.loc[valid].astype(int).copy()
    if data.empty:
        raise ValueError("No valid records remain after validation.")

    # 学习时长沿用数据集的四档编码；缺勤次数与成绩的分组由作者设计。
    data["study_group"] = pd.Categorical(
        data["studytime"].map(dict(enumerate(STUDY_LABELS, start=1))),
        categories=STUDY_LABELS, ordered=True,
    )
    data["absence_group"] = pd.cut(
        data["absences"], bins=[-1, 0, 5, 10, float("inf")], labels=ABSENCE_LABELS,
    )
    data["grade_group"] = pd.cut(
        data["G3"], bins=[-1, 9, 14, 20], labels=GRADE_LABELS,
    )
    return data


def build_sankey(data):
    """汇总相邻类别计数并生成交互式桑基图。"""
    # 人工设计节点及悬停提示；AI 辅助实现节点映射、连线汇总和 Plotly 配置。
    node_keys = [(stage, label) for stage, labels in STAGES.items() for label in labels]
    node_ids = {key: index for index, key in enumerate(node_keys)}
    sources, targets, values, link_colors = [], [], [], []
    stages = list(STAGES)
    for left, right in zip(stages, stages[1:]):
        counts = data.groupby([left, right], observed=True).size()
        for (left_label, right_label), count in counts.items():
            sources.append(node_ids[(left, left_label)])
            targets.append(node_ids[(right, right_label)])
            values.append(int(count))
            link_colors.append(LINK_COLORS[left])

    figure = go.Figure(go.Sankey(
        arrangement="snap",
        node={
            "label": [label for _, label in node_keys],
            "color": NODE_COLORS, "pad": 24, "thickness": 21,
        },
        link={
            "source": sources, "target": targets, "value": values, "color": link_colors,
            "hovertemplate": "%{source.label} → %{target.label}<br>Records: %{value}<extra></extra>",
        },
    ))
    figure.update_layout(
        title="Study time, absences and final grades",
        font={"family": "Arial", "size": 14},
    )
    return figure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=PROJECT_DIR / "student-mat.csv")
    parser.add_argument("--output", type=Path, default=Path("student_sankey.html"))
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    data = load_and_prepare(args.data)
    figure = build_sankey(data)
    figure.write_html(str(args.output), include_plotlyjs=True, auto_open=not args.no_browser)
    print(f"{len(data)} valid records. Chart: {args.output.resolve()}")


if __name__ == "__main__":
    main()
