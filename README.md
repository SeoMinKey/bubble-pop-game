---
# Bubble Pop Game

Python pygame 기반의 버블 슈터

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5.2-green.svg)

---

## 빠른 시작 방법

```bash
git clone https://github.com/gzntzz/bubble-pop-game.git
cd bubble-pop-game
pip install -r requirements.txt
python main.py
```

**조작법**: `← →` 각도 조절 | `Space` 발사

---

## 주요 기능

![시작 스크린샷](assets/screenshot.png)
- 육각형 격자 체계, 벽 반사
- DFS 기반 같은 색깔 버블 제거 (3개 이상)
- 4발마다 벽 하강 난이도 조절
- 3단계 스테이지 구성

---

## 팀 구성 및 역할

**개발** 
- gzntzz (리포지토리 구축, 메인 개발 및 설계)

**기획**  
- 민기 (PM, 프로젝트 진행)
- 준호 (발표 자료, UI 피드백)

**디자인**  
- 예린 (UI, UX 디자인)
- 민기 (UI 레이아웃)

자세한 기여 내역은 [CONTRIBUTORS.md](CONTRIBUTORS.md)를 참고하세요.

---

## 프로젝트 구조

```
bubble-pop-game/  
├── src/  
│   ├── main.py         # 실제 구현 코드
│   └── skeleton.py     # 초기 설계도
├── assets/  
│   ├── images/         # 이미지 파일  
│   └── sounds/         # 사운드 파일 (예정)  
└── docs/               # 문서 (예정)
```

---

**MIT License** | Made by **Team 언빌리버블**
