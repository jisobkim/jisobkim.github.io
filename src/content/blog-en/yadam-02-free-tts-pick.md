---
title: 'Picking one of 8 free TTS voices: the narration voice and pauses between sentences'
description: I picked a voice for hour-long Korean folk tale narration from 8 free
  TTS options. Why I chose Supertonic 3 F5, and how I added pauses between sentences
  in code.
pubDate: '2026-11-26'
tags:
- TTS comparison
- Supertonic
- Qwen3 TTS
- Korean TTS
- audiobook TTS
- narration TTS
- sentence pauses
- AI narration
heroImage: ../blog/yadam-02-free-tts-pick/yadam-02-cover-en.jpg
---

> I am building, in code, a channel that narrates old Korean folk tales (yadam) for listeners in their 60s to 80s who leave it playing in the background. Each episode runs about an hour and ends on its own, with no teaser for the next one.

## Where things stood

On November 7, 2026, I had scripts but no voice. An episode runs over an hour, so recording it by hand was not an option. I decided to start by listening to free TTS engines.

I knew what voice I wanted. A steady tone like a middle-aged female announcer, easy for senior viewers to listen to for an hour.

## Listening to 8 voices on the same text

There were 8 candidates. Five Supertonic 3 voices, F1 to F5, and three Qwen3 VoiceDesign voices, which you create by describing the voice in text. I generated files from the same script paragraph and listened to them one by one. I set Supertonic's speed to 0.9.

The result was simpler than I expected. Nothing except F5 was usable. The other Supertonic voices did not match the target tone. Qwen3 VoiceDesign made voices that fit the description, but two things bothered me. It pronounced "씨" (ssi, a Korean syllable) weakly, and the timbre shifted a little from paragraph to paragraph. In narration where the same person has to read for an hour, a wavering timbre is fatal.

Here are the first 10 seconds of the files I made then. Both are Korean narration of the same opening lines. The first is F5, the one I picked. The second is a Qwen3 VoiceDesign voice made from the description "Korean female storyteller in her early 60s".

<figure class="audio"><audio controls preload="none" src="/audio/yadam-02-free-tts-pick/tts-10s-s-F5.mp3"></audio><figcaption>Supertonic 3 F5 (chosen)</figcaption></figure>

<figure class="audio"><audio controls preload="none" src="/audio/yadam-02-free-tts-pick/tts-10s-q2-storyteller60.mp3"></audio><figcaption>Qwen3 VoiceDesign: "Korean female storyteller in her early 60s"</figcaption></figure>

## What got in the way: pauses

Once I settled on F5, another problem showed up. The gaps between sentences were tight. For senior viewers, it is better to leave more space between sentences and read at a relaxed pace.

If you feed a long paragraph to TTS in one go, the model decides how long the pauses are. To control this myself, I switched to synthesizing each sentence separately and inserting silence between them. The silence lengths between sentences, between paragraphs, and around dialogue became constants in the code.

```python
for s in re.findall(r'"[^"]*"|[^.?!"]+[.?!]?', p):
    q = s.startswith('"')
    wav, _ = tts.synthesize(s.strip(), voice_style=style, lang="ko", speed=speed, total_steps=10)
    out += [sil(quote) if q else sil(0), np.asarray(wav, dtype=np.float32).reshape(-1), sil(sent + (quote if q else 0))]
out.append(sil(para - sent))
```

Dialogue (sentences starting with a quotation mark) gets a little extra pause before and after.

Putting the waveforms of the first 20 seconds side by side shows the difference. The bottom one is the version synthesized per sentence with pauses added in code. The gaps between sentences are longer and even.

![First 20 seconds of waveform: F5 synthesizing the whole paragraph at once, and F5 synthesizing per sentence with pauses added in code](<../blog/yadam-02-free-tts-pick/tts-pause-wave-en.png>)

## The numbers

I made several pause-length candidates and compared them. I also transcribed videos from a narration channel aimed at seniors, measured its pauses at the end of sentences, and matched them. The final settings are below.

| Item | Value |
| --- | --- |
| Voice | Supertonic 3 F5 |
| Speed | 0.9 |
| Pause between sentences | 0.6 s |
| Pause between paragraphs | 1.2 s |
| Extra pause around dialogue | 0.25 s |

You can compare the first 10 seconds of a short-pause candidate and the final settings.

<figure class="audio"><audio controls preload="none" src="/audio/yadam-02-free-tts-pick/tts-10s-f5-a.mp3"></audio><figcaption>Short-pause candidate (0.5 s between sentences)</figcaption></figure>

<figure class="audio"><audio controls preload="none" src="/audio/yadam-02-free-tts-pick/tts-10s-f5-final.mp3"></audio><figcaption>Final (0.6 s between sentences, 1.2 s between paragraphs, +0.25 s around dialogue)</figcaption></figure>

## Looking back

I made videos with F5 for over two weeks. Then on November 22, a family member who watches the channel (in their 70s) told me the narration "lacks emotion and sounds flat." After that, the voice changed to a private voice designed from a text description (Fish Audio drama3), and the next day it moved again to a local model. I will cover that in a separate post about the voice.

I wrote about how I called the image service through browser automation in [this post](/en/blog/muse-image-pipeline-ego-lite/).
