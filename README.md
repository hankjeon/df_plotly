# df_plotly

pandas DataFrame으로 저장된 값을 plotly로 바로 그려서 확인할 수 있는 Streamlit 앱.

`dt` 간격으로 기록된 시계열 DataFrame(`t, x, y, z, ...`)을 파일로 저장해두고, 매번 플롯 스크립트를 새로 짜지 않고 브라우저에서 컬럼을 골라가며 그래프를 확인하기 위한 범용 도구.

## 주요 기능

- CSV/Parquet 파일을 업로드하면 컬럼 목록을 보여준다.
- X축 컬럼 1개, Y축 컬럼 여러 개를 선택하면 즉시 그래프가 그려진다. X축은 보통 `t`(시간)나
  `x`(이동거리)를 쓰겠지만 어떤 컬럼이든 선택 가능(제약 없음).
- Y축을 여러 개 선택했을 때 두 가지 방식 지원:
  - **Overlay**: 한 그래프에 라인을 겹쳐서 표시
  - **Stacked**: X축을 공유하는 서브플롯으로 컬럼별로 나눠서 표시
- 업로드한 데이터 미리보기(상위 20행) 제공.

## 사용 라이브러리

- **Streamlit** - 파일 업로드, 컬럼 선택 UI, 앱 실행/서빙
- **pandas** - CSV/Parquet 로드
- **plotly** (`graph_objects`, `subplots`) - 그래프 렌더링
- **pyarrow** - Parquet 읽기/쓰기 (pandas의 Parquet 엔진)

## 데이터 파일 포맷: CSV vs Parquet

둘 다 지원하지만 상황에 따라 골라 쓰면 된다.

| | CSV | Parquet |
|---|---|---|
| 사람이 직접 열어보기 | 가능 (텍스트) | 불가 (바이너리) |
| 파일 크기 | 큼 | 작음 (컬럼형 압축) |
| dtype 보존 | 안 됨 (다시 읽을 때 추론) | 보존됨 |
| 로드 속도 | 느림 (대용량일수록) | 빠름 |
| 저장 방법 | `df.to_csv("run.csv", index=False)` | `df.to_parquet("run.parquet")` |

**권장**: 시뮬레이션 결과처럼 스텝 수가 많은(dt별 기록) 시계열은 **Parquet**을 기본으로 쓴다.
용량이 작고 float 정밀도·dtype이 그대로 보존되어 재현성이 좋다. CSV는 결과를 잠깐 눈으로
확인하거나 다른 툴(엑셀 등)과 주고받을 때만 쓴다.

저장할 때 예:

```python

df = to_dataframe(result)
df.to_parquet("run.parquet")   # 권장
# df.to_csv("run.csv", index=False)  # 필요할 때만
```

## 실행

```bash
streamlit run app.py
```

브라우저가 열리면 CSV/Parquet 파일을 업로드하고 X/Y축을 선택한다.

## 그래프 텍스트 언어 규칙

코드 주석은 한국어, 그래프에 렌더링되는 문자열(제목·축 이름·범례·hover 텍스트 등)은 영어로 쓴다
(m270_rocket 프로젝트 컨벤션과 동일하게 맞춤).
