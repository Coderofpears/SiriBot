import Foundation
import AVFoundation
import AppKit

class BackgroundService: ObservableObject {
    static let shared = BackgroundService()
    
    @Published var isListening = false
    @Published var lastHotwordDetected = ""
    
    private var audioEngine: AVAudioEngine?
    private var hotwordDetector: HotwordDetector?
    
    private init() {}
    
    func start() {
        guard !isListening else { return }
        
        setupAudioSession()
        startHotwordDetection()
        isListening = true
        
        NotificationCenter.default.post(name: .siribotStatusChanged, object: ["status": "listening"])
        LogService.shared.log("Background listening started", level: .info)
    }
    
    func stop() {
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        isListening = false
        
        NotificationCenter.default.post(name: .siribotStatusChanged, object: ["status": "stopped"])
        LogService.shared.log("Background listening stopped", level: .info)
    }
    
    private func setupAudioSession() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .allowBluetooth])
            try session.setActive(true)
        } catch {
            LogService.shared.log("Audio session setup failed: \(error)", level: .error)
        }
    }
    
    private func startHotwordDetection() {
        hotwordDetector = HotwordDetector { [weak self] hotword in
            self?.handleHotword(hotword)
        }
        hotwordDetector?.start()
    }
    
    private func handleHotword(_ hotword: String) {
        DispatchQueue.main.async {
            self.lastHotwordDetected = hotword
        }
        
        // Trigger notification
        NotificationCenter.default.post(name: .hotwordDetected, object: ["hotword": hotword])
        
        // Show listening indicator
        showListeningNotification()
        
        // Start voice capture
        captureVoiceCommand()
    }
    
    private func showListeningNotification() {
        let content = UNMutableNotificationContent()
        content.title = "Listening..."
        content.body = "Speak your command"
        content.sound = nil
        
        let request = UNNotificationRequest(identifier: "listening", content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request)
    }
    
    private func captureVoiceCommand() {
        VoiceService.shared.capture { [weak self] text in
            self?.processVoiceCommand(text)
        }
    }
    
    private func processVoiceCommand(_ text: String) {
        Task {
            let response = await AIPService.shared.chat(text)
            VoiceService.shared.speak(response)
        }
    }
}

class HotwordDetector {
    private var isRunning = false
    private var onDetection: ((String) -> Void)?
    private var timer: Timer?
    
    init(onDetection: @escaping (String) -> Void) {
        self.onDetection = onDetection
    }
    
    func start() {
        isRunning = true
        let hotword = UserDefaults.standard.string(forKey: "Hotword") ?? "Hey Siri"
        
        // Simple simulation for demo
        timer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            if self?.isRunning == true {
                self?.onDetection?(hotword)
            }
        }
    }
    
    func stop() {
        isRunning = false
        timer?.invalidate()
        timer = nil
    }
}

extension Notification.Name {
    static let hotwordDetected = Notification.Name("hotwordDetected")
    static let siribotStatusChanged = Notification.Name("siribotStatusChanged")
}
