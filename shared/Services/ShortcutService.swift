import Foundation
import AppKit

class ShortcutService {
    static let shared = ShortcutService()
    
    private let shortcutsURL: URL
    
    private init() {
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        let siribotDir = appSupport.appendingPathComponent("SiriBot", isDirectory: true)
        try? FileManager.default.createDirectory(at: siribotDir, withIntermediateDirectories: true)
        shortcutsURL = siribotDir.appendingPathComponent("shortcuts.json")
    }
    
    struct Shortcut: Codable, Identifiable {
        let id: UUID
        var name: String
        var phrase: String
        var action: String
        var enabled: Bool
        
        init(id: UUID = UUID(), name: String, phrase: String, action: String, enabled: Bool = true) {
            self.id = id
            self.name = name
            self.phrase = phrase
            self.action = action
            self.enabled = enabled
        }
    }
    
    func getShortcuts() -> [Shortcut] {
        guard let data = try? Data(contentsOf: shortcutsURL),
              let shortcuts = try? JSONDecoder().decode([Shortcut].self, from: data) else {
            return defaultShortcuts()
        }
        return shortcuts
    }
    
    func addShortcut(_ shortcut: Shortcut) {
        var shortcuts = getShortcuts()
        shortcuts.append(shortcut)
        saveShortcuts(shortcuts)
    }
    
    func removeShortcut(_ shortcut: Shortcut) {
        var shortcuts = getShortcuts()
        shortcuts.removeAll { $0.id == shortcut.id }
        saveShortcuts(shortcuts)
    }
    
    func matchShortcut(for phrase: String) -> Shortcut? {
        let shortcuts = getShortcuts().filter { $0.enabled }
        
        for shortcut in shortcuts {
            if phrase.localizedCaseInsensitiveContains(shortcut.phrase) {
                return shortcut
            }
        }
        return nil
    }
    
    func executeShortcut(_ shortcut: Shortcut) {
        LogService.shared.log("Executing shortcut: \(shortcut.name)", level: .info)
        
        switch shortcut.action {
        case "open_studio":
            openStudio()
        case "handoff":
            enableHandoffMode()
        case "toggle_voice":
            toggleVoiceListening()
        case "clear_memory":
            MemoryService.shared.clearAll()
        default:
            Task {
                _ = await AIPService.shared.chat("Execute: \(shortcut.action)")
            }
        }
    }
    
    func saveShortcuts(_ shortcuts: [Shortcut]) {
        if let data = try? JSONEncoder().encode(shortcuts) {
            try? data.write(to: shortcutsURL)
        }
    }
    
    private func openStudio() {
        if let appURL = NSWorkspace.shared.urlForApplication(withBundleIdentifier: "com.siribot.SiriBotStudio") {
            NSWorkspace.shared.openApplication(at: appURL, configuration: NSWorkspace.OpenConfiguration())
        }
    }
    
    private func enableHandoffMode() {
        NotificationCenter.default.post(name: .enableHandoff, object: nil)
    }
    
    private func toggleVoiceListening() {
        if BackgroundService.shared.isListening {
            BackgroundService.shared.stop()
        } else {
            BackgroundService.shared.start()
        }
    }
    
    private func defaultShortcuts() -> [Shortcut] {
        let defaults = [
            Shortcut(name: "Open SiriBot", phrase: "open siribot", action: "open_studio", enabled: true),
            Shortcut(name: "Handoff Mode", phrase: "handoff", action: "handoff", enabled: true),
            Shortcut(name: "Toggle Voice", phrase: "listen", action: "toggle_voice", enabled: true),
            Shortcut(name: "Clear Memory", phrase: "forget", action: "clear_memory", enabled: true)
        ]
        saveShortcuts(defaults)
        return defaults
    }
}

extension Notification.Name {
    static let enableHandoff = Notification.Name("enableHandoff")
}
