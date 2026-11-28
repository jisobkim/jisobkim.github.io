---
title: 'Adding 12 Motions to a Desktop Pet with Free Gemini: A Prompt That Edits a
  3x2 Grid'
description: I added 12 new motions to Clawd on Desk, a desktop pet that reacts to
  Claude Code, with free Gemini. The grid-edit prompt, failed tries, and background
  traps.
pubDate: '2026-11-28'
tags:
- Clawd on Desk
- desktop pet
- Claude Code pet
- Gemini image editing
- sprite animation
- APNG
- AI pixel art
- Gemini prompt
heroImage: ../blog/alfred-desktop-pet-gemini-motions/alfred-cover-en.jpg
---

A butler stands in the corner of my screen. When Claude Code starts thinking, he strokes his mustache. When it runs a tool, he polishes a silver spoon. When it needs a permission, he rings a bell. When an error happens, he drops his teacup. On October 1, I made these 12 motions with the free version of Gemini and added them. This post covers the prompts I used that day and the attempts that failed.

![The 12 new motions. From top left: pouring tea, thinking, polishing a spoon, bell, done bow, teacup mishap, dusting, yawn, dozing, collapse, sleep, wake up](<../blog/alfred-desktop-pet-gemini-motions/alfred-motions.gif>)

## Where the pet and the art come from

The pet app is [Clawd on Desk](https://github.com/rullerzhou-afk/clawd-on-desk). Install it with `brew install --cask clawd-on-desk` and it hooks into Claude Code. It swaps the pet image on screen to match the session state (thinking, running a tool, notification, error, and so on).

The pet art comes from the assets in [pablomanjarres/Alfred](https://github.com/pablomanjarres/Alfred), under the MIT license. It is one sprite sheet in Codex Pet format (1536x1872, 8 columns by 9 rows, 192x208 per cell). It only had basic motions like standing, running, and waving.

It started with [a Korean video about making game character movement with AI image tools](https://youtu.be/Ricxy_CHZig). It said Gemini is better at detailed edits, so I decided to give Alfred more motions.

## Why I could not just fill the empty cells

Only 57 of the 72 cells in the sprite are filled. At first I thought I could draw into the 15 empty cells. But the adapter that turns a Codex Pet into a Clawd theme (`codex-pet-adapter.js`) hardcodes the frame count and timing for each row (idle 6, waving 4, jumping 5, and so on). Art placed in an empty cell never plays.

So I forked the theme. I copied the `codex-pet-alfred` theme the adapter had generated, then removed the adapter marker file (`.clawd-codex-pet.json`) and the `source` entry. After that the adapter no longer overwrites it. Clawd's own themes take an APNG per state, with no limit on frame count.

The new poses had to be drawn by an outside tool. Claude can recombine existing frames, but it cannot draw new objects like a teapot or a feather duster. I used the free Gemini web app (Flash). I sent about 16 image requests that day and never saw a limit message.

## Make it edit, not draw

First I uploaded one reference frame and asked: "Draw a 6-frame sprite sheet of the same character in a single horizontal row." The character stayed the same, but I got a portrait image with six figures of different sizes. The output aspect ratio follows the input image. When I uploaded the image with no prompt, it put crowns on the bottom three.

I changed direction. I made the image myself first, with the same pose laid out six times in a 3x2 grid. Then I asked Gemini to edit it: "In each cell, change only the hidden arm like this." Position and size are already fixed, so Gemini only touches the part it needs to change. One request gives one motion.

![Left is the input image I made, right is Gemini's pouring-tea edit. The silver hair turned purple and there is a watermark in the bottom-right cell](<../blog/alfred-desktop-pet-gemini-motions/alfred-grid-edit-en.jpg>)

A small script (`clawd-pet-motion template`) builds the input image. It scales the first frame of the original up 3x and pastes it six times on a magenta (#FF00FF) background. Every prompt that worked had the same skeleton, written in English.

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

The cell numbers and reading order are what let me give each cell a different action. Cell 6 is `unchanged` because Gemini stamps a watermark in the bottom-right corner. I throw that cell away and use cell 1 in its place during playback.

I chose the arm hidden behind his back as the one that moves. Whenever the hand holding the tray was touched, the tray disappeared. I asked twice for a motion of him pulling out a pocket watch, and both times the tray and teacup vanished from the middle four cells. After that I put this sentence on the second line of the prompt.

```text
In every one of the six figures, the hand holding the silver tray with the
teacup must stay exactly as it is in the input: same arm, same tray, same
teacup on the tray, untouched.
```

With that sentence, the silver spoon and bell motions kept the tray in all six cells. In the done bow, the tray dropped out only in cell 4, where he spreads his hand to the side, so I left that cell out. The pocket watch never worked, so I replaced it with a mustache stroke that needs no new object. I did not figure out why only the pocket watch failed.

## Removing the background and packing APNGs

The returned image (1216x878) goes through `clawd-pet-motion frames`. It removes the magenta background, cuts six 192x208 cells, and builds an APNG with the order and timing I want.

```bash
clawd-pet-motion frames pour-tea.png alfred-pour-tea.apng \
  --seq 1,2,3,4,4,5,1 --ms 400,200,300,400,400,250,300
```

`--seq` is the playback order of cell numbers. Cell 6 is missing and cell 4 appears twice. That makes him hold the tilted teapot for a moment.

I hit two traps here. First, in the original sprite the silver hair highlights, the whites of the eyes, the mustache, and the shirt buttons are transparent holes (1,531 pixels per frame). Put it on magenta as is and the magenta shows through those holes. So when building the input image, I flood fill from the outside to find the real background, and fill the inner holes with white.

Second, even with the holes filled, the pouring-tea result came back with purple silver hair (right side of the image above). The background color had bled into the light gray. I tried a green background, but the background color was not the cause, so I went back to magenta. Instead, `frames` darkens the outline by subtracting the background color component, and turns the light inner areas back to gray by filling in the missing green channel.

```python
spill = (alpha > 0) & (m > 0)        # m = min(R, B) - G, magenta tint
edge = spill & ((alpha < 1) | near)  # outline touching the background
inner = spill & ~edge
r2, b2 = np.where(edge, r - m, r), np.where(edge, b - m, b)
g2 = np.where(inner, np.minimum(r, b), g)
```

## Registering in the theme

I put the APNGs in `assets/` of the forked theme and map them to states in `theme.json`.

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

Pouring tea plays once after the mouse stays still for 20 seconds. For sleep, I made five states (yawn, dozing, collapse, sleep, wake up) from one image (six cells). Only the cell combinations differ. `sweeping` is the state shown while the context is being compacted, so I gave it the feather duster.

Clawd receives states through a local server. If I send events directly, I can check the image for each state without running Claude Code.

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"state":"error","session_id":"test","event":"StopFailure"}' \
  http://127.0.0.1:23333/state
```

![Clawd window captured after sending events. Notification, task done, error](<../blog/alfred-desktop-pet-gemini-motions/alfred-states.jpg>)

## A tuxedo color per machine

I use the same pet on three machines: a Mac Studio, a MacBook Pro, and a MacBook Air. I kept losing track of which machine's screen I was looking at, so I painted the tuxedo a different color on each one (`clawd-pet-tint`).

At first I wanted to paint only the teacup. But the sprite is anti-aliased art with 4,339 colors, so there was no way to separate the white of the teacup from the white of the shirt. So I picked only dark, neutral pixels: opaque (alpha > 0.3), lightness under 0.36, saturation under 0.28. That catches the tuxedo, shoes, and bow tie. The silver hair, skin, shirt, and teacup are bright, so they are left out. I stretch the original lightness to the new range so wrinkles and shadows stay.

![Mac Studio is the black original, MacBook Pro is gray, MacBook Air is ivory](<../blog/alfred-desktop-pet-gemini-motions/alfred-tint.jpg>)

I painted the whole forked theme with the new motions using the same script, then copied it to the two MacBooks with rsync.

## What is left

Frames redrawn by Gemini are softer and lower in contrast than the original. When the pet switches from an original idle motion to a new motion, the art style shifts a little. At actual size (134px) it does not bother me much, so I am leaving it.

The running motion is still the original. The input image is a standing pose, so grid editing could not move the legs. I would need a separate input image built from the frames of the running row.

I wrote about hooking a web image service into a pipeline with browser automation in [this post](/en/blog/muse-image-pipeline-ego-lite/), and about animating images with a local video model in [this post](/en/blog/wan22-mac-studio-mlx/).
