# Scoring

## From text to a number

Each guess and the target word are embedded with
[`silma-ai/silma-embedding-matryoshka-v0.1`](https://huggingface.co/silma-ai/silma-embedding-matryoshka-v0.1),
an Arabic sentence-embedding model fine-tuned from AraBERT. Their cosine
similarity is a number in `[-1, 1]`.

That raw cosine is a poor thing to show a player. Real Arabic word pairs cluster
tightly: unrelated words rarely score below about 0.2, so a linear mapping
would start everyone at "50%" and make the whole game feel like noise.

## The curve

```python
# api/app/services/similarity_service.py
x = (cos_sim + 1) / 2        # [-1, 1] → [0, 1]
score = x ** 2 * 100         # back-load the curve
```

Squaring compresses the low end and stretches the top, so the score only climbs
steeply once you are genuinely close:

| cosine | score | feels like |
|---:|---:|---|
| -1.0 | 0.0 | opposite (effectively never happens) |
| 0.0 | 25.0 | unrelated |
| 0.3 | 42.3 | same general domain |
| 0.6 | 64.0 | related |
| 0.8 | 81.0 | close |
| 0.95 | 95.1 | very close |
| 1.0 | 100.0 | correct |

Both values are stored on every guess: `similarity_score` (what the player
sees) and `cosine_similarity` (the raw measurement). Changing the curve later
therefore does not invalidate historical data.

## Non-Arabic input

A guess containing Latin letters short-circuits to `0.0` without consulting the
model. The model is Arabic; a Latin string would still produce *some* embedding
and *some* distance, and showing a player a confident-looking 31% for `hello`
would be misleading. The guess is still recorded, so it counts as an attempt.

## Changing the model

Set `ML_MODEL_NAME` to any `sentence-transformers`-compatible model. Scores are
not comparable across models: existing `similarity_score` values stay as they
were, computed under the old model, so switching models mid-deployment means
accepting a discontinuity in the archive.
