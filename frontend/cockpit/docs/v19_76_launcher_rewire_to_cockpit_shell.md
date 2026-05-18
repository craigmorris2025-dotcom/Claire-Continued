# Claire Syntalion v19.76

## Launcher Rewire to Cockpit Shell

This build rewires the root launcher toward the new cockpit shell.

## Primary launcher UI target

```text
frontend/cockpit/shell/cockpit_shell.html
```

## Legacy fallback preserved

```text
frontend/command_center/modern/index.html
```

## Backup

```text
backups/v19_76_launcher_rewire_to_cockpit_shell/LAUNCH_CLAIRE_before_v19_76.bat
```

## Not done

- legacy dashboard deleted: no
- backend rewritten: no
- cockpit fake data added: no

## Manual verification

Run:

```bat
LAUNCH_CLAIRE.bat
```

Then verify:

```text
http://localhost:8000/dashboard/payload/status
http://localhost:8000/dashboard/payload
```
