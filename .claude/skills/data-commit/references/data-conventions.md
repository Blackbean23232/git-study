# 데이터 분석 조직 커밋 컨벤션 상세

SKILL.md의 타입 표만으로 분류가 애매할 때 읽는 보충 자료.

## 컨벤션 근거

- 기반: [Conventional Commits 1.0.0](https://www.conventionalcommits.org/ko/v1.0.0/) — `type(scope): description` 구조, `!`/`BREAKING CHANGE` 푸터, 본문·푸터 규칙을 그대로 따른다. 표준 타입(feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert)은 유지한다.
- 분석 특화: 표준에는 "데이터가 바뀌었다", "분석/시각화 산출물이 바뀌었다"를 표현할 타입이 없다. 분석 조직에서는 코드보다 데이터·산출물 변경이 훨씬 많고 그 추적이 재현성의 핵심이므로 `data`, `analysis`, `viz`, `pipeline`, `model`을 추가했다.
- 표준의 SemVer 연동(`feat`=MINOR, `fix`=PATCH)은 분석 저장소에선 의미가 약하다. 대신 **"산출물 수치가 바뀌는가"** 를 `feat`/`fix` vs `refactor`/`perf`의 기준으로 삼는다.

## 타입 판별 규칙 (애매할 때)

| 상황 | 선택 | 이유 |
|---|---|---|
| 더미 데이터 생성 스크립트 + 생성된 데이터 | `data` | 목적이 데이터 확보. 스크립트는 데이터의 출처이므로 같이 묶음 |
| 새 분석 스크립트 + 그 결과 md/그림 | `feat` (결과가 그림 위주면 `viz`) | 산출물은 생성 코드와 함께 |
| 기존 분석 코드의 필터/집계 조건 변경 | `fix` (오류 정정) / `feat` (새 기준 추가) | 수치가 바뀜 |
| 함수 분리·변수명 정리, 수치 동일 | `refactor` | 결과 불변을 본문에 명시 |
| 차트 색상·라벨·레이아웃만 수정 | `viz` | 분석 결과 불변 |
| 노트북에 셀 추가해 탐색 | `analysis` | EDA |
| 노트북 출력(output)만 변경 | 커밋 보류 권장 | 노이즈. 출력 제거 후 커밋 |
| 컬럼명 변경으로 하위 분석이 깨짐 | 해당 type + `!` | `BREAKING CHANGE:` 푸터에 영향 범위 |
| `.gitignore`, 린트 설정 | `chore` | |
| requirements/conda 환경 | `build` | |
| 데이터 사전, 컬럼 설명 | `docs` | |
| 데이터 검증 로직(결측·범위 체크) | `test` (자동화된 검증) / `pipeline` (파이프라인에 내장) | |

## 경로·확장자별 1차 분류

| 패턴 | 1차 후보 |
|---|---|
| `data/**`, `*.csv`, `*.xlsx`, `*.parquet`, `*.json`(데이터) | `data` |
| `*.ipynb` | `analysis` |
| `fig/**`, `*.png`, `*.svg`, `viz_*.py` | `viz` |
| `out_*.md`, `report*.md` | `analysis` (생성 코드와 함께면 그 코드의 type) |
| `make_*.py`, `etl/**`, `dags/**`, `*.sql`(적재) | `pipeline` |
| `models/**`, `features/**` | `model` |
| `tests/**` | `test` |
| `README.md`, `docs/**` | `docs` |
| `requirements*.txt`, `environment.yml`, `Dockerfile` | `build` |
| `.gitignore`, `.editorconfig`, `.claude/**` | `chore` |

1차 후보일 뿐이다. 실제 diff 내용이 우선한다 (예: `data/` 안의 설정 yaml은 `data`가 아니라 `chore`).

## scope 규칙

- 도메인 명사 소문자: `bus`, `alighting`, `routes`, `stops`, `hourly`, `trend`.
- 계층 이름도 허용: `etl`, `eda`, `dashboard`.
- 저장소 이력에서 이미 쓰인 scope를 우선 재사용한다 (`git log --format=%s`로 확인) — scope가 난립하면 필터링 가치가 사라진다.
- 3개 이상 도메인에 걸치면 scope를 생략한다.

## 본문에 쓰면 좋은 분석 맥락

분석 변경은 코드 diff만으로는 "왜"가 안 보인다. 다음 중 해당하는 것만 간결히 남긴다.

- 데이터 기준: 기간, 필터, 집계 단위, 결측·이상치 처리 방식
- 수치 영향: 변경 전후 핵심 지표 (예: "상위 10개 합계 8% 감소")
- 재현 정보: random seed, 데이터 버전/출처, 실행 명령
- 영향 범위: 이 변경에 의존하는 하위 산출물

## 하지 말 것

- `update`, `수정`, `작업중`, `WIP` 같은 정보 없는 제목
- 데이터 파일과 분석 코드를 한 커밋에 혼합
- 결과가 바뀌는 변경을 `refactor`로 표기
- 한 커밋에 서로 무관한 변경 묶기 ("여러 가지 수정")
- 대용량 원본·개인정보 데이터 커밋
