// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "InnovusXAdvisor",
    platforms: [.macOS(.v13)],
    targets: [
        .executableTarget(
            name: "InnovusXAdvisor",
            path: "Sources"
        )
    ]
)
