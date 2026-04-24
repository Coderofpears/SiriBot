import Foundation

class AIPService {
    static let shared = AIPService()
    
    private var currentProvider: String {
        UserDefaults.standard.string(forKey: "APIProvider") ?? "ollama"
    }
    
    private init() {}
    
    func testConnection() async -> Bool {
        let provider = currentProvider
        
        switch provider {
        case "ollama":
            return await testOllama()
        case "openai":
            return await testOpenAI()
        case "anthropic":
            return await testAnthropic()
        default:
            return false
        }
    }
    
    private func testOllama() async -> Bool {
        let baseURL = UserDefaults.standard.string(forKey: "OllamaURL") ?? "http://localhost:11434"
        guard let url = URL(string: "\(baseURL)/api/tags") else {
            return false
        }
        
        do {
            let (_, response) = try await URLSession.shared.data(from: url)
            return (response as? HTTPURLResponse)?.statusCode == 200
        } catch {
            return false
        }
    }
    
    private func testOpenAI() async -> Bool {
        let key = UserDefaults.standard.string(forKey: "OpenAIKey") ?? ""
        return !key.isEmpty && key.hasPrefix("sk-")
    }
    
    private func testAnthropic() async -> Bool {
        let key = UserDefaults.standard.string(forKey: "AnthropicKey") ?? ""
        return !key.isEmpty && key.hasPrefix("sk-ant-")
    }
    
    func chat(_ message: String) async -> String {
        switch currentProvider {
        case "ollama":
            return await chatOllama(message)
        case "openai":
            return await chatOpenAI(message)
        case "anthropic":
            return await chatAnthropic(message)
        default:
            return "Unknown provider"
        }
    }
    
    private func chatOllama(_ message: String) async -> String {
        let baseURL = UserDefaults.standard.string(forKey: "OllamaURL") ?? "http://localhost:11434"
        let model = UserDefaults.standard.string(forKey: "OllamaModel") ?? "llama3.2"
        
        guard let url = URL(string: "\(baseURL)/api/chat") else { return "Invalid URL" }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "model": model,
            "messages": [
                ["role": "system", "content": systemPrompt()],
                ["role": "user", "content": message]
            ],
            "stream": false
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let message = json["message"] as? [String: Any],
               let content = message["content"] as? String {
                return content
            }
        } catch {
            LogService.shared.log("Ollama request failed: \(error)", level: .error)
        }
        
        return "Failed to get response from Ollama"
    }
    
    private func chatOpenAI(_ message: String) async -> String {
        let key = UserDefaults.standard.string(forKey: "OpenAIKey") ?? ""
        guard let url = URL(string: "https://api.openai.com/v1/chat/completions") else { return "Invalid URL" }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "model": "gpt-4o",
            "messages": [
                ["role": "system", "content": systemPrompt()],
                ["role": "user", "content": message]
            ]
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let choices = json["choices"] as? [[String: Any]],
               let first = choices.first,
               let message = first["message"] as? [String: Any],
               let content = message["content"] as? String {
                return content
            }
        } catch {
            LogService.shared.log("OpenAI request failed: \(error)", level: .error)
        }
        
        return "Failed to get response from OpenAI"
    }
    
    private func chatAnthropic(_ message: String) async -> String {
        let key = UserDefaults.standard.string(forKey: "AnthropicKey") ?? ""
        guard let url = URL(string: "https://api.anthropic.com/v1/messages") else { return "Invalid URL" }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(key)", forHTTPHeaderField: "x-api-key")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")
        
        let body: [String: Any] = [
            "model": "claude-sonnet-4-20250514",
            "messages": [
                ["role": "user", "content": message]
            ],
            "max_tokens": 1024
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let content = json["content"] as? [[String: Any]],
               let first = content.first,
               let text = first["text"] as? String {
                return text
            }
        } catch {
            LogService.shared.log("Anthropic request failed: \(error)", level: .error)
        }
        
        return "Failed to get response from Anthropic"
    }
    
    func createPlan(for task: String) async -> Plan {
        let messages: [[String: String]] = [
            ["role": "system", "content": planningSystemPrompt()],
            ["role": "user", "content": "Create a plan for: \(task)"]
        ]
        
        let response = await chatPlanning(messages: messages)
        return parsePlan(from: response, goal: task)
    }
    
    private func chatPlanning(messages: [[String: String]]) async -> String {
        switch currentProvider {
        case "ollama":
            return await chatOllamaPlanning(messages: messages)
        case "openai":
            return await chatOpenAIPlanning(messages: messages)
        default:
            return "{}"
        }
    }
    
    private func chatOllamaPlanning(messages: [[String: String]]) async -> String {
        let baseURL = UserDefaults.standard.string(forKey: "OllamaURL") ?? "http://localhost:11434"
        let model = UserDefaults.standard.string(forKey: "OllamaModel") ?? "llama3.2"
        
        guard let url = URL(string: "\(baseURL)/api/chat") else { return "{}" }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "model": model,
            "messages": messages,
            "stream": false
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let message = json["message"] as? [String: Any],
               let content = message["content"] as? String {
                return content
            }
        } catch {
            return "{}"
        }
        return "{}"
    }
    
    private func chatOpenAIPlanning(messages: [[String: String]]) async -> String {
        let key = UserDefaults.standard.string(forKey: "OpenAIKey") ?? ""
        guard let url = URL(string: "https://api.openai.com/v1/chat/completions") else { return "{}" }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "model": "gpt-4o",
            "messages": messages
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let choices = json["choices"] as? [[String: Any]],
               let first = choices.first,
               let message = first["message"] as? [String: Any],
               let content = message["content"] as? String {
                return content
            }
        } catch {
            return "{}"
        }
        return "{}"
    }
    
    private func parsePlan(from response: String, goal: String) -> Plan {
        // Try to find JSON in response
        var jsonString = response
        if let range = response.range(of: "{"), let endRange = response.range(of: "}", range: range.upperBound..<response.endIndex, options: .backwards) {
            jsonString = String(response[range.lowerBound...endRange.upperBound])
        }
        
        if let data = jsonString.data(using: .utf8),
           let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let goalStr = json["goal"] as? String,
           let stepsData = json["steps"] as? [[String: Any]] {
            let steps = stepsData.compactMap { stepData -> PlanStep? in
                guard let tool = stepData["tool"] as? String else { return nil }
                let args = stepData["args"] as? [String: Any] ?? [:]
                let description = stepData["description"] as? String ?? ""
                return PlanStep(tool: tool, args: args, description: description)
            }
            return Plan(goal: goalStr, steps: steps)
        }
        
        return Plan(goal: goal, steps: [])
    }
    
    private func systemPrompt() -> String {
        """
        You are SiriBot, an intelligent AI assistant that helps users control their Mac.
        
        You can:
        - Execute tasks using tools (shell, file operations, app control)
        - Answer questions and have conversations
        - Plan and execute multi-step workflows
        
        Be helpful, concise, and proactive. When a task requires multiple steps, offer to create a plan.
        """
    }
    
    private func planningSystemPrompt() -> String {
        """
        You are a planning agent. Given a user task, create a step-by-step plan to accomplish it.
        
        Output JSON with this structure:
        {
            "goal": "What we're trying to achieve",
            "steps": [
                {
                    "tool": "tool_name",
                    "args": {"key": "value"},
                    "description": "What this step does"
                }
            ]
        }
        
        Available tools:
        - shell: Execute shell commands (args: command)
        - file_read: Read file contents (args: path)
        - file_write: Write to files (args: path, content)
        - click: Click at coordinates (args: x, y)
        - type: Type text (args: text)
        - open_app: Open an application (args: app)
        """
    }
}
