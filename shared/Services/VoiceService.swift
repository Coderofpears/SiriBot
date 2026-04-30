import Foundation
import AVFoundation
import Speech
import AppKit

class VoiceService: ObservableObject {
    static let shared = VoiceService()
    
    @Published var isListening = false
    @Published var isSpeaking = false
    @Published var transcription = ""
    
    private var audioEngine: AVAudioEngine?
    private var speechRecognizer: SFSpeechRecognizer?
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private var onResult: ((String) -> Void)?
    
    private init() {
        speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    }
    
    func requestPermission(completion: @escaping (Bool) -> Void) {
        AVAudioSession.sharedInstance().requestRecordPermission { granted in
            DispatchQueue.main.async {
                completion(granted)
            }
        }
    }
    
    func startListening(onResult: @escaping (String) -> Void) {
        self.onResult = onResult
        
        guard let recognizer = speechRecognizer, recognizer.isAvailable else {
            // LogService.shared.log("Speech recognizer not available", level: .error)
            print("Speech recognizer not available")
            return
        }
        
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.playAndRecord, mode: .default)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            LogService.shared.log("Audio session setup failed: \(error)", level: .error)
            return
        }
        
        audioEngine = AVAudioEngine()
        guard let audioEngine = audioEngine else { return }
        
        let inputNode = audioEngine.inputNode
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else { return }
        
        recognitionRequest.shouldReportPartialResults = true
        
        recognitionTask = recognizer.recognitionTask(with: recognitionRequest) { [weak self] result, error in
            if let result = result {
                let text = result.bestTranscription.formattedString
                DispatchQueue.main.async {
                    self?.transcription = text
                }
                
                if result.isFinal {
                    self?.stopListening()
                    onResult(text)
                }
            }
            
            if error != nil || result?.isFinal == true {
                self?.stopListening()
            }
        }
        
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            self.recognitionRequest?.append(buffer)
        }
        
        audioEngine.prepare()
        do {
            try audioEngine.start()
            isListening = true
            LogService.shared.log("Voice listening started", level: .info)
        } catch {
            LogService.shared.log("Audio engine start failed: \(error)", level: .error)
        }
    }
    
    func stopListening() {
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        recognitionRequest = nil
        recognitionTask = nil
        audioEngine = nil
        
        DispatchQueue.main.async {
            self.isListening = false
        }
        
        LogService.shared.log("Voice listening stopped", level: .info)
    }
    
    func capture(onResult: @escaping (String) -> Void) {
        // Request permission and start
        SFSpeechRecognizer.requestAuthorization { [weak self] status in
            guard status == .authorized else { return }
            
            DispatchQueue.main.async {
                self?.startListening(onResult: onResult)
            }
        }
    }
    
    func speak(_ text: String) {
        let synthesizer = AVSpeechSynthesizer()
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate
        
        isSpeaking = true
        synthesizer.speak(utterance)
        
        // Simple approach - could use delegate for completion
        DispatchQueue.main.asyncAfter(deadline: .now() + Double(text.count) * 0.05) {
            self.isSpeaking = false
        }
    }
}
