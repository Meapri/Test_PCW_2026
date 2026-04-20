"""
시각화 모듈 (Step 5)

3개 분석 결과를 하나의 대시보드 이미지(dashboard.png)로 생성합니다.

레이아웃: 1행 3열 (가로 배치)
1. 이벤트 타입 파이 차트
2. 시간대별 트래픽/매출 이중축 그래프
3. 유저별 이벤트 TOP 10 수평 막대 그래프
"""

import os

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns


# seaborn 스타일 적용
sns.set_theme(style="whitegrid", font_scale=1.1)

# 파이 차트 색상
PIE_COLORS = ["#4CAF50", "#2196F3", "#FF5722"]


def create_dashboard(
    results: dict, output_path: str = "/app/output/dashboard.png"
):
    """
    분석 결과를 3개 차트로 구성된 대시보드 이미지로 저장합니다.

    Args:
        results: {분석명: DataFrame} 딕셔너리
        output_path: 저장 경로
    """
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle(
        "Event Log Pipeline — Dashboard",
        fontsize=16,
        fontweight="bold",
        y=1.02,
    )

    # ── Chart 1: 이벤트 타입별 발생 비율 (파이 차트) ──
    ax1 = axes[0]
    df_types = results["event_type_distribution"]
    ax1.pie(
        df_types["count"],
        labels=df_types["event_type"],
        autopct="%1.1f%%",
        colors=PIE_COLORS[: len(df_types)],
        startangle=90,
        textprops={"fontsize": 11},
    )
    ax1.set_title("Event Type Distribution", fontsize=13, fontweight="bold")

    # ── Chart 2: 시간대별 트래픽 & 매출 (이중축 꺾은선) ──
    ax2 = axes[1]
    df_hourly = results["hourly_traffic_and_revenue"]

    color_events = "#2196F3"
    color_revenue = "#FF9800"

    ax2.plot(
        df_hourly["hour"],
        df_hourly["event_count"],
        color=color_events,
        marker="o",
        markersize=3,
        linewidth=1.5,
        label="Event Count",
    )
    ax2.set_xlabel("Time (Hour)", fontsize=11)
    ax2.set_ylabel("Event Count", color=color_events, fontsize=11)
    ax2.tick_params(axis="y", labelcolor=color_events)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:00"))
    ax2.tick_params(axis="x", rotation=45)

    # 이중축: 매출
    ax2_twin = ax2.twinx()
    ax2_twin.fill_between(
        df_hourly["hour"],
        df_hourly["total_revenue"].astype(float),
        alpha=0.3,
        color=color_revenue,
        label="Revenue",
    )
    ax2_twin.set_ylabel("Revenue (KRW)", color=color_revenue, fontsize=11)
    ax2_twin.tick_params(axis="y", labelcolor=color_revenue)

    ax2.set_title(
        "Hourly Traffic & Revenue", fontsize=13, fontweight="bold"
    )

    # 범례 합치기
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    # ── Chart 3: 유저별 이벤트 TOP 10 (수평 막대) ──
    ax3 = axes[2]
    df_users = results["top_users_by_events"]
    df_users_sorted = df_users.sort_values("event_count", ascending=True)

    ax3.barh(
        df_users_sorted["user_id"].astype(str).apply(lambda x: f"User {x}"),
        df_users_sorted["event_count"],
        color=sns.color_palette("viridis", len(df_users_sorted)),
    )
    ax3.set_xlabel("Event Count", fontsize=11)
    ax3.set_title("Top 10 Users by Events", fontsize=13, fontweight="bold")

    # ── 저장 ──
    plt.tight_layout()

    # 출력 디렉토리 생성 (컨테이너 내부)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"🎨 대시보드 저장 완료: {output_path}")
