import Foundation
import UserNotifications
import SwiftUI

enum LogLevel: String, Codable {
    case info, warning, error, success
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

extension Notification.Name {
    static let newLogEntry = Notification.Name("newLogEntry")
}

class LogService {
    static let shared = LogService()
    
    private var logs: [LogEntry] = []
    private let maxLogs = 1000
    
    private init() {}
    
    func log(_ message: String, level: LogLevel, notify: Bool = false) {
        let entry = LogEntry(id: UUID(), level: level, message: message, timestamp: Date())
        logs.insert(entry, at: 0)
        
        if logs.count > maxLogs {
            logs.removeLast()
        }
        
        // Post notification
        NotificationCenter.default.post(name: .newLogEntry, object: entry)
        
        // System notification for errors
        if level == .error && notify {
            sendNotification(title: "SiriBot Error", body: message)
        }
        
        #if DEBUG
        let prefix: String
        switch level {
        case .info: prefix = "ℹ️"
        case .warning: prefix = "⚠️"
        case .error: prefix = "❌"
        case .success: prefix = "✅"
        }
        print("\(prefix) [\(dateFormatter.string(from: entry.timestamp))] \(message)")
        #endif
    }
    
    func getRecentLogs(count: Int = 100) -> [LogEntry] {
        return Array(logs.prefix(count))
    }
    
    func clearLogs() {
        logs.removeAll()
    }
    
    private var dateFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter
    }
    
    private func sendNotification(title: String, body: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        
        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request)
    }
}
