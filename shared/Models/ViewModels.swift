import Foundation
import Combine
import SwiftUI

class ConversationViewModel: ObservableObject {
    @Published var messages: [Message] = []
    @Published var isConnected = false
    @Published var isRecording = false
    @Published var isProcessing = false
    
    init() {
        Task {
            isConnected = await AIPService.shared.testConnection()
        }
    }
    
    func sendMessage(_ text: String) {
        let userMessage = Message(role: "user", content: text)
        messages.append(userMessage)
        
        Task {
            isProcessing = true
            let response = await AIPService.shared.chat(text)
            await MainActor.run {
                messages.append(Message(role: "assistant", content: response))
                isProcessing = false
            }
        }
    }
    
    func toggleRecording() {
        isRecording.toggle()
        if isRecording {
            VoiceService.shared.startListening { [weak self] text in
                self?.sendMessage(text)
                self?.isRecording = false
            }
        } else {
            VoiceService.shared.stopListening()
        }
    }
}

class MemoryViewModel: ObservableObject {
    @Published var memories: [MemoryEntry] = []
    @Published var searchText = ""
    
    var filteredMemories: [MemoryEntry] {
        if searchText.isEmpty {
            return memories
        }
        return memories.filter { $0.key.localizedCaseInsensitiveContains(searchText) || $0.value.localizedCaseInsensitiveContains(searchText) }
    }
    
    init() {
        loadMemories()
    }
    
    func loadMemories() {
        memories = MemoryService.shared.getAll()
    }
}

class HandoffViewModel: ObservableObject {
    @Published var isActive = false
    @Published var currentTask = ""
    @Published var progress: Double = 0
    @Published var completedSteps = 0
    @Published var totalSteps = 0
    
    func start(task: String) {
        currentTask = task
        isActive = true
        HandoffService.shared.startHandoff(task: task) { [weak self] in
            self?.updateProgress()
        }
    }
    
    func stop() {
        HandoffService.shared.stopHandoff()
        isActive = false
    }
    
    func startDemo() {
        start(task: "Organize desktop files by type")
    }
    
    private func updateProgress() {
        progress = HandoffService.shared.progress
    }
}

class LogsViewModel: ObservableObject {
    @Published var logs: [LogEntry] = []
    
    init() {
        NotificationCenter.default.addObserver(forName: .newLogEntry, object: nil, queue: .main) { [weak self] notification in
            if let entry = notification.object as? LogEntry {
                self?.logs.insert(entry, at: 0)
            }
        }
        logs = LogService.shared.getRecentLogs()
    }
    
    func filteredLogs(level: LogLevel?, search: String) -> [LogEntry] {
        var result = logs
        if let level = level {
            result = result.filter { $0.level == level }
        }
        if !search.isEmpty {
            result = result.filter { $0.message.localizedCaseInsensitiveContains(search) }
        }
        return result
    }
}

class SkillsViewModel: ObservableObject {
    @Published var skills: [Skill] = []
    @Published var showAddSheet = false
    
    init() {
        loadSkills()
    }
    
    func loadSkills() {
        skills = SkillsService.shared.getAllSkills()
    }
    
    func toggleSkill(_ skill: Skill, enabled: Bool) {
        SkillsService.shared.setEnabled(skill, enabled: enabled)
        if let index = skills.firstIndex(where: { $0.id == skill.id }) {
            skills[index].enabled = enabled
        }
    }
}

extension Notification.Name {
    static let newLogEntry = Notification.Name("newLogEntry")
}
