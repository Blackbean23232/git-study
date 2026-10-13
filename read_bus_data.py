"""노선/하차 xlsx를 pandas로 읽어 병합하고 간단히 집계한다."""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def load_data():
    # 시트 이름을 주면 DataFrame, sheet_name=None이면 {시트명: DataFrame} 딕셔너리
    sheets = pd.read_excel(DATA_DIR / "routes.xlsx", sheet_name=None)
    routes = sheets["routes"]
    route_stops = sheets["route_stops"]
    stops = sheets["stops"]

    alighting = pd.read_excel(
        DATA_DIR / "alighting.xlsx",
        sheet_name="alighting",
        parse_dates=["date"],
    )
    return routes, route_stops, stops, alighting


def main():
    routes, route_stops, stops, alighting = load_data()

    for name, df in [("routes", routes), ("route_stops", route_stops),
                     ("stops", stops), ("alighting", alighting)]:
        print(f"\n[{name}] shape={df.shape}")
        print(df.head(3).to_string(index=False))

    # 하차 + 노선명 + 정류장명 + 정류장 순서 병합
    merged = (
        alighting
        .merge(routes[["route_id", "route_name", "route_type"]], on="route_id", how="left")
        .merge(stops[["stop_id", "stop_name"]], on="stop_id", how="left")
        .merge(route_stops, on=["route_id", "stop_id"], how="left")
    )

    print("\n[노선별 총 하차 인원]")
    print(merged.groupby("route_name")["alight_count"].sum().sort_values(ascending=False))

    print("\n[시간대별 평균 하차 인원 TOP 5]")
    print(merged.groupby("hour")["alight_count"].mean().nlargest(5).round(2))

    print("\n[하차 많은 정류장 TOP 5]")
    print(merged.groupby("stop_name")["alight_count"].sum().nlargest(5))


if __name__ == "__main__":
    main()
