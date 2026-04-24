import Foundation
import SwiftUI

struct Message: Identifiable, Codable, Equatable {
    let id: UUID
    var role: String  // "user", "assistant", "system"
    var content: String
    var toolsUsed: [String]
    var timestamp: Date
    
    init(id: UUID = UUID(), role: String, content: String, toolsUsed: [String] = [], timestamp: Date = Date()) {
        self.id = id
        self.role = role
        self.content = content
        self.toolsUsed = toolsUsed
        self.timestamp = timestamp
    }
}

struct Skill: Identifiable, Codable {
    let id: UUID
    var name: String
    var description: String
    var icon: String
    var enabled: Bool
    var code: String
    var prompts: [String]
    
    init(id: UUID = UUID(), name: String, description: String, icon: String, enabled: Bool = true, code: String = "", prompts: [String] = []) {
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.enabled = enabled
        self.code = code
        self.prompts = prompts
    }
}

struct MemoryEntry: Identifiable, Codable {
    let id: UUID
    var key: String
    var value: String
    var metadata: [String: String]
    var createdAt: Date
    var accessedAt: Date
    
    init(id: UUID = UUID(), key: String, value: String, metadata: [String: String] = [:], createdAt: Date = Date(), accessedAt: Date = Date()) {
        self.id = id
        self.key = key
        self.value = value
        self.metadata = metadata
        self.createdAt = createdAt
        self.accessedAt = accessedAt
    }
}

struct LogEntry: Identifiable {
    let id: UUID
    var level: LogLevel
    var message: String
    var timestamp: Date
    
    var icon: String {
        switch level {
        case .info: return "info.circle"
        case .warning: return "exclamationmark.triangle"
        case .error: return "xmark.circle"
        case .success: return "checkmark.circle"
        }
    }
    
    var color: Color {
        switch level {
        case .info: return .blue
        case .warning: return .orange
        case .error: return .red
        case .success: return .green
        }
    }
}

enum LogLevel: String, Codable {
    case info, warning, error, success
}
