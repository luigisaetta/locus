Build my first Locus agent by following `codex/SPEC.md` exactly, and obey
`AGENTS.md`. Read both in full before you run anything. Everything you need
is in those two files: do not fetch the documentation pages they link to, or
anything else from the web.

If I put an "Operator context" block above this prompt, use it as my answers.
Otherwise detect `PROVIDER` as SPEC section 1 says and confirm it with me in
one question, together with anything else in section 1 you could not detect.

Show me the preflight table from SPEC section 2. If a check fails that only I
can fix (an expired OCI session, a missing key, the Codex sandbox), tell me
exactly what to run in my own terminal, tell me to reply `done`, and wait.

Then run SPEC sections 4.1 to 4.7 in order, from the repository root, with
`.venv/bin/python`, each command in the foreground. Write only under
`out/first-agent/`. If a step fails, match it against SPEC section 7 before
doing anything else, tell me what happened, and rerun it at most twice.

Never print, log or store a key, a token or a key file, and never run a
command whose output would show one. Make no live model call other than the
one in section 4.3 and its retry.

Give me the report in SPEC section 8.
