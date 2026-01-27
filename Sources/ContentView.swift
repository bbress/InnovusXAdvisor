import SwiftUI

struct ContentView: View {
    @State private var suggestions = SuggestionEngine.pickThree()
    @State private var animateIn = false
    @State private var selectedSuggestion: Suggestion?

    var body: some View {
        ZStack {
            // Main list view
            VStack(spacing: 0) {
                // Header
                VStack(spacing: 6) {
                    Text("INNOVUS-X")
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                        .tracking(4)
                        .foregroundStyle(.secondary)

                    Text("Growth Advisor")
                        .font(.system(size: 28, weight: .bold, design: .rounded))
                        .foregroundStyle(.primary)

                    Text("3 fresh ideas to expand your business")
                        .font(.subheadline)
                        .foregroundStyle(.tertiary)
                }
                .padding(.top, 28)
                .padding(.bottom, 20)

                // Cards
                ScrollView {
                    VStack(spacing: 14) {
                        ForEach(Array(suggestions.enumerated()), id: \.element.id) { index, suggestion in
                            SuggestionCard(suggestion: suggestion, index: index + 1)
                                .onTapGesture {
                                    withAnimation(.spring(response: 0.4, dampingFraction: 0.85)) {
                                        selectedSuggestion = suggestion
                                    }
                                }
                                .opacity(animateIn ? 1 : 0)
                                .offset(y: animateIn ? 0 : 20)
                                .animation(
                                    .spring(response: 0.5, dampingFraction: 0.8)
                                        .delay(Double(index) * 0.12),
                                    value: animateIn
                                )
                        }
                    }
                    .padding(.horizontal, 24)
                    .padding(.bottom, 20)
                }

                Divider()

                // Footer
                HStack {
                    Text("\(formattedDate())")
                        .font(.caption)
                        .foregroundStyle(.tertiary)

                    Spacer()

                    Button(action: refresh) {
                        Label("New Ideas", systemImage: "arrow.clockwise")
                            .font(.system(size: 13, weight: .medium))
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.small)
                    .tint(.blue)
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 14)
            }
            .opacity(selectedSuggestion == nil ? 1 : 0)

            // Detail view
            if let suggestion = selectedSuggestion {
                DetailView(suggestion: suggestion) {
                    withAnimation(.spring(response: 0.4, dampingFraction: 0.85)) {
                        selectedSuggestion = nil
                    }
                }
                .transition(.asymmetric(
                    insertion: .opacity.combined(with: .move(edge: .trailing)),
                    removal: .opacity.combined(with: .move(edge: .trailing))
                ))
            }
        }
        .frame(minWidth: 520, minHeight: 560)
        .background(.background)
        .onAppear {
            withAnimation {
                animateIn = true
            }
        }
    }

    private func refresh() {
        animateIn = false
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
            suggestions = SuggestionEngine.pickThree()
            withAnimation {
                animateIn = true
            }
        }
    }

    private func formattedDate() -> String {
        let f = DateFormatter()
        f.dateStyle = .long
        return f.string(from: Date())
    }
}

// MARK: - Detail View

struct DetailView: View {
    let suggestion: Suggestion
    let onBack: () -> Void

    @State private var stepsAnimated = false

    var body: some View {
        VStack(spacing: 0) {
            // Header with back button
            HStack(alignment: .top) {
                Button(action: onBack) {
                    HStack(spacing: 4) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 13, weight: .semibold))
                        Text("Back")
                            .font(.system(size: 13, weight: .medium))
                    }
                    .foregroundStyle(.blue)
                }
                .buttonStyle(.plain)

                Spacer()

                Image(systemName: suggestion.icon)
                    .font(.system(size: 22))
                    .foregroundStyle(accentColor)
            }
            .padding(.horizontal, 24)
            .padding(.top, 20)
            .padding(.bottom, 12)

            // Suggestion info
            VStack(alignment: .leading, spacing: 8) {
                Text(suggestion.category.uppercased())
                    .font(.system(size: 10, weight: .semibold, design: .monospaced))
                    .tracking(1.5)
                    .foregroundStyle(accentColor)

                Text(suggestion.title)
                    .font(.system(size: 22, weight: .bold, design: .rounded))
                    .foregroundStyle(.primary)
                    .fixedSize(horizontal: false, vertical: true)

                Text(suggestion.description)
                    .font(.system(size: 13))
                    .foregroundStyle(.secondary)
                    .lineSpacing(2)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.horizontal, 24)
            .padding(.bottom, 16)

            Divider()
                .padding(.horizontal, 24)

            // Action steps header
            HStack {
                Text("ACTION STEPS")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .tracking(2)
                    .foregroundStyle(.secondary)

                Spacer()

                Text("\(suggestion.actions.count) steps")
                    .font(.system(size: 12))
                    .foregroundStyle(.tertiary)
            }
            .padding(.horizontal, 24)
            .padding(.top, 16)
            .padding(.bottom, 10)

            // Steps list
            ScrollView {
                VStack(spacing: 0) {
                    ForEach(Array(suggestion.actions.enumerated()), id: \.element.id) { index, action in
                        ActionStepRow(action: action, accentColor: accentColor, isLast: index == suggestion.actions.count - 1)
                            .opacity(stepsAnimated ? 1 : 0)
                            .offset(x: stepsAnimated ? 0 : 30)
                            .animation(
                                .spring(response: 0.45, dampingFraction: 0.8)
                                    .delay(Double(index) * 0.08),
                                value: stepsAnimated
                            )
                    }
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 20)
            }
        }
        .background(.background)
        .onAppear {
            withAnimation {
                stepsAnimated = true
            }
        }
    }

    private var accentColor: Color {
        switch suggestion.category {
        case "Market Expansion": return .blue
        case "Product & Service": return .purple
        case "Partnerships": return .green
        case "Revenue Model": return .orange
        case "Talent & Ops": return .pink
        case "Brand & Marketing": return .indigo
        case "Verticals": return .teal
        case "IP & Assets": return .brown
        default: return .blue
        }
    }
}

// MARK: - Action Step Row

struct ActionStepRow: View {
    let action: ActionStep
    let accentColor: Color
    let isLast: Bool

    @State private var isHovering = false

    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            // Step number + connector line
            VStack(spacing: 0) {
                ZStack {
                    Circle()
                        .fill(accentColor)
                        .frame(width: 28, height: 28)

                    Text("\(action.step)")
                        .font(.system(size: 13, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)
                }

                if !isLast {
                    Rectangle()
                        .fill(accentColor.opacity(0.2))
                        .frame(width: 2)
                        .frame(maxHeight: .infinity)
                }
            }
            .frame(width: 28)

            // Step content
            VStack(alignment: .leading, spacing: 4) {
                Text(action.title)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundStyle(.primary)

                Text(action.detail)
                    .font(.system(size: 12.5))
                    .foregroundStyle(.secondary)
                    .lineSpacing(1.5)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(.bottom, isLast ? 0 : 18)
        }
        .padding(.vertical, 6)
        .padding(.horizontal, 8)
        .background(
            RoundedRectangle(cornerRadius: 8, style: .continuous)
                .fill(isHovering ? accentColor.opacity(0.04) : .clear)
        )
        .onHover { hovering in
            withAnimation(.easeOut(duration: 0.15)) {
                isHovering = hovering
            }
        }
    }
}

// MARK: - Suggestion Card

struct SuggestionCard: View {
    let suggestion: Suggestion
    let index: Int

    @State private var isHovering = false

    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            // Number + Icon
            VStack(spacing: 6) {
                Text("\(index)")
                    .font(.system(size: 11, weight: .bold, design: .rounded))
                    .foregroundStyle(.white)
                    .frame(width: 24, height: 24)
                    .background(cardColor)
                    .clipShape(Circle())

                Image(systemName: suggestion.icon)
                    .font(.system(size: 18))
                    .foregroundStyle(cardColor)
            }
            .frame(width: 36)
            .padding(.top, 2)

            // Content
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text(suggestion.category.uppercased())
                        .font(.system(size: 10, weight: .semibold, design: .monospaced))
                        .tracking(1.5)
                        .foregroundStyle(cardColor)

                    Spacer()

                    // Tap hint
                    HStack(spacing: 3) {
                        Text("Action Steps")
                            .font(.system(size: 10))
                        Image(systemName: "chevron.right")
                            .font(.system(size: 8, weight: .semibold))
                    }
                    .foregroundStyle(.tertiary)
                    .opacity(isHovering ? 1 : 0)
                }

                Text(suggestion.title)
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundStyle(.primary)
                    .fixedSize(horizontal: false, vertical: true)

                Text(suggestion.description)
                    .font(.system(size: 13))
                    .foregroundStyle(.secondary)
                    .lineSpacing(2)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(.background)
                .shadow(color: .black.opacity(isHovering ? 0.12 : 0.06), radius: isHovering ? 8 : 4, y: 2)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(cardColor.opacity(isHovering ? 0.3 : 0.1), lineWidth: 1)
        )
        .scaleEffect(isHovering ? 1.01 : 1.0)
        .animation(.easeOut(duration: 0.2), value: isHovering)
        .onHover { hovering in
            isHovering = hovering
        }
        .contentShape(Rectangle())
    }

    private var cardColor: Color {
        switch index {
        case 1: return .blue
        case 2: return .purple
        case 3: return .orange
        default: return .blue
        }
    }
}
