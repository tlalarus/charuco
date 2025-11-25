# charuco
ChArUco 보드를 이용한 캘리브레이션 예제 연습

## poetry

## Chessboard Calibration Image Metrics & Scoring

본 문서는 체스보드 기반 카메라 캘리브레이션에서  
**1장의 이미지에 대해 계산하는 기하학적 품질 지표와 스코어링 함수**를 정의한다.

---

## 1. 입력 정의

- `corners2d` : 체스보드 코너 2D 좌표 (N × 2, row-major)
- `rows, cols` : 체스보드 내부 코너 행/열 개수
- `resolution = (W, H)` : 이미지 해상도 (pixel)

모든 좌표는 가능하면 **왜곡 보정된 이미지** 기준으로 사용하는 것을 권장한다.

---

## 2. 단일 이미지 지표 정의

### 2.1 Grid Coverage

**목적**: 보드가 이미지 전역에 골고루 분포하는지 평가.

1. 이미지 전체를 `g × g` 그리드로 분할 (기본 `g = 3`, 즉 3×3).
2. `corners2d`에 대한 **convex hull** P를 계산.
3. 각 셀 C_i 에 대해 교집합 면적 비율:
   - `coverage_i = area(P ∩ C_i) / area(C_i)`
4. 출력:
   - `coverage_per_cell[i] ∈ [0, 1]`
   - `max_cell, max_ratio` (가장 많이 덮은 셀과 비율)

---

### 2.2 Corner Count

**목적**: 코너 검출의 신뢰성과 패턴 시야 범위를 확인.

- `count = len(corners2d)`

예상 코너 수 `rows * cols` 대비 비율로도 사용 가능.

---

### 2.3 Global Coverage Ratio

**목적**: 보드가 이미지에서 차지하는 전체 비율(스케일)을 평가.

1. `P = convex_hull(corners2d)`
2. `coverage = area(P) / (W * H)`

- `coverage`가 작으면 보드가 너무 작게 찍힌 샷.

---

### 2.4 Spacing Ratios (Tilt / Pan)

**아이디어**: 기울어질수록 가까운 쪽과 먼 쪽의 코너 간 간격 차이가 커짐.

#### 2.4.1 Vertical Tilt (세로 틸트)

행 r 에서 세로 간격 평균:

- `d_v(r) = mean_c || p_{r+1,c} - p_{r,c} ||`

상단 행 vs 하단 행 비교:

- `S_tilt_raw = min(d_v(0), d_v(rows-2)) / max(d_v(0), d_v(rows-2))`

- `S_tilt_raw ≈ 1.0` : 거의 정면
- `S_tilt_raw` 작을수록 강한 위/아래 틸트

#### 2.4.2 Horizontal Pan (가로 팬)

열 c 에서 가로 간격 평균:

- `d_h(c) = mean_r || p_{r,c+1} - p_{r,c} ||`

좌열 vs 우열 비교:

- `S_pan_raw = min(d_h(0), d_h(cols-2)) / max(d_h(0), d_h(cols-2))`

- `S_pan_raw ≈ 1.0` : 좌우 기울기 거의 없음
- `S_pan_raw` 작을수록 좌/우 팬이 강함

---

### 2.5 Roll Angle (격자선 방향)

**목적**: 카메라 z축 회전(roll) 정도를 평가.

가로 격자선 벡터:

- `h_{r,c} = p_{r,c+1} - p_{r,c}`

각도(rad):

- `theta_{r,c} = atan2( h_{r,c}.y, h_{r,c}.x )`

모든 `theta_{r,c}`를 모아 **원형 평균**을 취해 roll(rad)을 얻고,  
`roll_deg = roll * 180 / π` 로 변환하여 사용.

---

## 3. 스코어링 함수 설계 (예시)

각 지표를 [0, 1] 범위의 스코어로 변환:

- `S_grid ∈ [0,1]`  (Grid coverage)
- `S_cov  ∈ [0,1]`  (Global coverage)
- `S_cnt  ∈ [0,1]`  (Corner count)
- `S_tilt ∈ [0,1]`  (Vertical tilt strength)
- `S_pan  ∈ [0,1]`  (Horizontal pan strength)
- `S_roll ∈ [0,1]`  (Roll quality)

### 3.1 Grid Coverage Score

파라미터:

- `target_cell_ratio = 0.2`

정의:

- `S_grid = average_i( clamp( coverage_i / target_cell_ratio, 0, 1 ) )`

각 셀에서 20% 이상 덮으면 1점,  
그보다 적으면 비례해서 점수.

---

### 3.2 Global Coverage Score

파라미터 예시:

- `cov_min  = 0.2`
- `cov_best = 0.5`

정의:

- `S_cov = clamp( (coverage - cov_min) / (cov_best - cov_min), 0, 1 )`

---

### 3.3 Corner Count Score

- `expected_corners = rows * cols`
- `S_cnt = clamp( len(corners2d) / expected_corners, 0, 1 )`

---

### 3.4 Tilt / Pan Strength Score

raw 비율:

- `S_tilt_raw, S_pan_raw ∈ (0, 1]`

파라미터 예시 (강한 틸트를 선호하는 경우):

- `target_ratio = 0.7`
- `min_ratio    = 0.4`

정의:

- `S_tilt = clamp( (target_ratio - S_tilt_raw) / (target_ratio - min_ratio), 0, 1 )`
- `S_pan  = clamp( (target_ratio - S_pan_raw)  / (target_ratio - min_ratio), 0, 1 )`

---

### 3.5 Roll Score

파라미터:

- `roll_clip = 60` degrees

정의:

- `S_roll = 1 - min( abs(roll_deg), roll_clip ) / roll_clip`

---

### 3.6 최종 이미지 스코어

가중치 예시 (합 = 1):

- `w_grid = 0.20`
- `w_cov  = 0.20`
- `w_cnt  = 0.10`
- `w_tilt = 0.20`
- `w_pan  = 0.10`
- `w_roll = 0.20`

최종 스코어:

```text
S_total = w_grid*S_grid + w_cov*S_cov + w_cnt*S_cnt
        + w_tilt*S_tilt + w_pan*S_pan + w_roll*S_roll
