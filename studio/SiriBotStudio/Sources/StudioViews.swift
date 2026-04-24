import SwiftUI
import Combine

struct StudioContentView: View {
    @StateObject private var vm = StudioViewModel()
    @State private var selectedSidebarItem: SidebarItem? = .conversations
    
    var body: some View {
        HSplitView {
            // Sidebar
            List(selection: $selectedSidebarItem) {
                Section("Workspace") {
                    ForEach(SidebarItem.workspaceItems) { item in
                        Label(item.title, systemImage: item.icon)
                            .tag(item)
                    }
                }
                
                Section("Tools") {
                    ForEach(SidebarItem.toolItems) { item in
                        Label(item.title, systemImage: item.icon)
                            .tag(item)
                    }
                }
                
                Section("Resources") {
                    ForEach(SidebarItem.resourceItems) { item in
                        Label(item.title, systemImage: item.icon)
                            .tag(item)
                    }
                }
            }
            .listStyle(.sidebar)
            .frame(width: 200)
            
            // Main content
            Group {
                switch selectedSidebarItem {
                case .conversations:
                    ConversationsView()
                case .memory:
                    StudioMemoryView()
                case .skills:
                    StudioSkillsView()
                case .handoff:
                    StudioHandoffView()
                case .logs:
                    StudioLogsView()
                case .projects:
                    ProjectsView()
                case .playground:
                    PlaygroundView()
                case .shortcuts:
                    ShortcutsView()
                case .settings:
                    StudioSettingsView()
                case .help:
                    HelpView()
                case .none:
                    Text("Select an item")
                }
            }
            .frame(minWidth: 500)
        }
        .frame(minWidth: 700, minHeight: 500)
        .toolbar {
            ToolbarItemGroup(placement: .primaryAction) {
                Button(action: { vm.toggleListening() }) {
                    Image(systemName: vm.isListening ? "mic.fill" : "mic")
                }
                .help(vm.isListening ? "Stop listening" : "Start listening")
            }
        }
    }
}

enum SidebarItem: Hashable, Identifiable {
    case conversations, memory, skills, handoff, logs
    case projects, playground, shortcuts
    case settings, help
    
    var id: String {
        switch self {
        case .conversations: return "conversations"
        case .memory: return "memory"
        case .skills: return "skills"
        case .handoff: return "handoff"
        case .logs: return "logs"
        case .projects: return "projects"
        case .playground: return "playground"
        case .shortcuts: return "shortcuts"
        case .settings: return "settings"
        case .help: return "help"
        }
    }
    
    var title: String {
        switch self {
        case .conversations: return "Conversations"
        case .memory: return "Memory"
        case .skills: return "Skills"
        case .handoff: return "Handoff"
        case .logs: return "Activity"
        case .projects: return "Projects"
        case .playground: return "Playground"
        case .shortcuts: return "Shortcuts"
        case .settings: return "Settings"
        case .help: return "Help"
        }
    }
    
    var icon: String {
        switch self {
        case .conversations: return "bubble.left.and.bubble.right"
        case .memory: return "brain"
        case .skills: return "wand.and.stars"
        case .handoff: return "arrow.triangle.2.circlepath"
        case .logs: return "list.bullet.rectangle"
        case .projects: return "folder"
        case .playground: return "puzzlepiece"
        case .shortcuts: return "command.square"
        case .settings: return "gear"
        case .help: return "questionmark.circle"
        }
    }
    
    static let workspaceItems: [SidebarItem] = [.conversations, .memory, .skills, .handoff, .logs]
    static let toolItems: [SidebarItem] = [.projects, .playground, .shortcuts]
    static let resourceItems: [SidebarItem] = [.settings, .help]
}

struct ConversationsView: View {
    @StateObject private var vm = ConversationsViewModel()
    @State private var selectedConversation: Conversation?
    
    var body: some View {
        HSplitView {
            // Conversation list
            List(selection: $selectedConversation) {
                ForEach(vm.conversations) { conv in
                    ConversationRow(conversation: conv)
                        .tag(conv)
                }
            }
            .listStyle(.sidebar)
            .frame(width: 250)
            
            // Conversation detail
            if let conv = selectedConversation {
                ConversationDetailView(conversation: conv)
            } else {
                ContentUnavailableView(
                    "Select a Conversation",
                    systemImage: "bubble.left.and.bubble.right",
                    description: Text("Choose a conversation from the list")
                )
            }
        }
    }
}

struct ConversationRow: View {
    let conversation: Conversation
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(conversation.title)
                .font(.headline)
                .lineLimit(1)
            Text(conversation.lastMessage)
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(1)
            Text(conversation.timestamp, style: .relative)
                .font(.caption2)
                .foregroundStyle(.tertiary)
        }
        .padding(.vertical, 4)
    }
}

struct ConversationDetailView: View {
    let conversation: Conversation
    @State private var inputText = ""
    
    var body: some View {
        VStack(spacing: 0) {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 12) {
                    ForEach(conversation.messages) { msg in
                        MessageView(message: msg)
                    }
                }
                .padding()
            }
            
            Divider()
            
            HStack {
                TextField("Message...", text: $inputText)
                    .textFieldStyle(.roundedBorder)
                    .onSubmit {
                        sendMessage()
                    }
                Button(action: sendMessage) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.title2)
                }
                .disabled(inputText.isEmpty)
            }
            .padding()
        }
    }
    
    private func sendMessage() {
        guard !inputText.isEmpty else { return }
        inputText = ""
    }
}

struct MessageView: View {
    let message: Message
    
    var body: some View {
        HStack(alignment: .top, spacing: 8) {
            if message.role == "assistant" {
                Image(systemName: "wave.3.right.circle.fill")
                    .foregroundStyle(.blue)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(message.content)
                    .padding(10)
                    .background(message.role == "user" ? Color.blue : Color.secondary.opacity(0.15))
                    .foregroundStyle(message.role == "user" ? .white : .primary)
                    .cornerRadius(12)
                
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
            
            Spacer()
        }
    }
}

struct StudioMemoryView: View {
    @StateObject private var vm = MemoryViewModel()
    @State private var searchText = ""
    
    var body: some View {
        VStack {
            HStack {
                Image(systemName: "magnifyingglass")
                TextField("Search memories...", text: $searchText)
                    .textFieldStyle(.plain)
                Spacer()
            }
            .padding()
            .background(Color.secondary.opacity(0.1))
            
            if #available(macOS 14.0, *) {
                Table(vm.memories) {
                    TableColumn("Key") { entry in Text(entry.key) }
                    TableColumn("Value") { entry in Text(entry.value).lineLimit(1) }
                    TableColumn("Created") { entry in Text(entry.createdAt, style: .date) }
                    TableColumn("Accessed") { entry in Text(entry.accessedAt, style: .relative) }
                }
            } else {
                List(vm.memories) { entry in
                    VStack(alignment: .leading) {
                        Text(entry.key).font(.headline)
                        Text(entry.value).font(.caption).foregroundStyle(.secondary)
                    }
                }
            }
        }
    }
}

struct StudioSkillsView: View {
    @StateObject private var vm = SkillsViewModel()
    @State private var selectedSkill: Skill?
    
    var body: some View {
        HSplitView {
            List(vm.skills, selection: $selectedSkill) { skill in
                SkillRowView(skill: skill, onToggle: { enabled in
                    vm.toggleSkill(skill, enabled: enabled)
                })
                .tag(skill)
            }
            .listStyle(.sidebar)
            .frame(width: 250)
            
            if let skill = selectedSkill {
                SkillDetailView(skill: skill)
            } else {
                ContentUnavailableView(
                    "Select a Skill",
                    systemImage: "wand.and.stars",
                    description: Text("Choose a skill to view details")
                )
            }
        }
    }
}

struct SkillRowView: View {
    let skill: Skill
    let onToggle: (Bool) -> Void
    
    var body: some View {
        HStack {
            Image(systemName: skill.icon)
                .frame(width: 24)
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
                set: { onToggle($0) }
            ))
            .labelsHidden()
        }
    }
}

struct SkillDetailView: View {
    let skill: Skill
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: skill.icon)
                    .font(.largeTitle)
                    .foregroundStyle(.blue)
                VStack {
                    Text(skill.name)
                        .font(.title2.bold())
                    Text(skill.description)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                Toggle("Enabled", isOn: .constant(skill.enabled))
            }
            
            Divider()
            
            Text("Triggers")
                .font(.headline)
            FlowLayout(spacing: 8) {
                ForEach(skill.prompts, id: \.self) { prompt in
                    Text(prompt)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(Color.secondary.opacity(0.2))
                        .cornerRadius(8)
                }
            }
            
            Divider()
            
            Text("Code")
                .font(.headline)
            Text(skill.code.isEmpty ? "// No custom code" : skill.code)
                .font(.system(.body, design: .monospaced))
                .padding()
                .background(Color.secondary.opacity(0.1))
                .cornerRadius(8)
            
            Spacer()
        }
        .padding()
    }
}

struct FlowLayout: Layout {
    var spacing: CGFloat = 8
    
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = FlowResult(in: proposal.width ?? 0, subviews: subviews, spacing: spacing)
        return result.size
    }
    
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(in: bounds.width, subviews: subviews, spacing: spacing)
        for (index, subview) in subviews.enumerated() {
            subview.place(at: CGPoint(x: bounds.minX + result.positions[index].x, y: bounds.minY + result.positions[index].y), proposal: .unspecified)
        }
    }
    
    struct FlowResult {
        var size: CGSize = .zero
        var positions: [CGPoint] = []
        
        init(in maxWidth: CGFloat, subviews: Subviews, spacing: CGFloat) {
            var x: CGFloat = 0
            var y: CGFloat = 0
            var maxH: CGFloat = 0
            
            for subview in subviews {
                let size = subview.sizeThatFits(.unspecified)
                if x + size.width > maxWidth && x > 0 {
                    x = 0
                    y += maxH + spacing
                    maxH = 0
                }
                positions.append(CGPoint(x: x, y: y))
                maxH = max(maxH, size.height)
                x += size.width + spacing
            }
            
            self.size = CGSize(width: maxWidth, height: y + maxH)
        }
    }
}

struct StudioHandoffView: View {
    @StateObject private var vm = HandoffViewModel()
    
    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "arrow.triangle.2.circlepath.circle.fill")
                .font(.system(size: 80))
                .foregroundStyle(vm.isActive ? .green : .gray)
            
            Text("Handoff Mode")
                .font(.largeTitle.bold())
            
            if vm.isActive {
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("Task:")
                            .font(.headline)
                        Spacer()
                        Text(vm.currentTask)
                            .foregroundStyle(.secondary)
                    }
                    ProgressView(value: vm.progress)
                    HStack {
                        Text("\(Int(vm.progress * 100))%")
                        Spacer()
                        Text("\(vm.completedSteps)/\(max(vm.totalSteps, 1)) steps")
                    }
                    .font(.caption)
                    .foregroundStyle(.secondary)
                }
                .padding()
                .background(Color.secondary.opacity(0.1))
                .cornerRadius(12)
                .frame(maxWidth: 500)
                
                Button("Stop Handoff") {
                    vm.stop()
                }
                .buttonStyle(.borderedProminent)
                .tint(.red)
            } else {
                Text("Handoff allows SiriBot to work independently on your Mac.\nIt can open its own desktop and complete tasks while you do other work.")
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

struct StudioLogsView: View {
    @StateObject private var vm = LogsViewModel()
    @State private var filterLevel: LogLevel?
    @State private var searchText = ""
    
    var body: some View {
        VStack {
            HStack {
                Picker("Level", selection: $filterLevel) {
                    Text("All").tag(nil as LogLevel?)
                    Text("Info").tag(LogLevel.info as LogLevel?)
                    Text("Warning").tag(LogLevel.warning as LogLevel?)
                    Text("Error").tag(LogLevel.error as LogLevel?)
                }
                .pickerStyle(.segmented)
                
                Spacer()
                
                TextField("Search", text: $searchText)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 200)
            }
            .padding()
            .background(Color.secondary.opacity(0.1))
            
            List {
                ForEach(vm.filteredLogs(level: filterLevel, search: searchText)) { log in
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
            }
            .listStyle(.plain)
        }
    }
}

struct ProjectsView: View {
    var body: some View {
        ContentUnavailableView(
            "Projects",
            systemImage: "folder",
            description: Text("Manage your AI projects and workflows")
        )
    }
}

struct PlaygroundView: View {
    @State private var input = ""
    @State private var output = ""
    @State private var isLoading = false
    
    var body: some View {
        HSplitView {
            VStack(alignment: .leading) {
                Text("Input")
                    .font(.headline)
                    .padding(.horizontal)
                    .padding(.top)
                TextEditor(text: $input)
                    .font(.system(.body, design: .monospaced))
                    .padding(8)
            }
            .background(Color.secondary.opacity(0.1))
            
            VStack {
                HStack {
                    Spacer()
                    Button("Run") {
                        runCode()
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(isLoading || input.isEmpty)
                }
                .padding()
                
                Divider()
                
                Text("Output")
                    .font(.headline)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal)
                
                ScrollView {
                    Text(output.isEmpty ? "Output will appear here..." : output)
                        .font(.system(.body, design: .monospaced))
                        .foregroundStyle(output.isEmpty ? .secondary : .primary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                }
            }
        }
    }
    
    private func runCode() {
        isLoading = true
        Task {
            output = await AIPService.shared.chat(input)
            isLoading = false
        }
    }
}

struct ShortcutsView: View {
    @StateObject private var vm = ShortcutsViewModel()
    
    var body: some View {
        VStack {
            HStack {
                Text("Apple Shortcuts Integration")
                    .font(.title2.bold())
                Spacer()
                Button("Add Shortcut") {
                    vm.showAddSheet = true
                }
            }
            .padding()
            
            List {
                ForEach(vm.shortcuts) { shortcut in
                    HStack {
                        VStack(alignment: .leading) {
                            Text(shortcut.name)
                                .font(.headline)
                            Text("Trigger: \"\(shortcut.phrase)\"")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        Spacer()
                        Toggle("", isOn: Binding(
                            get: { shortcut.enabled },
                            set: { vm.toggleShortcut(shortcut, enabled: $0) }
                        ))
                        .labelsHidden()
                    }
                }
            }
            .listStyle(.plain)
        }
        .sheet(isPresented: $vm.showAddSheet) {
            AddShortcutView(vm: vm)
        }
    }
}

struct StudioSettingsView: View {
    @AppStorage("APIProvider") private var apiProvider = "ollama"
    @AppStorage("OllamaURL") private var ollamaURL = "http://localhost:11434"
    @AppStorage("OllamaModel") private var ollamaModel = "llama3.2"
    @AppStorage("GitHubToken") private var githubToken = ""
    
    var body: some View {
        Form {
            Section("AI Provider") {
                Picker("Provider", selection: $apiProvider) {
                    Text("Ollama (Local)").tag("ollama")
                    Text("OpenAI").tag("openai")
                    Text("Anthropic").tag("anthropic")
                }
                
                if apiProvider == "ollama" {
                    TextField("URL", text: $ollamaURL)
                    TextField("Model", text: $ollamaModel)
                }
            }
            
            Section("GitHub") {
                SecureField("Personal Access Token", text: $githubToken)
                Button("Create & Push to GitHub") {
                    createGitHubRepo()
                }
            }
            
            Section("About") {
                HStack {
                    Text("Version")
                    Spacer()
                    Text("1.0.0")
                        .foregroundStyle(.secondary)
                }
            }
        }
        .formStyle(.grouped)
    }
    
    private func createGitHubRepo() {
        Task {
            do {
                let token = githubToken
                let repo = try await GitHubService.shared.createRepo(
                    name: "SiriBot",
                    description: "Open-source AI assistant for macOS",
                    isPrivate: false,
                    token: token
                )
                try await GitHubService.shared.pushToRepo(
                    repoName: repo.full_name,
                    repoURL: repo.html_url,
                    localPath: "."
                )
            } catch {
                LogService.shared.log("GitHub error: \(error)", level: .error)
            }
        }
    }
}

struct HelpView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("SiriBot Studio Help")
                    .font(.largeTitle.bold())
                
                Text("Getting Started")
                    .font(.title2.bold())
                Text("SiriBot is an open-source AI assistant that runs locally on your Mac. Get started by configuring your AI provider in Settings.")
                
                Text("Voice Commands")
                    .font(.title2.bold())
                Text("Enable voice control and say 'Hey Siri' followed by your command to control SiriBot hands-free.")
                
                Text("Handoff Mode")
                    .font(.title2.bold())
                Text("Tell SiriBot to handle a complex task and it will open its own desktop to work independently. You'll receive a notification when it's done.")
                
                Text("Skills")
                    .font(.title2.bold())
                Text("Skills extend SiriBot's capabilities. Enable or disable skills in the Skills panel, or create custom skills with code.")
                
                Link("View Full Documentation", destination: URL(string: "https://github.com/siribot/siribot")!)
            }
            .padding()
        }
    }
}

struct AddShortcutView: View {
    @ObservedObject var vm: ShortcutsViewModel
    @State private var name = ""
    @State private var phrase = ""
    @State private var action = ""
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack {
            Text("Add Apple Shortcut")
                .font(.title2.bold())
            Form {
                TextField("Name", text: $name)
                TextField("Trigger Phrase", text: $phrase)
                TextField("Action", text: $action)
            }
            HStack {
                Button("Cancel") { dismiss() }
                Button("Add") {
                    let shortcut = ShortcutService.Shortcut(
                        id: UUID(),
                        name: name,
                        phrase: phrase,
                        action: action,
                        enabled: true
                    )
                    vm.addShortcut(shortcut)
                    dismiss()
                }
                .buttonStyle(.borderedProminent)
                .disabled(name.isEmpty || phrase.isEmpty)
            }
        }
        .padding()
        .frame(width: 400)
    }
}
