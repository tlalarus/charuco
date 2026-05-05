# ChArUco Board Image Augmentation

이 디렉토리는 ChArUco 보드 이미지의 데이터 증강(augmentation) 방법 및 구현을 기록합니다.

## 목적

카메라 캘리브레이션에 사용되는 ChArUco 보드 이미지의 질을 개선하고 다양한 환경에서의 성능 평가를 위해 다음과 같은 요소들을 다룹니다:

- **기하학적 변환**: 회전, 스케일링, 원근 변환 등
- **속성 변경**: 밝기, 대비, 포화도 조정
- **노이즈 추가**: 가우시안 노이즈, 소금-후추 노이즈 등
- **블러 효과**: 모션 블러, 가우시안 블러 등
- **조명 변화**: 섀도우, 글레어 시뮬레이션

## 구조

```
augmentation/
├── README.md                    # 이 파일
├── notebooks/                   # 증강 방법 실험용 노트북
│   └── augmentation_experiments.ipynb
├── scripts/                     # 증강 함수 및 유틸리티
│   └── augmentation_utils.py
└── results/                     # 증강 결과 저장
    └── augmented_samples/
```

## 사용 방법

(추후 추가 예정)

## 참고 자료

- OpenCV Documentation
- Albumentations Library
- ChArUco Calibration Best Practices
