import SwiftUI

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Ensure the app registers as a regular dock app
        NSApp.setActivationPolicy(.regular)

        // Watch for any window becoming key and prevent it from being
        // deallocated when closed, so the dock click can restore it.
        NotificationCenter.default.addObserver(
            forName: NSWindow.didBecomeKeyNotification,
            object: nil,
            queue: .main
        ) { notification in
            (notification.object as? NSWindow)?.isReleasedWhenClosed = false
        }

        // Catch windows SwiftUI may have already created before this observer
        DispatchQueue.main.async {
            for window in NSApplication.shared.windows {
                window.isReleasedWhenClosed = false
            }
        }
    }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        if !flag {
            var restored = false
            for window in sender.windows {
                window.makeKeyAndOrderFront(self)
                restored = true
            }
            if !restored {
                // All windows were deallocated; activate the app so
                // WindowGroup creates a fresh window.
                NSApp.activate(ignoringOtherApps: true)
            }
        }
        return true
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        // Keep the app running (and in the dock) after the window is closed.
        return false
    }
}

@main
struct InnovusXAdvisorApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.titleBar)
        .defaultSize(width: 580, height: 620)
    }
}
