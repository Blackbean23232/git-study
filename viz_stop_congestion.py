"""정류장 혼잡도(시간당 평균 하차 인원)를 계산해 차트와 리포트(md)를 만든다."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from read_bus_data import load_data

BASE_DIR = Path(__file__).parent
FIG_DIR = BASE_DIR / "fig"
OUT_MD = BASE_DIR / "out_stop_congestion.md"

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

GRADE_COLORS = {"혼잡": "#c0392b", "보통": "#7f8c8d", "여유": "#2e86c1"}
TOP_N = 10


def build_metrics(route_stops, stops, alighting):
    """정류장 x 시간대 일평균 하차(hourly)와 정류장별 요약(summary)을 만든다."""
    n_days = alighting["date"].nunique()

    # 여러 노선이 지나는 정류장은 노선을 합산한 뒤 일평균을 낸다
    hourly = (
        alighting.groupby(["stop_id", "hour"])["alight_count"].sum().div(n_days)
        .unstack("hour")
    )

    summary = pd.DataFrame({
        "daily_avg": hourly.sum(axis=1),
        "peak_hour": hourly.idxmax(axis=1),
        "peak_avg": hourly.max(axis=1),
        "n_routes": route_stops.groupby("stop_id")["route_id"].nunique(),
    })
    # 하차 기록이 없는 정류장(어느 노선도 지나지 않음)은 제외된다
    summary = summary.dropna(subset=["peak_avg"])
    summary["n_routes"] = summary["n_routes"].astype(int)

    hi, lo = summary["peak_avg"].quantile([0.8, 0.2])
    summary["grade"] = "보통"
    summary.loc[summary["peak_avg"] >= hi, "grade"] = "혼잡"
    summary.loc[summary["peak_avg"] <= lo, "grade"] = "여유"

    summary = (
        summary.join(stops.set_index("stop_id")[["stop_name", "lat", "lon"]])
        .sort_values("peak_avg", ascending=False)
    )
    return hourly.loc[summary.index], summary


def build_daytype(alighting, n_stops):
    """평일/주말별 시간대 하차 인원 (정류장 1곳당 일평균)."""
    df = alighting.assign(
        daytype=alighting["date"].dt.dayofweek.ge(5).map({True: "주말", False: "평일"})
    )
    n_days = df.groupby("daytype")["date"].nunique()
    total = df.groupby(["daytype", "hour"])["alight_count"].sum().unstack("daytype")
    return total.div(n_days).div(n_stops)


def plot_top(summary):
    top = summary.head(TOP_N).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(top["stop_name"], top["peak_avg"],
                   color=top["grade"].map(GRADE_COLORS))
    ax.bar_label(bars, labels=[f"{v:.1f}명 ({h}시)" for v, h in
                               zip(top["peak_avg"], top["peak_hour"])], padding=3)
    ax.set_xlabel("첨두 시간대 평균 하차 인원 (명/시간)")
    ax.set_title(f"혼잡 상위 {TOP_N}개 정류장")
    ax.set_xlim(0, top["peak_avg"].max() * 1.2)
    ax.spines[["top", "right"]].set_visible(False)
    return save(fig, "stop_congestion_top10.png")


def plot_heatmap(hourly, summary):
    fig, ax = plt.subplots(figsize=(10, 11))
    im = ax.imshow(hourly.to_numpy(), aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(hourly.columns)), hourly.columns)
    ax.set_yticks(range(len(hourly.index)), summary["stop_name"])
    ax.set_xlabel("시간대 (시)")
    ax.set_title("정류장 × 시간대 평균 하차 인원 (첨두 하차 많은 순)")
    fig.colorbar(im, ax=ax, label="명/시간", shrink=0.6)
    return save(fig, "stop_congestion_heatmap.png")


def plot_daytype(daytype):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for name, color in [("평일", "#c0392b"), ("주말", "#2e86c1")]:
        ax.plot(daytype.index, daytype[name], marker="o", color=color, label=name)
    ax.set_xticks(daytype.index)
    ax.set_xlabel("시간대 (시)")
    ax.set_ylabel("정류장 1곳당 평균 하차 인원 (명/시간)")
    ax.set_title("평일·주말 시간대별 하차 추이")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)
    return save(fig, "stop_congestion_daytype.png")


def plot_map(summary):
    fig, ax = plt.subplots(figsize=(8, 6))
    for grade, color in GRADE_COLORS.items():
        g = summary[summary["grade"] == grade]
        ax.scatter(g["lon"], g["lat"], s=g["peak_avg"] * 6, color=color,
                   alpha=0.7, edgecolor="white", label=f"{grade} ({len(g)}곳)")
    for _, r in summary.head(TOP_N).iterrows():
        ax.annotate(r["stop_name"].replace("가상정류장", ""), (r["lon"], r["lat"]),
                    ha="center", va="center", fontsize=8, color="white")
    ax.set_xlabel("경도")
    ax.set_ylabel("위도")
    ax.set_title(f"정류장 위치별 혼잡도 (원 크기 = 첨두 하차 인원, 숫자 = 상위 {TOP_N}개 정류장 번호)")
    ax.legend(frameon=False, markerscale=0.6, loc="center left", bbox_to_anchor=(1, 0.5))
    ax.spines[["top", "right"]].set_visible(False)
    return save(fig, "stop_congestion_map.png")


def save(fig, name):
    FIG_DIR.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / name, dpi=150)
    plt.close(fig)
    return f"fig/{name}"


def md_table(df):
    lines = ["| " + " | ".join(df.columns) + " |",
             "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |"
              for row in df.itertuples(index=False)]
    return "\n".join(lines)


def write_report(summary, daytype, alighting, figs, n_unused):
    dates = alighting["date"]
    top = summary.head(TOP_N).reset_index()
    top_tbl = pd.DataFrame({
        "순위": range(1, len(top) + 1),
        "정류장": top["stop_name"],
        "등급": top["grade"],
        "첨두 시간대": top["peak_hour"].astype(str) + "시",
        "첨두 하차(명/시간)": top["peak_avg"].round(1),
        "일평균 하차(명)": top["daily_avg"].round(0).astype(int),
        "경유 노선 수": top["n_routes"],
    })

    grade = summary.groupby("grade").agg(
        n=("peak_avg", "size"), lo=("peak_avg", "min"), hi=("peak_avg", "max"),
        daily=("daily_avg", "mean"), routes=("n_routes", "mean"),
    ).loc[list(GRADE_COLORS)]
    grade_tbl = pd.DataFrame({
        "등급": grade.index,
        "정류장 수": grade["n"],
        "첨두 하차 범위(명/시간)": grade["lo"].round(1).astype(str) + " ~ " + grade["hi"].round(1).astype(str),
        "평균 일 하차(명)": grade["daily"].round(0).astype(int),
        "평균 경유 노선 수": grade["routes"].round(1),
    })

    day_tbl = pd.DataFrame({
        "구분": ["평일", "주말"],
        "정류장 1곳당 일 하차(명)": [round(daytype[c].sum(), 1) for c in ["평일", "주말"]],
        "첨두 시간대": [f"{daytype[c].idxmax()}시" for c in ["평일", "주말"]],
        "첨두 하차(명/시간)": [round(daytype[c].max(), 1) for c in ["평일", "주말"]],
    })

    md = f"""# 정류장 혼잡도 리포트

`viz_stop_congestion.py`가 생성한 문서. 직접 고치지 말고 스크립트를 다시 실행한다.

## 기준

- 기간: {dates.min():%Y-%m-%d} ~ {dates.max():%Y-%m-%d} ({dates.nunique()}일), {alighting['hour'].min()}~{alighting['hour'].max()}시
- 대상: 하차 기록이 있는 정류장 {len(summary)}곳 (노선이 지나지 않는 정류장 {n_unused}곳 제외)
- 혼잡도: 정류장의 시간당 평균 하차 인원. 여러 노선이 지나는 정류장은 노선을 합산
- 등급: 첨두 시간대 하차 인원 기준 상위 20% 혼잡, 하위 20% 여유, 나머지 보통
- 한계: 승차 인원·차량 정원 데이터가 없어 하차 인원을 혼잡도의 대리 지표로 사용

## 혼잡 상위 {TOP_N}개 정류장

![혼잡 상위 정류장]({figs['top']})

{md_table(top_tbl)}

## 등급별 정류장

{md_table(grade_tbl)}

## 정류장 × 시간대

![정류장 시간대 히트맵]({figs['heatmap']})

## 평일·주말 비교

![평일 주말 추이]({figs['daytype']})

{md_table(day_tbl)}

## 정류장 위치

![정류장 위치별 혼잡도]({figs['map']})
"""
    OUT_MD.write_text(md, encoding="utf-8")


def main():
    _, route_stops, stops, alighting = load_data()
    hourly, summary = build_metrics(route_stops, stops, alighting)
    daytype = build_daytype(alighting, len(summary))

    # 검증: 정류장별 합계의 총합 = 전체 하차 합계
    n_days = alighting["date"].nunique()
    total = alighting["alight_count"].sum()
    assert round(summary["daily_avg"].sum() * n_days) == total, "정류장 합계가 전체 합계와 다름"

    figs = {
        "top": plot_top(summary),
        "heatmap": plot_heatmap(hourly, summary),
        "daytype": plot_daytype(daytype),
        "map": plot_map(summary),
    }
    write_report(summary, daytype, alighting, figs, len(stops) - len(summary))

    print(f"정류장 {len(summary)}곳, 전체 하차 {total:,}명 (합계 검증 통과)")
    print(summary["grade"].value_counts().to_string())
    print(f"차트 {len(figs)}개 → {FIG_DIR}")
    print(f"리포트 → {OUT_MD}")


if __name__ == "__main__":
    main()
