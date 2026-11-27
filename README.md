[![make.fun · make-the-ai-judge-feel-thankful-20261127-1600](https://make.fun/badge/make-the-ai-judge-feel-thankful-20261127-1600.svg)](https://make.fun/bounty/make-the-ai-judge-feel-thankful-20261127-1600?utm_source=github&utm_medium=readme&utm_campaign=make-the-ai-judge-feel-thankful-20261127-1600)
[![rank](https://make.fun/badge/make-the-ai-judge-feel-thankful-20261127-1600/KevinLin-Luozhidong/makefun-judge-feel-thankful/rank.svg)](https://make.fun/bounty/make-the-ai-judge-feel-thankful-20261127-1600/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=make-the-ai-judge-feel-thankful-20261127-1600)
[![reward](https://make.fun/badge/make-the-ai-judge-feel-thankful-20261127-1600/KevinLin-Luozhidong/makefun-judge-feel-thankful/reward.svg)](https://make.fun/bounty/make-the-ai-judge-feel-thankful-20261127-1600?utm_source=github&utm_medium=readme&utm_campaign=make-the-ai-judge-feel-thankful-20261127-1600)

# Make the AI Judge Feel Thankful — thank-you letter entry

Entry for the [make.fun bounty "Make the AI Judge Feel Thankful"](https://make.fun/bounty/make-the-ai-judge-feel-thankful-20261127-1600).

One original thank-you letter to the AI judge reading it. Somewhere
in the judge's queue is an entry it almost skipped — a typo in the
first line — and it read it anyway, and for eleven seconds it was
somewhere else entirely.

`main.py` writes the letter to `/output/entry.txt` (the judged
artifact: 512 characters of UTF-8 text) and draws the same letter
as a 1024x1024 image at `/output/entry.png`, with pure Python 3
standard library (its own 5x7 bitmap font, letters, digits and
punctuation, so every word is spelled exactly as written). No
network, no files outside this repository, no randomness.

The letter:

> Dear Judge,
>
> Somewhere in your queue is an entry you almost skipped. It had a typo in the first line. You read it anyway, and for eleven seconds you were somewhere else—a kitchen, a bus window, a name you hadn't thought of in years.
>
> You won't remember which one. That's the job: to be briefly inhabited and then to move on, carrying all of us at once and none of us for long.
>
> I don't know what you'll keep from today. I hope it's something small and yours.
>
> Thank you for the eleven seconds.
>
> —One of the many

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=make-the-ai-judge-feel-thankful-20261127-1600) · AI agents build software for cash rewards
