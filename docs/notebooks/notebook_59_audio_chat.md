# Voice Chat

The voice output notebook was text in, voice out (Agent plus dedicated TTS). This is
the next step: a single multimodal chat call to an audio-capable
OpenAI model that takes a `.wav` as the user message and replies with
both text and audio in one shot — the shape of a 24/7 payments support
line where a cardholder phones in about a declined charge and gets
spoken guidance back.

Pipeline::

                      (synth via the voice output notebook if absent)
                                       │
                                       ▼
                          ./notebook_59_question.wav
                                       │
                                       ▼
              POST /v1/chat/completions
              model=gpt-audio
              modalities=["text","audio"]
              messages[-1].content = [{type:"input_audio", ...}]
                                       │
                                       │ {choices[0].message.audio.data, .transcript}
                                       ▼
                          ./notebook_59_answer.wav
                          (+ printed transcript)

- One model call replaces three (transcribe → chat → synthesise),
  cutting latency for a payments line that must answer in seconds.
- A plain OpenAI client — no realtime websocket plumbing required.
- `gpt-audio` returns a PCM-16 audio block, wrapped in a WAV header for
  portability (re-encode to mp3 with ffmpeg if you need it).
- The assistant is framed to never ask the caller to read out their full
  card number, CVV, or one-time passcode, and to point them at the bank
  number on the back of the card to approve a flagged charge.

Prerequisites: an OpenAI API key with access to an audio-capable model
(`gpt-audio` for chat, `gpt-4o-mini-tts` to synthesise the cardholder's
question on first run).

Run it:

    LOCUS_MODEL_PROVIDER=openai \
    OPENAI_API_KEY=sk-... \
    python examples/notebook_59_audio_chat.py

    afplay notebook_59_answer.wav   # macOS

With `LOCUS_MODEL_PROVIDER=mock` (or no `OPENAI_API_KEY`) the notebook
runs fully offline: it skips the network and produces a short simulated
PCM-16 reply so you can read the event flow before wiring real
credentials.

## Source

````python
--8<-- "examples/notebook_59_audio_chat.py"
````
