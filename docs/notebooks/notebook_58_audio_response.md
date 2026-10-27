# Voice Output

A real agent often needs to talk, not just type. This notebook pairs a
regular chat-completions agent (text in, text out) with OpenAI's
audio.speech endpoint so a cloud status advisory can be spoken aloud —
ready for the on-call hotline, a status-page audio feed, or an IVR
announcement about a region degradation.

Pipeline::

    advisory request ──▶ Agent (chat model)
                            │
                            │  advisory text
                            ▼
                      OpenAI /v1/audio/speech
                      (gpt-4o-mini-tts)
                            │
                            │  mp3 bytes
                            ▼
                      ./notebook_58_response.mp3

- A plain OpenAI client — no separate audio service to configure.
- Bring-your-own-voice via the `voice=` parameter (alloy, ash, ballad,
  coral, echo, sage, shimmer, verse).
- Output is a normal MP3 you can pipe into a frontend `<audio>`
  element, the on-call IVR, or a status-page audio feed.

Prerequisites for live speech: an OpenAI API key with access to a TTS
model. The notebook uses `gpt-4o-mini-tts` for synthesis.

Run it:

    LOCUS_MODEL_PROVIDER=openai \
    OPENAI_API_KEY=sk-... \
    python examples/notebook_58_audio_response.py

    afplay notebook_58_response.mp3   # macOS

Offline, under `LOCUS_MODEL_PROVIDER=mock` (or with no `OPENAI_API_KEY`),
the agent still drafts the advisory text against the mock model and the
notebook prints the synthesis step it *would* run instead of calling the
real TTS endpoint — so it runs end-to-end with zero credentials.

## Source

````python
--8<-- "examples/notebook_58_audio_response.py"
````
