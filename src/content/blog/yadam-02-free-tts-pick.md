---
title: '야담 낭독 채널을 코드로 만든 3주 2: 무료 TTS 8개를 듣고 하나를 고르다'
description: 한 시간짜리 옛날이야기 낭독에 쓸 목소리를 무료 TTS 8개 중에서 골랐다. Supertonic 3 F5를 고른 이유와, 문장
  사이 쉼을 TTS에 맡기지 않고 코드로 넣은 방법.
pubDate: '2026-11-26'
tags:
- TTS 비교
- Supertonic
- Qwen3 TTS
- 한국어 TTS
- 오디오북 TTS
- 낭독 TTS
- 문장 쉼
- AI 낭독
heroImage: ./yadam-02-free-tts-pick/yadam-02-cover.jpg
---

> 지난 회: 60~80대가 틀어 두고 듣는 옛날이야기 낭독 채널을 코드로 만들기로 했다. 한 편이 한 시간 안팎이고, 다음 편 예고 없이 한 편으로 끝난다.

## 당시 상태

2026년 11월 7일, 대본은 있고 목소리는 없었다. 한 편이 한 시간이 넘으니 사람이 녹음할 수는 없다. 그래서 무료로 쓸 수 있는 TTS부터 들어 보기로 했다.

원하는 목소리는 분명했다. 시니어 시청자가 한 시간 동안 듣기 편한, 중년 여성 아나운서처럼 안정된 톤이다.

## 8개를 같은 글로 들어 보기

후보는 8개였다. Supertonic 3의 목소리 F1~F5 다섯 개와, 목소리를 글로 설명해서 만드는 Qwen3 VoiceDesign 세 가지다. 같은 대본 문단으로 파일을 만들어 하나씩 들었다. Supertonic은 속도를 0.9로 맞췄다.

결과는 생각보다 단순했다. F5 말고는 쓸 수 있는 게 없었다. Supertonic의 다른 목소리들은 톤이 목표와 맞지 않았다. Qwen3 VoiceDesign은 설명대로 그럴듯한 목소리를 만들었지만 두 가지가 걸렸다. "씨"를 약하게 발음했고, 문단마다 음색이 조금씩 바뀌었다. 한 시간 동안 같은 사람이 읽어 줘야 하는 낭독에서 음색이 흔들리는 건 치명적이다.

그때 만든 파일에서 앞 10초씩만 잘라 올린다. 같은 대본 첫머리다. 위가 고른 F5, 아래가 Qwen3 VoiceDesign에 "60대 초반 한국 여성 낭독가"라고 설명해서 만든 목소리다.

<figure class="audio"><audio controls preload="none" src="/audio/yadam-02-free-tts-pick/tts-10s-s-F5.mp3"></audio><figcaption>Supertonic 3 F5 (채택)</figcaption></figure>

<figure class="audio"><audio controls preload="none" src="/audio/yadam-02-free-tts-pick/tts-10s-q2-storyteller60.mp3"></audio><figcaption>Qwen3 VoiceDesign: "60대 초반 한국 여성 낭독가"</figcaption></figure>

## 막힌 것: 쉼

F5로 정하고 나니 다른 문제가 보였다. 문장과 문장 사이가 빡빡했다. 시니어 시청자용으로는 문장 사이를 더 띄워서 여유 있게 읽어 주는 편이 좋다.

TTS에 긴 문단을 통째로 넣으면 쉼의 길이는 모델이 정한다. 이걸 내 쪽에서 조절하려고, 문장을 하나씩 따로 합성하고 그 사이에 무음을 직접 붙이는 방식으로 바꿨다. 문장 사이, 문단 사이, 대사 앞뒤에 넣는 무음 길이를 코드 상수로 둔 것이다.

```python
for s in re.findall(r'"[^"]*"|[^.?!"]+[.?!]?', p):
    q = s.startswith('"')
    wav, _ = tts.synthesize(s.strip(), voice_style=style, lang="ko", speed=speed, total_steps=10)
    out += [sil(quote) if q else sil(0), np.asarray(wav, dtype=np.float32).reshape(-1), sil(sent + (quote if q else 0))]
out.append(sil(para - sent))
```

대사(따옴표로 시작하는 문장)는 앞뒤로 조금 더 쉰다.

처음 20초의 파형을 나란히 놓으면 차이가 보인다. 아래쪽이 문장마다 합성하고 쉼을 코드로 넣은 판이다. 문장 사이 빈칸이 고르게 길어졌다.

![문단을 통째로 합성한 F5와, 문장마다 합성하고 쉼을 코드로 넣은 F5의 처음 20초 파형](<./yadam-02-free-tts-pick/tts-pause-wave.png>)

## 숫자

쉼 길이는 후보를 몇 개 만들어 비교했고, 시니어 대상 낭독 채널의 영상을 받아쓰기로 재서 그 채널의 문장 끝 쉼에 맞췄다. 최종 설정은 이렇다.

| 항목 | 값 |
| --- | --- |
| 목소리 | Supertonic 3 F5 |
| 속도 | 0.9 |
| 문장 사이 쉼 | 0.6초 |
| 문단 사이 쉼 | 1.2초 |
| 대사 앞뒤 추가 쉼 | 0.25초 |

쉼 후보 가운데 쉼이 짧은 판과 최종 설정을 앞 10초씩 비교해 들을 수 있다.

<figure class="audio"><audio controls preload="none" src="/audio/yadam-02-free-tts-pick/tts-10s-f5-a.mp3"></audio><figcaption>쉼이 짧은 후보 (문장 사이 0.5초)</figcaption></figure>

<figure class="audio"><audio controls preload="none" src="/audio/yadam-02-free-tts-pick/tts-10s-f5-final.mp3"></audio><figcaption>최종 (문장 사이 0.6초, 문단 사이 1.2초, 대사 앞뒤 +0.25초)</figcaption></figure>

## 지금 보니

F5로 2주 넘게 영상을 만들었다. 그러다 11월 22일, 가족 시청자(70대)에게서 "나레이션 감정이 약하고 평탄하다"는 말을 들었다. 목소리는 그 뒤 설명으로 설계한 비공개 목소리(Fish Audio drama3)로 바뀌고, 다음 날에는 다시 로컬 모델로 옮겨 간다. 그 이야기는 10회와 11회에 쓴다.

다음 회는 그림이다. 남녀노소의 화풍을 맞추려고 그림마다 기준판을 붙인 이야기다. 그림 서비스를 브라우저 자동화로 부른 방법은 [이 글](/blog/muse-image-pipeline-ego-lite/)에 먼저 적었다.
