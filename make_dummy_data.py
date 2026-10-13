"""버스 노선/하차 더미 데이터를 xlsx로 생성한다."""
from pathlib import Path

import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).parent / "data"
OUT_DIR.mkdir(exist_ok=True)
rng = np.random.default_rng(42)

# ---- 정류장 마스터 (서울 시내 가상 좌표) ----
N_STOPS = 40
stops = pd.DataFrame({
    "stop_id": [f"S{i:03d}" for i in range(1, N_STOPS + 1)],
    "stop_name": [f"가상정류장{i:02d}" for i in range(1, N_STOPS + 1)],
    "lat": 37.45 + rng.uniform(0, 0.15, N_STOPS).round(6),
    "lon": 126.85 + rng.uniform(0, 0.25, N_STOPS).round(6),
})

# ---- 노선 마스터 ----
routes = pd.DataFrame({
    "route_id": ["R100", "R200", "R300", "R400", "R500"],
    "route_name": ["100번", "200번", "300번", "400번", "500번"],
    "route_type": ["간선", "간선", "지선", "지선", "광역"],
    "first_bus": ["05:00", "05:10", "05:30", "05:30", "05:00"],
    "last_bus": ["23:30", "23:00", "22:30", "22:30", "01:00"],
})

# ---- 노선별 정류장 순서 ----
rows = []
for rid in routes["route_id"]:
    n = int(rng.integers(12, 21))
    picked = rng.choice(stops["stop_id"], size=n, replace=False)
    for seq, sid in enumerate(picked, start=1):
        rows.append({"route_id": rid, "stop_seq": seq, "stop_id": sid})
route_stops = pd.DataFrame(rows)

# ---- 하차 데이터 (14일 x 시간대 x 노선정류장) ----
dates = pd.date_range("2026-09-01", periods=14, freq="D")
hours = list(range(5, 24))
peak = {7: 3.0, 8: 4.0, 9: 2.5, 17: 2.5, 18: 4.0, 19: 3.0}

alight = []
for d in dates:
    weekend = d.dayofweek >= 5
    for _, r in route_stops.iterrows():
        for h in hours:
            base = 6 if not weekend else 4
            lam = base * peak.get(h, 1.0)
            alight.append((d.date(), h, r["route_id"], r["stop_id"], int(rng.poisson(lam))))
alighting = pd.DataFrame(
    alight, columns=["date", "hour", "route_id", "stop_id", "alight_count"]
)

# ---- xlsx 저장 ----
with pd.ExcelWriter(OUT_DIR / "routes.xlsx") as w:
    routes.to_excel(w, sheet_name="routes", index=False)
    route_stops.to_excel(w, sheet_name="route_stops", index=False)
    stops.to_excel(w, sheet_name="stops", index=False)

alighting.to_excel(OUT_DIR / "alighting.xlsx", sheet_name="alighting", index=False)

print(f"routes.xlsx: routes={len(routes)}, route_stops={len(route_stops)}, stops={len(stops)}")
print(f"alighting.xlsx: {len(alighting)} rows")
