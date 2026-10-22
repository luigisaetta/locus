# Skills

[AgentSkills.io](https://agentskills.io)-compatible packaged instruction bundles (`SKILL.md`
files) that agents load on demand via progressive disclosure:

- **L1:** the skill catalog (names + descriptions) appears in the
  system prompt.
- **L2:** the agent activates a skill — full instructions are loaded.
- **L3:** activation also appends a listing of the skill's resource
  files (`scripts/`, `references/`, `assets/`) — the first 20 by default
  (the `max_resource_files` argument of `SkillsPlugin`;
  `AgentConfig.skills` uses the default). A skill with no folder
  (`path=None`) has none. The listing gives paths, not contents, and the
  skills plugin registers no file reader. To open those files the agent
  needs a tool that can read them, such as a file or MCP read tool you
  register, or code execution (`code_mode`).

Attach via `AgentConfig.skills=[skill_or_path, ...]`.

For the concepts, start with [Skills](../concepts/skills.md).

::: locus.skills.models.Skill
::: locus.skills.plugin.SkillsPlugin
