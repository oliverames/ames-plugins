# SwiftUI Coding Rules (Apple Platforms 26+)

Authoritative conventions from the Swift/SwiftUI team for writing, reviewing, or refactoring code.

## Swift Code Style

- Use 2-space indentation at every level. Convert existing code that uses different indentation.
- Prefer `var` for stored properties in structs. Reserve `let` only when preserving invariants.
- Use strong types to encode guarantees at compile time. Create String-backed enums for values with a fixed set of options.
- Never name custom types with names already used by framework types (e.g., do not create a view called `ProgressView`, `Button`, `Label`, etc.).
- Place the primary type for a file at the top; supporting types go below it.
- Prefer trailing closures (including multiple trailing closures) unless there is a strong reason not to.
- Do not emit `#Preview` blocks in generated code. When reviewing existing code, prefer `#Preview` over the legacy `PreviewProvider` protocol.

## UI Design

- Make all UI Apple-like: clean typography, consistent padding and spacing.
- Prefer SF Symbols over emoji in all UI elements.
- Use the real ellipsis character `…` (U+2026), never three dots `...`.

## Styling

- To use the app's accent color, apply `.tint` on `ShapeStyle`.
- `.tint`, `.primary`, `.secondary`, etc. are different `ShapeStyle` types and cannot be mixed in a ternary. Erase the type with `AnyShapeStyle`:

```swift
.foregroundStyle(
  condition ? AnyShapeStyle(.tint) : AnyShapeStyle(.primary)
)
```

## Controls and Toolbars

Choose control types based on semantics, then style visually:

- **`Toggle`** with `.toggleStyle(.button)` for persistent state (e.g., a filter that IS set to "Unread").
- **`Button`** with alternating labels for actions that change something (e.g., "Show Details" / "Hide Details").
- **`Picker`** with `.pickerStyle(.menu)` for selecting one option from many. Do not use a `Menu` of `Button`s.
- Apply `.buttonStyle()` to controls styled as buttons (`Toggle`, `Picker`, `Menu`, etc.) to customize their appearance.
- Most controls that accept a string label also accept `systemImage:`. Use that instead of a trailing closure with a `Label`:

```swift
Button("Play", systemImage: "play") { }
```

- For `Slider`, always pass `label`, `minimumValueLabel`, and `maximumValueLabel` as view builder closures. Use `Image(systemName:)` with appropriate SF Symbols for min/max.
- Rounded-rectangle buttons: make the background part of the label so the entire area is tappable.
- Toolbar items: prefer symbols over text.
  - Avoid SF Symbols ending in `.circle` in toolbar items (they already have a platter background).
  - Group related toolbar items with `ToolbarItemGroup`.
  - Do not group text toolbar items with other toolbar items.

## File and Media

- When accessing a file URL, always start and stop accessing the security-scoped resource.
- When playing audio files, use `AVAudioEngine` with `AVAudioFile`.

## iOS 26 APIs

The most recent version of iOS is iOS 26, released in 2025. All iOS 26 APIs must be guarded with `@available(iOS 26.0, *)` or `if #available(iOS 26.0, *) { ... }`.

### Liquid Glass

Apply `.glassEffect()` to container views for a glass background:

```swift
someContent
  .padding()
  .glassEffect(in: .rect(cornerRadius: 16))
```

Rules:
- Allowed style variants: `.glassEffect(.regular)`, `.glassEffect(.regular.tint(color))`, `.glassEffect(.regular.interactive())`, and the shaped variant `glassEffect(_:in:isEnabled:)`. Do not pass unavailable styles.
- Apply corner radius via the `in:` shape parameter (e.g., `.rect(cornerRadius: 16)`).
- Apply padding outside `.glassEffect` so clipping is correct.
- Never combine `.glassEffect` with `.background(.ultraThinMaterial)` or other blurs.
- For overlapping glass items, wrap children in `GlassEffectContainer(spacing:) { ... }`.
- Use `.buttonStyle(.glass)` for standard glass buttons and `.buttonStyle(.glassProminent)` for emphasis. Never reimplement glass buttons manually.
- For interactive reactions, use `.regular.interactive()` (or `.interactive(true)`). Disable with `isEnabled: false`.
- For morphing between shapes, keep content in the same container and use `@Namespace` + `matchedGeometryEffect` on the glass container.

### Foundation Models

Import `FoundationModels` for on-device LLM. Always check availability and provide fallback UI:

```swift
import FoundationModels

let model = SystemLanguageModel.default
switch model.availability {
case .available:
  // show AI-powered UI
case .unavailable(let reason):
  // show fallback UI
}
```

Session management:
- Create sessions with `LanguageModelSession()` or `LanguageModelSession(instructions:)` for a system prompt.
- Reuse a session for multi-turn conversations; create a new one for single-turn.
- Generate text: `try await session.respond(to: prompt)`. Access results via `response.content`.
- Only one request at a time per session. Check `isResponding` before sending another.
- Optionally pass `GenerationOptions(temperature:, maxTokens:)`.

For structured output, use `@Generable` and `@Guide` macros:

```swift
@Generable(description: "A recipe suggestion")
struct Recipe {
  @Guide(description: "The recipe title")
  var title: String
  @Guide(description: "Estimated prep time in minutes")
  var prepMinutes: Int
}

let result = try await session.respond(
  to: "Suggest a quick dinner recipe",
  generating: Recipe.self
)
let recipe = result.content
```

## Purpose Strings

When generating permission purpose strings for the project:

- Keep them under 4,000 bytes. Typical strings are one complete sentence, with optional additional information to help the user make an informed decision.
- Use the proper type the corresponding key requires (typically a string).
- Make the description accurate, meaningful, and specific about why the app needs the protected resource.
- Good examples:
  - "Your location is used to show your position on the map, get directions, estimate travel times, and improve search results."
  - "This app requires camera access to capture your site photos."
