// GMCF Masters Swim WOD - Shortcuts Edition
// -------------------------------------------
// Designed to run as a Scriptable.app step on iOS, not a widget.
// Returns a dictionary with:
//   - html:        Formatted workout HTML (feed to "Make PDF" in Shortcuts)
//   - structured:  Parsed workout JSON (feed to /generate API)
//   - raw:         Original workout text
//   - title:       Workout title string
//   - date:        Scheduled date string
//   - status:      "ok" | "empty" | "error"
// -------------------------------------------

const CONFIG = {
  affiliateId: "EI3YKIBca5",
  track: "Masters Swim",
  gymName: "GMCF Masters Swim",
  swimDays: [2, 3, 4], // Tue, Wed, Thu
  colors: {
    primary: "#1a6fa8",
    accent: "#0a4a7a",
    warmup: "#e8f4fd",
    set: "#f0f8e8",
    cooldown: "#fdf8e8",
    text: "#1a1a2e",
    muted: "#5a6a7a",
  }
};

// --- MAIN ---

async function main() {
  const targetDate = getTargetDate();
  const dateInt = toDateInt(targetDate);

  let workoutData;
  try {
    workoutData = await fetchWorkout(dateInt);
  } catch (e) {
    const result = {
      status: "error",
      title: "Failed to fetch workout",
      raw: "",
      html: buildErrorHTML(e.message),
      structured: null,
      date: formatDisplayDate(targetDate),
    };
    Script.setShortcutOutput(result);
    Script.complete();
    return;
  }

  if (!workoutData) {
    const isToday = toDateInt(new Date()) === dateInt;
    const result = {
      status: "empty",
      title: isToday ? "Not posted yet" : "No workout found",
      raw: "",
      html: buildEmptyHTML(formatDisplayDate(targetDate), isToday),
      structured: null,
      date: formatDisplayDate(targetDate),
    };
    Script.setShortcutOutput(result);
    Script.complete();
    return;
  }

  const structured = parseWorkoutStructure(workoutData.description, workoutData.title, workoutData.scheduledDateDisplay);
  const html = buildWorkoutHTML(structured);

  const result = {
    status: "ok",
    title: workoutData.title,
    raw: workoutData.description,
    html: html,
    structured: JSON.stringify(structured),
    date: workoutData.scheduledDateDisplay || formatDisplayDate(targetDate),
  };

  Script.setShortcutOutput(result);
  Script.complete();
}

// --- FETCH ---

async function fetchWorkout(dateInt) {
  const track = encodeURIComponent(JSON.stringify([CONFIG.track]));
  const url = `https://app.sugarwod.com/public/api/v1/affiliates/${CONFIG.affiliateId}/workouts/${dateInt}?tracks=${track}`;

  const req = new Request(url);
  req.headers = { "User-Agent": "Scriptable/GMCF-WOD" };
  req.timeoutInterval = 15;

  const json = await req.loadJSON();

  if (!json.success || !json.data || json.data.length === 0) return null;
  return json.data[0];
}

// --- PARSER ---
// Parses Steve's workout format into a structured object
// compatible with the WorkoutKit JSON schema

function parseWorkoutStructure(description, title, dateDisplay) {
  const lines = description.split("\n").map(l => l.trim()).filter(Boolean);

  // Skip the title repeat at top if it matches
  const startIdx = lines[0] === title ? 1 : 0;
  const workLines = lines.slice(startIdx);

  const sections = [];
  let currentSection = null;

  // Section detection patterns
  const SECTION_PATTERNS = [
    { regex: /^warm.?up/i, type: "warmup" },
    { regex: /^cool.?down/i, type: "cooldown" },
    { regex: /^set\s*\d/i, type: "mainSet" },
    { regex: /^main\s*set/i, type: "mainSet" },
    { regex: /^pre.?set/i, type: "preSet" },
    { regex: /^workout/i, type: "mainSet" },
  ];

  // Extract total distance from title (e.g., "Hold Focus (2500)")
  const titleDistanceMatch = title.match(/\((\d+)\)?/);
  const totalDistance = titleDistanceMatch ? parseInt(titleDistanceMatch[1]) : null;

  for (const line of workLines) {
    const sectionMatch = SECTION_PATTERNS.find(p => p.regex.test(line));

    if (sectionMatch || (line.includes(":") && line.length < 80 && /\([\d,]+\+?\)/.test(line))) {
      if (currentSection) sections.push(currentSection);

      // Extract section distance
      const distMatch = line.match(/\((\d+)\+?\)/);
      const dist = distMatch ? parseInt(distMatch[1]) : null;

      currentSection = {
        type: sectionMatch ? sectionMatch.type : "mainSet",
        header: line,
        distanceYards: dist,
        lines: [],
        intervals: [],
      };
    } else if (currentSection) {
      currentSection.lines.push(line);

      // Parse interval lines: "Nx DISTANCE TYPE @interval" or "NxDISTANCE"
      const intervalMatch = line.match(/^(\d+)\s*[xX\u00d7]\s*(\d+)\s*(.*?)(?:\s*[@:](.+))?$/);
      if (intervalMatch) {
        const reps = parseInt(intervalMatch[1]);
        const distance = parseInt(intervalMatch[2]);
        const desc = (intervalMatch[3] || "").trim();
        const rest = intervalMatch[4] ? intervalMatch[4].trim() : null;

        currentSection.intervals.push({
          reps,
          distanceYards: distance,
          description: desc,
          restInterval: rest,
        });
      }

      // Handle A/B/C option lines
      const optionMatch = line.match(/^([ABC]):\s*(.+)/);
      if (optionMatch && currentSection.intervals.length > 0) {
        const lastInterval = currentSection.intervals[currentSection.intervals.length - 1];
        if (!lastInterval.options) lastInterval.options = {};
        lastInterval.options[optionMatch[1]] = optionMatch[2].trim();
      }
    } else {
      // Line before any section detected - treat as preamble
      if (!currentSection) {
        currentSection = {
          type: "warmup",
          header: "Warm-up",
          distanceYards: null,
          lines: [line],
          intervals: [],
        };
      }
    }
  }

  if (currentSection) sections.push(currentSection);

  // Map to WorkoutKit-compatible structure
  return {
    title: title,
    scheduledDate: dateDisplay,
    totalDistanceYards: totalDistance,
    activityType: "poolSwimming",
    poolLength: 25,
    poolUnit: "yards",
    warmup: sections.find(s => s.type === "warmup") || null,
    sets: sections.filter(s => ["mainSet", "preSet"].includes(s.type)),
    cooldown: sections.find(s => s.type === "cooldown") || null,
    rawSections: sections,
    source: {
      platform: "SugarWOD",
      affiliateId: CONFIG.affiliateId,
      track: CONFIG.track,
    }
  };
}

// --- HTML BUILDER ---

function buildWorkoutHTML(structured) {
  const C = CONFIG.colors;

  const sectionHTML = (section, bgColor, icon) => {
    if (!section) return "";

    const intervalRows = section.intervals.length > 0
      ? `<table style="width:100%;border-collapse:collapse;margin-top:8px">` +
        section.intervals.map(iv => {
          const optionText = iv.options
            ? Object.entries(iv.options).map(([k, v]) => `<span style="opacity:0.7">${k}: ${v}</span>`).join(" &nbsp; ")
            : "";
          return `<tr style="border-bottom:1px solid rgba(0,0,0,0.06)">
            <td style="padding:5px 8px;font-weight:600;color:${C.primary};white-space:nowrap">${iv.reps}x${iv.distanceYards}</td>
            <td style="padding:5px 8px;color:${C.text}">${iv.description}</td>
            <td style="padding:5px 8px;color:${C.muted};text-align:right;white-space:nowrap">${iv.restInterval || ""}</td>
          </tr>${optionText ? `<tr><td></td><td colspan="2" style="padding:2px 8px 6px;font-size:12px;color:${C.muted}">${optionText}</td></tr>` : ""}`;
        }).join("") +
        `</table>`
      : "";

    const noteLines = section.lines
      .filter(l => !section.intervals.some(iv => l.match(/^\d+\s*[xX\u00d7]/)))
      .map(l => `<p style="margin:4px 0;color:${C.muted};font-size:13px">${escapeHTML(l)}</p>`)
      .join("");

    const distBadge = section.distanceYards
      ? `<span style="float:right;background:${C.primary}22;color:${C.primary};padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600">${section.distanceYards} yds</span>`
      : "";

    return `
      <div style="background:${bgColor};border-left:4px solid ${C.primary};border-radius:0 8px 8px 0;margin-bottom:16px;padding:12px 14px">
        <div style="font-size:14px;font-weight:700;color:${C.accent};margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">
          ${icon} ${escapeHTML(section.header)} ${distBadge}
        </div>
        ${intervalRows}
        ${noteLines}
      </div>`;
  };

  const setsHTML = structured.sets.map((set, i) =>
    sectionHTML(set, CONFIG.colors.set, `Set ${i + 1}`)
  ).join("");

  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body { font-family: -apple-system, 'SF Pro Text', sans-serif; margin: 0; padding: 20px; color: ${C.text}; background: white; }
  @media print { body { padding: 10px; } }
</style>
</head>
<body>

<div style="background:${C.accent};color:white;padding:16px 20px;border-radius:12px;margin-bottom:20px">
  <div style="font-size:11px;opacity:0.7;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">
    GMCF Masters Swim
  </div>
  <div style="font-size:20px;font-weight:700;line-height:1.2">${escapeHTML(structured.title)}</div>
  <div style="font-size:13px;opacity:0.8;margin-top:6px">${escapeHTML(structured.scheduledDate)}</div>
  ${structured.totalDistanceYards ? `<div style="margin-top:8px"><span style="background:rgba(255,255,255,0.2);padding:3px 10px;border-radius:20px;font-size:13px;font-weight:600">${structured.totalDistanceYards} yards total</span></div>` : ""}
</div>

${sectionHTML(structured.warmup, C.warmup, "Warm-up")}
${setsHTML}
${sectionHTML(structured.cooldown, C.cooldown, "Cooldown")}

<div style="margin-top:20px;padding-top:12px;border-top:1px solid #eee;font-size:11px;color:${C.muted};text-align:center">
  GMCF Masters Swim &middot; gmcf.life &middot; Coach Steve Maas
</div>

</body>
</html>`;
}

function buildErrorHTML(message) {
  return `<!DOCTYPE html><html><body style="font-family:-apple-system;padding:20px;color:#333">
<h2 style="color:#c00">Could Not Load Workout</h2>
<p>${escapeHTML(message)}</p>
<p style="color:#888;font-size:12px">Check your network connection and try again.</p>
</body></html>`;
}

function buildEmptyHTML(dateDisplay, isToday) {
  const msg = isToday
    ? "Steve hasn't posted today's workout yet. Check back closer to practice time."
    : "No Masters Swim workout was found for this date.";
  return `<!DOCTYPE html><html><body style="font-family:-apple-system;padding:20px;color:#333">
<h2 style="color:#666">${escapeHTML(dateDisplay)}</h2>
<p>${msg}</p>
</body></html>`;
}

// --- HELPERS ---

function getTargetDate() {
  const now = new Date();
  const day = now.getDay();
  if (CONFIG.swimDays.includes(day)) return now;
  for (let i = 1; i <= 7; i++) {
    const next = new Date(now);
    next.setDate(now.getDate() + i);
    if (CONFIG.swimDays.includes(next.getDay())) return next;
  }
  return now;
}

function toDateInt(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return parseInt(`${y}${m}${d}`);
}

function formatDisplayDate(date) {
  return date.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });
}

function escapeHTML(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// --- RUN ---
await main();
