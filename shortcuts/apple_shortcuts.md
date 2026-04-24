# Apple Shortcuts Integration

SiriBot integrates with Apple Shortcuts through a URL scheme and the Shortcuts app.

## URL Scheme

Open SiriBot with these URLs:

```
siribot://chat?text=YOUR_MESSAGE
siribot://handoff?task=YOUR_TASK
siribot://voice?command=YOUR_COMMAND
siribot://skill?skill=SKILL_NAME
```

## Shortcut Actions

### 1. Get SiriBot Response
```
URL: siribot://chat?text={Query}
Method: GET
```

### 2. Start Handoff Task
```
URL: siribot://handoff?task={Task}
Method: GET
```

### 3. Voice Command
```
URL: siribot://voice?command={Phrase}
Method: GET
```

### 4. Execute Skill
```
URL: siribot://skill?skill={SkillName}
Method: GET
```

## Example Shortcuts

### "Ask SiriBot"
```applescript
tell application "Shortcuts"
    run shortcut "Ask SiriBot"
end tell
```

### "Start Homework"
```applescript
tell application "Shortcuts"
    run shortcut "Start Homework"
end tell
```

## Installation

The SiriBot URL scheme is registered automatically on first launch. No additional setup required.
