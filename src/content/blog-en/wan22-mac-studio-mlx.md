---
title: 'Running the Wan2.2 video model on a Mac Studio: from 42 minutes to 5'
description: I ran Wan2.2 TI2V-5B with mlx-video on a Mac Studio (M2 Max, 32GB). Turbo
  weights cut 42 minutes to 5. Two pitfalls and a jitter fix included.
pubDate: '2026-11-26'
tags:
- Wan2.2
- Wan2.2 TI2V-5B
- mlx-video
- Apple Silicon video generation
- Mac Studio M2 Max
- local image to video
- Wan2.2 Turbo
- METAL GPU Timeout
heroImage: ../blog/wan22-mac-studio-mlx/wan22-cover-en.jpg
---

> Part of my notes on building a Korean folk-tale (yadam) narration channel.

[The previous post](/en/blog/muse-image-pipeline-ego-lite/) was about hooking Muse into my video pipeline through browser automation. After that, I tried running the video model Wan2.2 locally. At first I planned to run it with ComfyUI on an RTX 3090. In the end I did it on the Mac Studio I already use (M2 Max, 32GB of memory). This is a record of tests from November 26, 2026.

I had one goal. If it could animate a single picture into a 10-second video within 10 to 20 minutes, I would use it. I needed it to make the short clip that opens each folk-tale narration video, as a stand-in when the external service hits its limit.

## Starting with the base model on mlx-video

The model is Wan2.2 TI2V-5B. It is a 5B model that takes an image and text and produces video, so it looked like it would fit in 32GB. On Apple Silicon I used `mlx-video`, a port to MLX, and quantized the weights to 8bit.

The first test used the base model as is. 832x480, 81 frames (about 3.4 seconds), 40 steps with CFG on. The output was good, but it took 42 minutes and memory climbed to 35GB and went into swap. Multiplying naively, 10 seconds would take over two hours. That was far from the goal.

## Turbo weights: 4 steps, no CFG

So I switched to Turbo weights (`quanhaol/Wan2.2-TI2V-5B-Turbo`), which cut the step count. It runs at 4 steps with CFG off. Same picture, same settings: 5 minutes, 22GB of memory. Put frames from the same moment side by side with the base model and the difference is hard to find.

![Frames at 1.6 seconds from videos made from the same picture with the base model at 40 steps and Turbo at 4 steps](<../blog/wan22-mac-studio-mlx/wan-base-vs-turbo-en.jpg>)

This is the command the pipeline actually calls. 4 steps, CFG scale 1 (off), fixed seed.

```python
cmd = [..., "--num-frames", str(op.get("frames", LOCAL_FRAMES)),
       "--steps", "4", "--guide-scale", "1", "--seed", "7", "--output-path", str(raw)]
```

I wrote the prompt in English, briefly: keep what is already in the picture, and name only what should move. Something like "face, hat and clothes exactly as in the picture, the young man on the right slowly sweeps the yard with a broom, static camera."

## Pitfall 1: the weights were silently dropped

My first Turbo run gave a video where only the first frame was the picture and everything after it was noise. There was no error message.

At first I thought cutting the steps to 4 had broken the scheduler. So I ran the base weights at 4 steps, and that was fine. The problem was on the Turbo weights side.

The Turbo checkpoint carries traces of the FSDP used in training in its key names. My cleanup script before conversion only stripped a prefix from the front of the keys.

```python
for p in ("model.", "module.", "generator.", "_fsdp_wrapped_module."):
    if sum(k.startswith(p) for k in ks) > len(ks) * 0.9:
        pref = p
if pref:
    sd = {k[len(pref):]: v for k, v in sd.items()}
```

But `_fsdp_wrapped_module.` was not only at the front. It was also wedged into the middle of keys inside the blocks. The converter skipped weights whose names did not match without any error, and saved random initial values in their place. That is why the first frame looked fine (it is the input picture) and the rest, which the model generated, came out as noise. After removing `_fsdp_wrapped_module.` from the middle of keys too and converting again, the output was normal.

## Pitfall 2: GPU timeout right after a big run

When I started the next test right after a 10-second run, it died while loading the text encoder (T5) with this.

```text
[METAL] GPU Timeout Error
```

Even after the big run finished, about 14GB of swap was still in use. Waiting a bit before running, or just running once more, works. So in the pipeline I put this job under the same lock file as the other heavy jobs (rendering, narration) so only one runs at a time. I'll cover that design separately in the last post of the series.

## 10 seconds: 16 minutes

The target of 10 seconds (241 frames) took 16 minutes with Turbo. Memory went up to 41GB and used a fair amount of swap, but it ran to the end. The face, clothes and art style held for the full 10 seconds, and the sweeping, the shoulder movement and the lantern under the eaves stayed intact.

![Frames at 0, 3, 6 and 9.5 seconds of the 10-second video made with Turbo](<../blog/wan22-mac-studio-mlx/wan-10s-frames-en.jpg>)

## Jitter: post-processing, not settings

The motion was fine, but the picture looked slightly choppy. I changed settings and compared the jitter ratio.

| Test (3.4-second clip) | Jitter ratio |
| --- | --- |
| Turbo, 4 steps | 1.40 |
| Turbo, 8 steps | 1.51 |
| Turbo, no temporal tiling | 1.39 |

More steps only made the motion bigger, and the jitter stayed the same. Turning off temporal tiling made no difference either. I took it as a property of the model and suppressed it in post-processing. I apply ffmpeg `tmix`, which blends neighboring frames 1:2:1, and re-encode at crf 23.

```python
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-vf", "tmix=frames=3:weights=1 2 1",
                "-c:v", "libx264", "-crf", "23", "-preset", "fast", "-pix_fmt", "yuv420p", "-an", op["out"]], check=True)
```

![The 10-second video after tmix post-processing](<../blog/wan22-mac-studio-mlx/wan-10s.gif>)

## Where I use it

It beat the goal (10 seconds within 10 to 20 minutes). The quality is below the external video service, but it passes my bar that faces and clothes must not change. So for the opening clip I still use the external service first, and I added this local model to the pipeline as the last fallback for when all of that service's limits are used up. I only measured at 832x480.

| Test (Mac Studio M2 Max 32GB, 2026-11-26) | Settings | Time | Memory |
| --- | --- | --- | --- |
| Base 8bit | 832x480, 81 frames, 40 steps + CFG | 42 min | 35GB (swap) |
| Turbo 8bit | Same settings, 4 steps, no CFG | 5 min | 22GB |
| Turbo 8bit | 241 frames (10 seconds) | 16 min | 41GB (swap) |

How I drew the character pictures on a white background and cut them out, instead of having the model paint the green background, is for the illustration post.
