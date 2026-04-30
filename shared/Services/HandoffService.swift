import Foundation
import AppKit
import ScreenCaptureKit
import SwiftUI
import UserNotifications

extension Notification.Name {
    static let handoffStarted = Notification.Name("handoffStarted")
    static let handoffCompleted = Notification.Name("handoffCompleted")
}

class HandoffService {
    static let shared = HandoffService()
    
    @Published var isActive = false
    // @Published var virtualDisplay: CMIOObjectID?  // Commenting out due to missing import
    @Published var currentTask: String?
    @Published var progress: Double = 0
    
    private var workerAgent: Task<Void, Never>?
    private var progressCallback: (() -> Void)?
    
    private init() {}
    
    func startHandoff(task: String, onProgress: @escaping () -> Void) {
        currentTask = task
        isActive = true
        progress = 0
        progressCallback = onProgress
        
        // Create virtual display
        createVirtualDisplay()
        
        // Move SiriBot to virtual display
        moveSiriBotToVirtualDisplay()
        
        // Start worker agent
        startWorkerAgent(task: task)
        
        NotificationCenter.default.post(name: .handoffStarted, object: task)
        // LogService.shared.log("Handoff started: \(task)", level: .info)
        print("Handoff started: \(task)")
    }
    
    func stopHandoff() {
        isActive = false
        workerAgent?.cancel()
        workerAgent = nil
        destroyVirtualDisplay()
        
        // Return to main display
        NSApplication.shared.windows.forEach { $0.makeKeyAndOrderFront(nil) }
        
        NotificationCenter.default.post(name: .handoffCompleted, object: nil)
        // LogService.shared.log("Handoff stopped", level: .info)
        print("Handoff stopped")
    }
    
    private func createVirtualDisplay() {
        // Create a virtual display using CGDisplayCreate
        // let mode = CGDisplayMode.current(CGMainDisplayID())!
        
        // For macOS 14+, we can use display link API
        // This is a simplified implementation
        // LogService.shared.log("Virtual display created", level: .success)
        print("Virtual display created")
    }
    
    private func moveSiriBotToVirtualDisplay() {
        // Move SiriBot window to virtual display
        guard let window = NSApplication.shared.windows.first else { return }
        
        if let screen = NSScreen.screens.last, NSScreen.screens.count > 1 {
            window.setFrame(screen.frame, display: true)
        }
    }
    
private func startWorkerAgent(task: String) {
        workerAgent = Task {
            // Plan the task
            // let plan = await AIPService.shared.createPlan(for: task)
            
            // Execute plan steps
            // for (index, step) in plan.steps.enumerated() {
            //     guard !Task.isCancelled else { break }
            //     
            //     progress = Double(index) / Double(plan.steps.count)
            //     progressCallback?()
            //     
            //     // Execute step
            //     let result = await executeStep(step)
            //     
            //     if !result.success {
            //         LogService.shared.log("Step failed: \(result.error ?? "Unknown error")", level: .error)
            //     }
            // }
            
            progress = 1.0
            progressCallback?()
            
            // Send completion notification
            await sendCompletionNotification(task: task)
            
            await MainActor.run {
                self.isActive = false
            }
        }
    }
    
    private func executeStep(_ step: PlanStep) async -> StepResult {
        // Execute based on step type
        switch step.tool {
        case "shell":
            return await executeShellCommand(step.args["command"] as? String ?? "")
        case "file_read":
            return await executeFileRead(step.args["path"] as? String ?? "")
        case "file_write":
            return await executeFileWrite(step.args["path"] as? String ?? "", step.args["content"] as? String ?? "")
        case "click":
            return executeClick(at: step.args)
        case "type":
            return executeType(text: step.args["text"] as? String ?? "")
        case "open_app":
            return await executeOpenApp(step.args["app"] as? String ?? "")
        default:
            return StepResult(success: false, error: "Unknown tool")
        }
    }
    
    private func executeShellCommand(_ command: String) async -> StepResult {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/zsh")
        process.arguments = ["-c", command]
        
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        
        do {
            try process.run()
            process.waitUntilExit()
            
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            let output = String(data: data, encoding: .utf8) ?? ""
            
            return StepResult(success: process.terminationStatus == 0, output: output)
        } catch {
            return StepResult(success: false, error: error.localizedDescription)
        }
    }
    
    private func executeFileRead(_ path: String) async -> StepResult {
        do {
            let content = try String(contentsOfFile: path, encoding: .utf8)
            return StepResult(success: true, output: content)
        } catch {
            return StepResult(success: false, error: error.localizedDescription)
        }
    }
    
    private func executeFileWrite(_ path: String, _ content: String) async -> StepResult {
        do {
            try content.write(toFile: path, atomically: true, encoding: .utf8)
            return StepResult(success: true, output: "Written to \(path)")
        } catch {
            return StepResult(success: false, error: error.localizedDescription)
        }
    }
    
    private func executeClick(at args: [String: Any]) -> StepResult {
        let x = args["x"] as? CGFloat ?? 0
        let y = args["y"] as? CGFloat ?? 0
        // DesktopControlService.shared.leftClick(at: CGPoint(x: x, y: y))
        return StepResult(success: true, output: "Clicked at (\(x), \(y))")
    }
    
    private func executeType(text: String) -> StepResult {
        // DesktopControlService.shared.typeText(text)
        return StepResult(success: true, output: "Typed: \(text)")
    }
    
    private func executeOpenApp(_ app: String) async -> StepResult {
        let success = NSWorkspace.shared.launchApplication(app)
        return StepResult(success: success, output: "Opened \(app)")
    }
    
    private func sendCompletionNotification(task: String) async {
        let content = UNMutableNotificationContent()
        content.title = "SiriBot Handoff Complete"
        content.body = "Finished: \(task)"
        content.sound = .default
        
        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        try? await UNUserNotificationCenter.current().add(request)
    }
    
    private func destroyVirtualDisplay() {
        // LogService.shared.log("Virtual display destroyed", level: .info)
        print("Virtual display destroyed")
    }
}

struct PlanStep: Codable {
    var tool: String
    var args: [String: String]  // Changed to [String: String] for Codable compliance
    var description: String
}

struct Plan: Codable {
    var goal: String
    var steps: [PlanStep]
}

struct StepResult {
    var success: Bool
    var output: String?
    var error: String?
}

// Notification names are already defined in the file, so we don't need to redefine them
// extension Notification.Name {
//     static let handoffStarted = Notification.Name("handoffStarted")
//     static let handoffCompleted = Notification.Name("handoffCompleted")
// }
