# Jelly Extended Examples

### Menu-Driven Shortcut with HTTP (GitHub Repo Stats)

```jelly
import Shortcuts
#Color: green, #Icon: star

askForInput(prompt: "Enter a GitHub repo (e.g. anthropics/claude-code):", type: Text, default: "", allowDecimal: false, allowNegative: false) >> repoInput
text(text: "https://api.github.com/repos/${repoInput}") >> apiURL
url(url: "${apiURL}") >> apiURLObj
downloadURL(url: "${apiURLObj}", method: GET) >> apiResponse
getDictionaryFrom(input: apiResponse) >> repoData
valuesFrom(dictionary: repoData, key: "stargazers_count") >> starsVal
valuesFrom(dictionary: repoData, key: "forks_count") >> forksVal
valuesFrom(dictionary: repoData, key: "open_issues_count") >> issuesVal
valuesFrom(dictionary: repoData, key: "description") >> descVal

menu "GitHub Repo Stats - what would you like to see?" {
    case("Stars"):
        sendNotification(body: "${starsVal} stars", title: "${repoInput}", sound: true)
    case("Forks"):
        sendNotification(body: "${forksVal} forks", title: "${repoInput}", sound: true)
    case("Open Issues"):
        sendNotification(body: "${issuesVal} open issues", title: "${repoInput}", sound: true)
    case("Description"):
        sendNotification(body: "${descVal}", title: "${repoInput}", sound: true)
}
```

Note: `getDictionaryFrom` and `valuesFrom` take bare refs (no `${}`). Use plain ASCII in menu prompts -- em-dash corrupts parsing, use `-` instead.

### Weather Notification

```jelly
import Shortcuts
#Color: blue, #Icon: star

getLocation(input: ShortcutInput) >> myLocation
getCurrentConditions(location: myLocation) >> weatherData
// comment line required between conditionDetail and next action (parser bug)
conditionDetail(condition: weatherData, detail: Temperature) >> tempVal
// comment line required between conditionDetail and next action (parser bug)
conditionDetail(condition: weatherData, detail: Condition) >> condVal
text(text: "Temperature: ${tempVal} degrees, Conditions: ${condVal}") >> weatherMessage
sendNotification(body: "${weatherMessage}", title: "Current Weather", sound: true, attachment: myLocation)
```

### Date Manipulation via AppleScript (Quick Reminder Pattern)

Jelly has no `getDate()` function -- use `${CurrentDate}` magic variable or handle dates in `runAppleScript`. The AppleScript approach is simpler for complex date logic:

```jelly
import Shortcuts
#Color: red, #Icon: star

menu "When should I remind you?" {
    case("In 30 minutes"):
        text(text: "30min") >> whenKey
    case("In 1 hour"):
        text(text: "1hour") >> whenKey
    case("Tonight at 9pm"):
        text(text: "tonight9pm") >> whenKey
    case("Tomorrow morning"):
        text(text: "tomorrow8am") >> whenKey
}

askForInput(prompt: "What is the reminder for?", type: Text, default: "", allowDecimal: false, allowNegative: false) >> reminderText
text(text: "${whenKey}|||${reminderText}") >> combined

runAppleScript(script: "on run argv\nset combined to item 1 of argv\nset AppleScript's text item delimiters to \"|||\"\nset whenKey to text item 1 of combined\nset reminderTitle to text item 2 of combined\nset AppleScript's text item delimiters to \"\"\nset dueDate to current date\nif whenKey is \"30min\" then\nset dueDate to (current date) + 1800\nelse if whenKey is \"1hour\" then\nset dueDate to (current date) + 3600\nend if\ntell application \"Reminders\"\nmake new reminder at end of default list with properties {name:reminderTitle, due date:dueDate, remind me date:dueDate}\nend tell\nreturn reminderTitle\nend run", input: combined) >> scriptResult

sendNotification(body: "Reminder set: ${scriptResult}", title: "Quick Reminder", sound: true)
```

Key patterns:
- Use `"|||"` as a delimiter to pass multiple values through a single `runAppleScript` input
- `current date + seconds` (not minutes/hours) in AppleScript for time offsets
- `make new reminder ... with properties {name:..., due date:..., remind me date:...}`

### Conditional Content Length

```jelly
import Shortcuts
#Color: blue, #Icon: globe

getClipboard() >> clipURL
downloadURL(url: "${clipURL}", method: GET) >> pageContent
getTextFrom(input: pageContent) >> pageText
count(input: pageText, type: Characters) >> charCount
if(charCount > 1000) {
    runShellScript(input: pageText, script: "printf '%s' \"$JELLY_INPUT\" | head -c 200", shell: binzsh, inputMode: tostdin) >> preview
    text(text: "Long page (${charCount} chars)\n\n${preview}") >> finalOutput
} else {
    text(text: "${pageText}") >> finalOutput
}
showResult(text: "${finalOutput}")
```
