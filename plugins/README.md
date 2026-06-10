# Plugins

Plugins are capability bundles for the Personal AI Engineering OS.

A plugin can contain:

```text
plugin/
  plugin.json
  skills/
  prompts/
  integrations/
  commands/
  adapters/
  hooks/
```

The plugin registry tracks what exists. It does not automatically execute plugin commands.

## Import A Plugin

```bash
aios import-plugin \
  --source ./plugin_pack \
  --provider community
```

Imported plugins are stored under:

```text
plugins/vendor/<provider>/<plugin_name>/
```

External plugins default to `untrusted`.

## Registry Files

```text
registry/plugins.json
registry/providers.json
```

Use:

```bash
aios list-plugins
aios list-providers
aios index-plugins
```

After reviewing a plugin, approve it:

```bash
aios trust-plugin example_provider_pack \
  --trust-level reviewed
```
