import Foundation
import Combine

class StudioViewModel: ObservableObject {
    @Published var isListening = false
    
    func toggleListening() {
        if isListening {
            BackgroundService.shared.stop()
        } else {
            BackgroundService.shared.start()
        }
        isListening.toggle()
    }
}

class ConversationsViewModel: ObservableObject {
    @Published var conversations: [Conversation] = []
    
    init() {
        loadConversations()
    }
    
    func loadConversations() {
        // Load from memory or disk
        conversations = [
            Conversation(title: "General Chat", lastMessage: "How do I organize my desktop?", timestamp: Date()),
            Conversation(title: "Coding Help", lastMessage: "Write a Python function", timestamp: Date().addingTimeInterval(-3600)),
            Conversation(title: "Research", lastMessage: "Find info about AI", timestamp: Date().addingTimeInterval(-7200))
        ]
    }
}

struct Conversation: Identifiable {
    let id = UUID()
    var title: String
    var lastMessage: String
    var timestamp: Date
    var messages: [Message] = []
}

class ShortcutsViewModel: ObservableObject {
    @Published var shortcuts: [ShortcutService.Shortcut] = []
    @Published var showAddSheet = false
    
    init() {
        shortcuts = ShortcutService.shared.getShortcuts()
    }
    
    func toggleShortcut(_ shortcut: ShortcutService.Shortcut, enabled: Bool) {
        if let index = shortcuts.firstIndex(where: { $0.id == shortcut.id }) {
            shortcuts[index].enabled = enabled
            ShortcutService.shared.saveShortcuts(shortcuts)
        }
    }
    
    func addShortcut(_ shortcut: ShortcutService.Shortcut) {
        shortcuts.append(shortcut)
        ShortcutService.shared.addShortcut(shortcut)
    }
}

extension ShortcutService {
    func saveShortcuts(_ shortcuts: [Shortcut]) {
        let storageURL = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
            .appendingPathComponent("SiriBot")
        let shortcutsURL = storageURL.appendingPathComponent("shortcuts.json")
        if let data = try? JSONEncoder().encode(shortcuts) {
            try? data.write(to: shortcutsURL)
        }
    }
}
