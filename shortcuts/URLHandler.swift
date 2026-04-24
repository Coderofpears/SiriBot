import AppKit
import Foundation

class URLHandler {
    static let shared = URLHandler()
    
    func handle(_ url: URL) {
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let host = components.host else { return }
        
        let queryItems = components.queryItems ?? []
        
        switch host {
        case "chat":
            let text = queryItems.first { $0.name == "text" }?.value ?? ""
            handleChat(text)
        case "handoff":
            let task = queryItems.first { $0.name == "task" }?.value ?? ""
            handleHandoff(task)
        case "voice":
            let command = queryItems.first { $0.name == "command" }?.value ?? ""
            handleVoice(command)
        case "skill":
            let skill = queryItems.first { $0.name == "skill" }?.value ?? ""
            handleSkill(skill)
        default:
            LogService.shared.log("Unknown URL scheme: \(host)", level: .warning)
        }
    }
    
    private func handleChat(_ text: String) {
        Task {
            let response = await AIPService.shared.chat(text)
            // Could send notification or speak response
            LogService.shared.log("Chat response: \(response)", level: .info)
        }
    }
    
    private func handleHandoff(_ task: String) {
        HandoffService.shared.startHandoff(task: task) { }
    }
    
    private func handleVoice(_ command: String) {
        Task {
            let response = await AIPService.shared.chat(command)
            VoiceService.shared.speak(response)
        }
    }
    
    private func handleSkill(_ skill: String) {
        if let skillObj = SkillsService.shared.matchSkill(for: skill) {
            Task {
                _ = await SkillsService.shared.executeSkill(skillObj, context: [:])
            }
        }
    }
}
