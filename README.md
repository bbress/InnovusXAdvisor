# InnovusX Advisor

A macOS app that generates fresh business expansion ideas for [Innovus-X](https://innovus-x.com/). Every time you open the app, you get 3 new strategic suggestions — click any idea to see 3-5 actionable steps to get started.

![macOS](https://img.shields.io/badge/platform-macOS_13+-blue) ![Swift](https://img.shields.io/badge/Swift-5.9-orange) ![SwiftUI](https://img.shields.io/badge/UI-SwiftUI-purple)

## Features

- **3 random suggestions** from a pool of 30 curated business growth ideas
- **7 categories**: Market Expansion, Product & Service, Partnerships, Revenue Model, Talent & Ops, Brand & Marketing, Verticals, and IP & Assets
- **Click any card** to reveal 3-5 detailed action steps with specific, practical guidance
- **"New Ideas" button** to shuffle and get a fresh set without restarting
- Animated card transitions and hover effects
- Native macOS app built with SwiftUI

## Screenshots

| Main View | Action Steps |
|-----------|-------------|
| 3 suggestion cards with category labels and descriptions | Numbered step-by-step guide with a connected timeline |

## Requirements

- macOS 13.0+
- Xcode 15+ or Swift 5.9+

## Build & Run

```bash
git clone https://github.com/bbress/InnovusXAdvisor.git
cd InnovusXAdvisor
swift build
open .build/debug/InnovusXAdvisor
```

## Install to Applications

```bash
swift build
mkdir -p "/Applications/InnovusX Advisor.app/Contents/MacOS"
cp .build/debug/InnovusXAdvisor "/Applications/InnovusX Advisor.app/Contents/MacOS/InnovusX Advisor"
```

## Project Structure

```
InnovusXAdvisor/
├── Package.swift                 # Swift package manifest
└── Sources/
    ├── InnovusXAdvisorApp.swift  # App entry point
    ├── ContentView.swift         # Main UI, detail view, and card components
    └── SuggestionEngine.swift    # Suggestion data and random selection logic
```

## License

MIT
