---
title: 'Gemini 무료판으로 데스크톱 펫에 모션 12개 넣기: 3x2 격자를 편집시키는 프롬프트'
description: Claude Code 상태에 따라 움직이는 데스크톱 펫(Clawd on Desk)에 Gemini 무료판으로 새 모션 12개를
  만들어 넣었다. 그림을 새로 그리게 하지 않고 3x2 격자를 편집시킨 프롬프트, 실패한 시도, 배경 제거 함정까지.
pubDate: '2026-11-28'
tags:
- Clawd on Desk
- 데스크톱 펫
- Claude Code 펫
- Gemini 이미지 편집
- 스프라이트 애니메이션
- APNG
- AI 픽셀아트
- Gemini 프롬프트
heroImage: ./alfred-desktop-pet-gemini-motions/alfred-cover.jpg
---

화면 구석에 집사 한 명이 서 있다. Claude Code가 생각을 시작하면 콧수염을 쓰다듬고, 도구를 돌리면 은수저를 닦고, 권한을 물어야 하면 종을 흔든다. 오류가 나면 찻잔을 떨어뜨린다. 10월 1일에 이 모션 12개를 Gemini 무료판으로 만들어 넣었다. 그날 쓴 프롬프트와 실패한 시도를 정리한다.

![새로 넣은 모션 12개. 왼쪽 위부터 차 따르기, 생각, 수저 닦기, 종, 완료 인사, 찻잔 사고, 먼지떨이, 하품, 졸기, 쓰러짐, 잠, 깨기](<./alfred-desktop-pet-gemini-motions/alfred-motions.gif>)

## 펫과 그림의 출처

펫 앱은 [Clawd on Desk](https://github.com/rullerzhou-afk/clawd-on-desk)다. `brew install --cask clawd-on-desk`로 설치하면 Claude Code에 훅을 걸고, 세션 상태(생각 중, 도구 실행 중, 알림, 오류 등)에 맞춰 화면의 펫 그림을 바꾼다.

펫 그림은 [pablomanjarres/Alfred](https://github.com/pablomanjarres/Alfred)의 에셋을 MIT 라이선스로 받아 썼다. Codex Pet 형식의 스프라이트 한 장(1536x1872, 8열 9행, 칸당 192x208)이다. 원래 들어 있던 동작은 서 있기, 달리기, 손 흔들기 같은 기본 동작뿐이었다.

계기는 [게임 캐릭터 이동 모션을 AI 이미지 도구로 만드는 영상](https://youtu.be/Ricxy_CHZig)이었다. 디테일 편집은 Gemini가 낫다는 말을 보고, 알프레드에도 모션을 늘려 보기로 했다.

## 빈 칸을 채울 수 없던 이유

스프라이트는 72칸 중 57칸만 차 있다. 처음엔 빈 15칸에 그림을 채우면 될 줄 알았다. 그런데 Clawd가 Codex Pet을 자기 테마로 바꾸는 어댑터(`codex-pet-adapter.js`)가 행마다 프레임 수와 시간을 코드에 박아 두고 있었다(idle 6, waving 4, jumping 5 등). 빈 칸에 그림을 넣어도 재생되지 않는다.

그래서 테마를 포크했다. 어댑터가 만든 `codex-pet-alfred` 테마를 복사하고, 어댑터 표시 파일(`.clawd-codex-pet.json`)과 `source` 항목을 떼면 어댑터가 다시 덮어쓰지 않는다. Clawd 자체 테마는 상태마다 APNG를 받고 프레임 수에 제약이 없다.

새 포즈는 외부 도구가 그려야 했다. Claude는 있는 프레임을 다시 조합하는 일은 해도 주전자나 먼지떨이 같은 새 물건을 그리지는 못한다. Gemini 웹 무료판(Flash)을 썼고, 하루에 이미지 요청이 16건쯤 나갔는데 제한 메시지는 없었다.

## 그리게 하지 말고 편집시킨다

처음엔 기준 프레임 1장을 올리고 "같은 캐릭터로 6프레임 스프라이트 시트를 가로 한 줄로 그려라"라고 시켰다. 캐릭터는 유지됐지만 세로형 그림에 크기가 제각각인 6명이 나왔다. 출력 비율이 입력 그림 비율을 따라간다. 프롬프트 없이 그림만 올렸더니 아래 세 칸에 왕관을 씌웠다.

방향을 바꿨다. 같은 포즈 6개를 3x2로 깐 그림을 내가 먼저 만들고, Gemini에는 "칸마다 숨긴 팔만 이렇게 바꿔라"라고 편집을 시켰다. 위치와 크기가 이미 정해져 있으니 Gemini는 바꿀 부위만 손댄다. 요청 1번에 모션 1개가 나온다.

![왼쪽은 내가 만든 입력 그림, 오른쪽은 Gemini가 편집한 차 따르기. 은발이 보라색으로 물들었고 오른쪽 아래 칸에 워터마크가 있다](<./alfred-desktop-pet-gemini-motions/alfred-grid-edit.jpg>)

입력 그림은 작은 스크립트(`clawd-pet-motion template`)로 만든다. 원본 첫 프레임을 세 배로 키워 마젠타(#FF00FF) 바탕에 6번 붙인다. 성공한 프롬프트는 모두 같은 뼈대였고, 영어로 썼다.

```text
Edit this image. It is a 3x2 grid containing the same butler six times
(reading order: top-left = 1, top-right = 3, bottom-left = 4, bottom-right = 6).
Turn it into a 6-frame animation of him pouring tea, changing ONLY the arm
that is currently behind his back and adding a small white teapot:
1 = ... 2 = ... 3 = ... 4 = ... 5 = ... 6 = unchanged.
Every butler must stay in exactly the same position, same size, same feet
placement as in the input. Do not move, rescale, merge or rearrange the figures.
Keep the same image dimensions and the flat magenta #FF00FF background.
No text, no letters, no numbers, no borders.
```

칸 번호와 읽는 순서를 적어야 칸마다 다른 동작을 시킬 수 있다. 6번 칸을 `unchanged`로 둔 것은 Gemini가 오른쪽 아래에 워터마크를 찍기 때문이다. 그 칸은 버리고 재생할 때 1번 칸으로 대신한다.

움직이는 팔은 뒤로 숨긴 팔로 정했다. 쟁반 든 손을 건드리면 쟁반이 사라졌다. 회중시계를 꺼내는 모션은 두 번 시켰는데 두 번 다 중간 4칸에서 쟁반과 찻잔이 없어졌다. 그 뒤로는 프롬프트 둘째 줄에 이 문장을 넣었다.

```text
In every one of the six figures, the hand holding the silver tray with the
teacup must stay exactly as it is in the input: same arm, same tray, same
teacup on the tray, untouched.
```

이 문장을 넣은 뒤로 은수저와 종은 여섯 칸 모두 쟁반이 남았다. 완료 인사는 손을 옆으로 펼치는 4번 칸에서만 쟁반이 빠져서 그 칸을 뺐다. 회중시계는 끝내 안 돼서 새 물건 없이 콧수염을 쓰다듬는 동작으로 바꿨다. 왜 회중시계만 안 됐는지는 확인하지 못했다.

## 배경을 빼고 APNG로 묶기

받은 그림(1216x878)은 `clawd-pet-motion frames`로 처리한다. 마젠타 배경을 지우고 192x208 칸 6개로 자른 뒤, 원하는 순서와 시간으로 APNG를 만든다.

```bash
clawd-pet-motion frames pour-tea.png alfred-pour-tea.apng \
  --seq 1,2,3,4,4,5,1 --ms 400,200,300,400,400,250,300
```

`--seq`는 칸 번호 재생 순서다. 6번 칸이 없고 4번 칸을 두 번 넣었다. 주전자를 기울인 채 잠깐 머무르게 하려는 것이다.

여기서 함정이 두 개 있었다. 첫째, 원본 스프라이트는 은발 하이라이트, 눈 흰자, 콧수염, 셔츠 단추 자리가 투명한 구멍이다(프레임당 1,531픽셀). 그대로 마젠타 위에 얹으면 그 구멍으로 마젠타가 비친다. 그래서 입력 그림을 만들 때 바깥에서 flood fill로 진짜 배경을 찾고, 안쪽 구멍은 흰색으로 메웠다.

둘째, 구멍을 메웠는데도 차 따르기 결과는 은발이 보라색으로 나왔다(위 그림 오른쪽). 배경색이 밝은 회색에 번진 것이다. 녹색 배경으로 바꿔 보기도 했지만 원인이 배경색이 아니라서 마젠타로 되돌렸다. 대신 `frames`에서 외곽선은 배경색 성분을 빼서 어둡게 하고, 안쪽 밝은 부분은 빠진 녹색 채널을 채워 회색으로 되돌린다.

```python
spill = (alpha > 0) & (m > 0)        # m = min(R, B) - G, 마젠타 기운
edge = spill & ((alpha < 1) | near)  # 배경과 맞닿은 외곽선
inner = spill & ~edge
r2, b2 = np.where(edge, r - m, r), np.where(edge, b - m, b)
g2 = np.where(inner, np.minimum(r, b), g)
```

## 테마에 등록

만든 APNG를 포크한 테마의 `assets/`에 넣고 `theme.json`에서 상태에 연결한다.

```json
"states": {
  "thinking": ["alfred-thinking.apng"],
  "working": ["alfred-polishing.apng"],
  "notification": ["alfred-bell.apng"],
  "attention": ["alfred-done.apng"],
  "error": ["alfred-mishap.apng"],
  "sweeping": ["alfred-dusting.apng"]
},
"idleAnimations": [{ "file": "alfred-pour-tea.apng", "duration": 2250 }],
"sleepSequence": { "mode": "full" }
```

차 따르기는 마우스를 20초 움직이지 않으면 한 번 나온다. 잠자기는 이미지 한 장(6칸)으로 하품, 졸기, 쓰러짐, 잠, 깨기 다섯 상태를 만들었다. 칸 조합만 다르게 묶었다. `sweeping`은 컨텍스트를 압축하는 동안 나오는 상태라 먼지떨이를 붙였다.

Clawd는 로컬 서버로 상태를 받는다. 이벤트를 직접 보내면 Claude Code를 돌리지 않아도 상태별 그림을 확인할 수 있다.

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"state":"error","session_id":"test","event":"StopFailure"}' \
  http://127.0.0.1:23333/state
```

![이벤트를 보내고 Clawd 창을 캡처한 모습. 알림, 작업 완료, 오류](<./alfred-desktop-pet-gemini-motions/alfred-states.jpg>)

## 기기마다 턱시도 색

같은 펫을 Mac Studio, MacBook Pro, MacBook Air 세 대에 쓴다. 지금 어느 기기 화면을 보는지 헷갈려서 턱시도 색을 기기마다 다르게 칠했다(`clawd-pet-tint`).

처음엔 찻잔만 칠하려 했다. 그런데 스프라이트에 색이 4,339개 쓰인 안티에일리어싱 그림이라, 찻잔의 흰색과 셔츠의 흰색을 나눌 방법이 없었다. 그래서 어둡고 무채색인 픽셀만 골랐다. 불투명(alpha > 0.3)이고 명도 0.36 미만, 채도 0.28 미만인 픽셀이다. 턱시도, 구두, 나비넥타이가 걸리고 은발, 피부, 셔츠, 찻잔은 밝아서 빠진다. 원본 명도를 새 범위로 늘려서 주름과 그림자는 남긴다.

![Mac Studio는 검정 원본, MacBook Pro는 회색, MacBook Air는 아이보리](<./alfred-desktop-pet-gemini-motions/alfred-tint.jpg>)

새 모션을 넣은 포크 테마도 같은 스크립트로 통째로 칠해 맥북 두 대에 rsync로 복사했다.

## 남은 것

Gemini가 다시 그린 프레임은 원본보다 부드럽고 대비가 낮다. 원래 대기 모션에서 새 모션으로 넘어갈 때 그림체가 살짝 바뀐다. 실제 크기(134px)에서는 크게 거슬리지 않아서 그대로 쓰고 있다.

달리기 모션은 원본 그대로다. 입력 그림이 서 있는 포즈라서 격자 편집으로는 다리를 움직이지 못했다. 달리기 행의 프레임으로 입력 그림을 따로 만들어야 한다.

웹 이미지 서비스를 브라우저 자동화로 파이프라인에 붙인 이야기는 [이 글](/blog/muse-image-pipeline-ego-lite/)에, 그림을 로컬 영상 모델로 움직인 이야기는 [이 글](/blog/wan22-mac-studio-mlx/)에 적었다.
