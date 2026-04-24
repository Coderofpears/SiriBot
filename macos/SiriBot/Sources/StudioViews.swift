import SwiftUI

struct StudioMainView: View {
    @StateObject private var conversationVM = ConversationViewModel()
    
    var body: some View {
        HSplitView {
            SidebarView()
            
            ChatView()
        }
        .frame(minWidth: 700, minHeight: 500)
    }
}

struct SidebarView: View {
    var body: some View {
        VStack(spacing: 0) {
            List {
                NavigationLink(destination: ChatView()) {
                    Label("Chat", systemImage: "bubble.left.and.bubble.right")
                }
                NavigationLink(destination: MemoryView()) {
                    Label("Memory", systemImage: "brain")
                }
                NavigationLink(destination: HandoffStatusView()) {
                    Label("Handoff", systemImage: "arrow.triangle.2.circlepath")
                }
                NavigationLink(destination: LogsView()) {
                    Label("Activity", systemImage: "list.bullet.rectangle")
                }
            }
            .listStyle(.sidebar)
            
            Divider()
            
            HStack {
                Circle()
                    .fill(ConversationViewModel().isConnected ? Color.green : Color.red)
                    .frame(width: 8, height: 8)
                Text(ConversationViewModel().isConnected ? "Connected" : "Disconnected")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Spacer()
                if BackgroundService.shared.isListening {
                    Image(systemName: "mic.fill")
                        .foregroundStyle(.green)
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
        }
        .frame(width: 180)
    }
}

struct ChatView: View {
    @StateObject private var vm = ConversationViewModel()
    @State private var inputText = ""
    
    var body: some View {
        VStack(spacing: 0) {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 16) {
                    ForEach(vm.messages) { message in
                        MessageBubble(message: message)
                    }
                }
                .padding()
            }
            
            Divider()
            
            HStack(spacing: 12) {
                Button(action: { vm.toggleRecording() }) {
                    Image(systemName: vm.isRecording ? "stop.circle.fill" : "mic.circle.fill")
                        .font(.title2)
                        .foregroundStyle(vm.isRecording ? .red : .blue)
                }
                .buttonStyle(.plain)
                
                TextField("Ask SiriBot anything...", text: $inputText)
                    .textFieldStyle(.roundedBorder)
                    .onSubmit {
                        sendMessage()
                    }
                
                Button(action: sendMessage) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.title2)
                }
                .buttonStyle(.plain)
                .disabled(inputText.isEmpty)
            }
            .padding()
            .background(Color(NSColor.textBackgroundColor))
        }
    }
    
    private func sendMessage() {
        guard !inputText.isEmpty else { return }
        vm.sendMessage(inputText)
        inputText = ""
    }
}

struct MessageBubble: View {
    let message: Message
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            if message.role == "assistant" {
                Image(systemName: "wave.3.right.circle.fill")
                    .font(.title3)
                    .foregroundStyle(.blue)
            } else {
                Spacer()
            }
            
            VStack(alignment: message.role == "user" ? .trailing : .leading, spacing: 4) {
                Text(message.content)
                    .padding(12)
                    .background(message.role == "user" ? Color.blue : Color.secondary.opacity(0.15))
                    .foregroundStyle(message.role == "user" ? .white : .primary)
                    .cornerRadius(16)
                
                if !message.toolsUsed.isEmpty {
                    HStack(spacing: 4) {
                        ForEach(message.toolsUsed, id: \.self) { tool in
                            Text(tool)
                                .font(.caption2)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.orange.opacity(0.2))
                                .cornerRadius(4)
                        }
                    }
                }
            }
            
            if message.role == "user" {
                Image(systemName: "person.circle.fill")
                    .font(.title3)
                    .foregroundStyle(.gray)
            } else {
                Spacer()
            }
        }
    }
}

struct MemoryView: View {
    @StateObject private var vm = MemoryViewModel()
    
    var body: some View {
        VStack {
            HStack {
                Image(systemName: "magnifyingglass")
                TextField("Search memories...", text: $vm.searchText)
                    .textFieldStyle(.plain)
            }
            .padding()
            .background(Color.secondary.opacity(0.1))
            
            List(vm.memories) { memory in
                VStack(alignment: .leading, spacing: 4) {
                    Text(memory.key)
                        .font(.headline)
                    Text(memory.value)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                    Text(memory.createdAt, style: .relative)
                        .font(.caption2)
                        .foregroundStyle(.tertiary)
                }
                .padding(.vertical, 4)
            }
            .listStyle(.inset)
        }
    }
}

struct HandoffStatusView: View {
    @StateObject private var vm = HandoffViewModel()
    
    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "arrow.triangle.2.circlepath.circle.fill")
                .font(.system(size: 60))
                .foregroundStyle(vm.isActive ? .green : .gray)
            
            Text("Handoff Mode")
                .font(.title.bold())
            
            if vm.isActive {
                Text("SiriBot is working independently...")
                    .foregroundStyle(.secondary)
                
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("Task:")
                        Spacer()
                        Text(vm.currentTask)
                            .foregroundStyle(.secondary)
                    }
                    HStack {
                        Text("Progress:")
                        Spacer()
                        Text("\(Int(vm.progress * 100))%")
                            .foregroundStyle(.secondary)
                    }
                }
                .padding()
                .background(Color.secondary.opacity(0.1))
                .cornerRadius(12)
                .frame(maxWidth: 400)
                
                Button("Stop Handoff") {
                    vm.stop()
                }
                .buttonStyle(.borderedProminent)
                .tint(.red)
            } else {
                Text("Tell SiriBot to handle a complex task and it will open its own desktop to work independently.")
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: 400)
                
                Button("Start Demo") {
                    vm.startDemo()
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
    }
}

struct LogsView: View {
    @StateObject private var vm = LogsViewModel()
    
    var body: some View {
        List(vm.logs) { log in
            HStack {
                Image(systemName: log.icon)
                    .foregroundStyle(log.color)
                VStack(alignment: .leading) {
                    Text(log.message)
                        .font(.system(.body, design: .monospaced))
                    Text(log.timestamp, style: .time)
                        .font(.caption2)
                        .foregroundStyle(.tertiary)
                }
            }
        }
        .listStyle(.plain)
    }
}

struct SettingsView: View {
    @AppStorage("APIProvider") private var apiProvider = "ollama"
    @AppStorage("OllamaURL") private var ollamaURL = "http://localhost:11434"
    @AppStorage("OllamaModel") private var ollamaModel = "llama3.2"
    @AppStorage("OpenAIKey") private var openAIKey = ""
    @AppStorage("EnableVoice") private var enableVoice = true
    @AppStorage("Hotword") private var hotword = "Hey Siri"
    
    var body: some View {
        Form {
            Section("AI Provider") {
                Picker("Provider", selection: $apiProvider) {
                    Text("Ollama").tag("ollama")
                    Text("OpenAI").tag("openai")
                    Text("Anthropic").tag("anthropic")
                }
                
                if apiProvider == "ollama" {
                    TextField("Ollama URL", text: $ollamaURL)
                    TextField("Model", text: $ollamaModel)
                } else {
                    SecureField("API Key", text: $openAIKey)
                }
            }
            
            Section("Voice") {
                Toggle("Enable Voice Control", isOn: $enableVoice)
                TextField("Hotword", text: $hotword)
            }
            
            Section("Memory") {
                Button("Clear Memory") {
                    MemoryService.shared.clearAll()
                }
                .foregroundStyle(.red)
            }
        }
        .formStyle(.grouped)
        .frame(width: 500, height: 400)
    }
}

struct SkillsView: View {
    @StateObject private var vm = SkillsViewModel()
    
    var body: some View {
        VStack {
            List(vm.skills) { skill in
                HStack {
                    Image(systemName: skill.icon)
                        .frame(width: 30)
                        .foregroundStyle(.blue)
                    VStack(alignment: .leading) {
                        Text(skill.name)
                            .font(.headline)
                        Text(skill.description)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                    Toggle("", isOn: Binding(
                        get: { skill.enabled },
                        set: { vm.toggleSkill(skill, enabled: $0) }
                    ))
                }
                .padding(.vertical, 4)
            }
            .listStyle(.inset)
            
            Divider()
            
            HStack {
                Text("\(vm.skills.filter(\.enabled).count) active")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .padding()
        }
    }
}
