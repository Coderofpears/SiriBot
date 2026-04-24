import SwiftUI
import AVFoundation
import ApplicationServices

struct SetupView: View {
    @State private var currentStep = 0
    @State private var apiProvider = "ollama"
    @State private var ollamaURL = "http://localhost:11434"
    @State private var ollamaModel = "llama3.2"
    @State private var openAIKey = ""
    @State private var anthropicKey = ""
    @State private var enableVoice = true
    @State private var enableDesktopControl = false
    @State private var hotword = "Hey Siri"
    @State private var isTestingMicrophone = false
    @State private var microphoneStatus = "Not tested"
    @State private var desktopPermissionGranted = false
    let onComplete: () -> Void
    
    private let steps = ["Welcome", "API Setup", "Voice Settings", "Desktop Control", "Ready"]
    
    var body: some View {
        VStack(spacing: 0) {
            HStack(spacing: 8) {
                ForEach(0..<steps.count, id: \.self) { index in
                    Circle()
                        .fill(index <= currentStep ? Color.accentColor : Color.gray.opacity(0.3))
                        .frame(width: 10, height: 10)
                    if index < steps.count - 1 {
                        Rectangle()
                            .fill(index < currentStep ? Color.accentColor : Color.gray.opacity(0.3))
                            .frame(height: 2)
                    }
                }
            }
            .padding(.horizontal, 40)
            .padding(.top, 30)
            
            Text(steps[currentStep])
                .font(.title2.bold())
                .padding(.top, 20)
            
            Spacer()
            
            Group {
                switch currentStep {
                case 0: welcomeStep
                case 1: apiSetupStep
                case 2: voiceStep
                case 3: desktopStep
                case 4: readyStep
                default: EmptyView()
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .animation(.easeInOut, value: currentStep)
            
            Divider()
            
            HStack {
                if currentStep > 0 {
                    Button("Back") {
                        withAnimation { currentStep -= 1 }
                    }
                    .buttonStyle(.bordered)
                }
                Spacer()
                if currentStep < steps.count - 1 {
                    Button("Continue") {
                        withAnimation { currentStep += 1 }
                    }
                    .buttonStyle(.borderedProminent)
                } else {
                    Button("Get Started") {
                        saveSettings()
                        onComplete()
                    }
                    .buttonStyle(.borderedProminent)
                }
            }
            .padding(.horizontal, 40)
            .padding(.vertical, 20)
        }
        .frame(width: 600, height: 700)
    }
    
    private var welcomeStep: some View {
        VStack(spacing: 24) {
            Image(systemName: "wave.3.right.circle.fill")
                .font(.system(size: 80))
                .foregroundStyle(.blue.gradient)
            
            Text("Welcome to SiriBot")
                .font(.largeTitle.bold())
            
            Text("Your open-source, local-first AI assistant that can control your Mac.")
                .font(.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .frame(maxWidth: 400)
            
            VStack(alignment: .leading, spacing: 12) {
                FeatureRow(icon: "cpu", title: "Local Models", desc: "Run AI locally with Ollama")
                FeatureRow(icon: "mic.fill", title: "Voice Control", desc: "Talk to SiriBot hands-free")
                FeatureRow(icon: "desktopcomputer", title: "Desktop Control", desc: "Automate tasks on your Mac")
                FeatureRow(icon: "arrow.triangle.2.circlepath", title: "Handoff", desc: "AI works independently")
            }
            .padding(.top, 20)
        }
        .padding()
    }
    
    private var apiSetupStep: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Configure AI Provider")
                .font(.title3.bold())
            
            Picker("Provider", selection: $apiProvider) {
                Text("Ollama (Local)").tag("ollama")
                Text("OpenAI").tag("openai")
                Text("Anthropic").tag("anthropic")
            }
            .pickerStyle(.segmented)
            
            if apiProvider == "ollama" {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Ollama URL")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    TextField("http://localhost:11434", text: $ollamaURL)
                        .textFieldStyle(.roundedBorder)
                    
                    Text("Model")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    TextField("llama3.2", text: $ollamaModel)
                        .textFieldStyle(.roundedBorder)
                }
            } else if apiProvider == "openai" {
                VStack(alignment: .leading, spacing: 8) {
                    Text("API Key")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    SecureField("sk-...", text: $openAIKey)
                        .textFieldStyle(.roundedBorder)
                }
            } else {
                VStack(alignment: .leading, spacing: 8) {
                    Text("API Key")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    SecureField("sk-ant-...", text: $anthropicKey)
                        .textFieldStyle(.roundedBorder)
                }
            }
            
            Link("Download Ollama", destination: URL(string: "https://ollama.ai")!)
                .font(.caption)
        }
        .padding(.horizontal, 40)
    }
    
    private var voiceStep: some View {
        VStack(alignment: .leading, spacing: 20) {
            Toggle("Enable Voice Control", isOn: $enableVoice)
                .font(.title3.bold())
            
            if enableVoice {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Hotword")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    TextField("Hey Siri", text: $hotword)
                        .textFieldStyle(.roundedBorder)
                    
                    HStack {
                        Button(isTestingMicrophone ? "Testing..." : "Test Microphone") {
                            testMicrophone()
                        }
                        .buttonStyle(.bordered)
                        .disabled(isTestingMicrophone)
                        
                        Text(microphoneStatus)
                            .font(.caption)
                            .foregroundStyle(microphoneStatus == "Ready" ? .green : .secondary)
                    }
                }
            }
        }
        .padding(.horizontal, 40)
    }
    
    private var desktopStep: some View {
        VStack(alignment: .leading, spacing: 20) {
            Toggle("Enable Desktop Control", isOn: $enableDesktopControl)
                .font(.title3.bold())
            
            if enableDesktopControl {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Desktop Control allows SiriBot to:")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        ControlFeature(icon: "mouse.fill", text: "Move and click the mouse")
                        ControlFeature(icon: "keyboard.fill", text: "Type and press keys")
                        ControlFeature(icon: "window.fill", text: "Control app windows")
                        ControlFeature(icon: "doc.fill", text: "Interact with UI elements")
                    }
                    
                    HStack {
                        Button("Grant Accessibility Permission") {
                            requestAccessibilityPermission()
                        }
                        .buttonStyle(.bordered)
                        
                        Image(systemName: desktopPermissionGranted ? "checkmark.circle.fill" : "xmark.circle")
                            .foregroundStyle(desktopPermissionGranted ? .green : .red)
                    }
                }
            }
        }
        .padding(.horizontal, 40)
    }
    
    private var readyStep: some View {
        VStack(spacing: 24) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 60))
                .foregroundStyle(.green)
            
            Text("You're All Set!")
                .font(.title.bold())
            
            VStack(alignment: .leading, spacing: 8) {
                SummaryRow(title: "Provider", value: apiProvider)
                SummaryRow(title: "Voice", value: enableVoice ? "Enabled" : "Disabled")
                SummaryRow(title: "Desktop Control", value: enableDesktopControl ? "Enabled" : "Disabled")
            }
            .padding()
            .background(Color.secondary.opacity(0.1))
            .cornerRadius(12)
            .frame(maxWidth: 300)
            
            Text("Click 'Get Started' to launch SiriBot")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }
    
    private func testMicrophone() {
        isTestingMicrophone = true
        AVCaptureDevice.requestAccess(for: .audio) { granted in
            DispatchQueue.main.async {
                isTestingMicrophone = false
                microphoneStatus = granted ? "Ready" : "Access Denied"
            }
        }
    }
    
    private func requestAccessibilityPermission() {
        let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true]
        desktopPermissionGranted = AXIsProcessTrustedWithOptions(options as CFDictionary)
    }
    
    private func saveSettings() {
        UserDefaults.standard.set(apiProvider, forKey: "APIProvider")
        UserDefaults.standard.set(ollamaURL, forKey: "OllamaURL")
        UserDefaults.standard.set(ollamaModel, forKey: "OllamaModel")
        UserDefaults.standard.set(openAIKey, forKey: "OpenAIKey")
        UserDefaults.standard.set(anthropicKey, forKey: "AnthropicKey")
        UserDefaults.standard.set(enableVoice, forKey: "EnableVoice")
        UserDefaults.standard.set(enableDesktopControl, forKey: "EnableDesktopControl")
        UserDefaults.standard.set(hotword, forKey: "Hotword")
    }
}

struct FeatureRow: View {
    let icon: String
    let title: String
    let desc: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .frame(width: 24)
                .foregroundStyle(.blue)
            VStack(alignment: .leading) {
                Text(title).font(.headline)
                Text(desc).font(.caption).foregroundStyle(.secondary)
            }
        }
    }
}

struct ControlFeature: View {
    let icon: String
    let text: String
    
    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: icon).frame(width: 20)
            Text(text).font(.caption)
        }
    }
}

struct SummaryRow: View {
    let title: String
    let value: String
    
    var body: some View {
        HStack {
            Text(title)
            Spacer()
            Text(value).foregroundStyle(.secondary)
        }
    }
}
