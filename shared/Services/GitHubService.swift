import Foundation

class GitHubService {
    static let shared = GitHubService()
    
    private let ghAPI = "https://api.github.com"
    
    private init() {}
    
    struct GitHubRepo: Codable {
        let name: String
        let full_name: String
        let html_url: String
        let description: String?
        let isPrivate: Bool
        let default_branch: String
        
        enum CodingKeys: String, CodingKey {
            case name
            case full_name
            case html_url
            case description
            case isPrivate = "private"
            case default_branch
        }
    }
    
    func createRepo(
        name: String,
        description: String,
        isPrivate: Bool,
        token: String
    ) async throws -> GitHubRepo {
        guard let url = URL(string: "\(ghAPI)/user/repos") else {
            throw GitHubError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
        
        let body: [String: Any] = [
            "name": name,
            "description": description,
            "private": isPrivate,
            "auto_init": true,
            "gitignore_template": "macOS"
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw GitHubError.invalidResponse
        }
        
        guard httpResponse.statusCode == 201 else {
            if let error = try? JSONDecoder().decode(GitHubErrorResponse.self, from: data) {
                throw GitHubError.apiError(error.message)
            }
            throw GitHubError.createFailed
        }
        
        return try JSONDecoder().decode(GitHubRepo.self, from: data)
    }
    
    func pushToRepo(
        repoName: String,
        repoURL: String,
        localPath: String,
        branch: String = "main"
    ) async throws {
        let git = GitService()
        
        // Initialize git if needed
        try await git.init(at: localPath)
        
        // Configure remote
        let remoteURL = "https://github.com/\(repoName).git"
        try await git.addRemote(name: "origin", url: remoteURL, at: localPath)
        
        // Add all files
        try await git.addAll(at: localPath)
        
        // Initial commit
        try await git.commit(message: "Initial SiriBot commit", at: localPath)
        
        // Push
        try await git.push(remote: "origin", branch: branch, at: localPath)
        
        LogService.shared.log("Pushed to \(remoteURL)", level: .success)
    }
    
    func getAuthToken() -> String? {
        if let token = ProcessInfo.processInfo.environment["GITHUB_TOKEN"] {
            return token
        }
        return UserDefaults.standard.string(forKey: "GitHubToken")
    }
    
    func setAuthToken(_ token: String) {
        UserDefaults.standard.set(token, forKey: "GitHubToken")
    }
}

enum GitHubError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case createFailed
    case apiError(String)
    case notAuthenticated
    
    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid GitHub URL"
        case .invalidResponse: return "Invalid response from GitHub"
        case .createFailed: return "Failed to create repository"
        case .apiError(let msg): return "GitHub API error: \(msg)"
        case .notAuthenticated: return "Not authenticated with GitHub"
        }
    }
}

struct GitHubErrorResponse: Codable {
    let message: String
    let errors: [GitHubAPIError]?
}

struct GitHubAPIError: Codable {
    let resource: String
    let field: String
    let code: String
}

class GitService {
    func init(at path: String) async throws {
        let result = try await runCommand("/usr/bin/git", args: ["init"], at: path)
        guard result.exitCode == 0 else { throw GitError.initFailed }
    }
    
    func addRemote(name: String, url: String, at path: String) async throws {
        let result = try await runCommand("/usr/bin/git", args: ["remote", "add", name, url], at: path)
        guard result.exitCode == 0 else { throw GitError.remoteFailed }
    }
    
    func addAll(at path: String) async throws {
        let result = try await runCommand("/usr/bin/git", args: ["add", "."], at: path)
        guard result.exitCode == 0 else { throw GitError.addFailed }
    }
    
    func commit(message: String, at path: String) async throws {
        let result = try await runCommand("/usr/bin/git", args: ["commit", "-m", message], at: path)
        guard result.exitCode == 0 else { throw GitError.commitFailed }
    }
    
    func push(remote: String, branch: String, at path: String) async throws {
        let result = try await runCommand("/usr/bin/git", args: ["push", "-u", remote, branch], at: path)
        guard result.exitCode == 0 else { throw GitError.pushFailed }
    }
    
    private func runCommand(_ command: String, args: [String], at path: String) async throws -> CommandResult {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: command)
        process.arguments = args
        process.currentDirectoryPath = path
        
        let outputPipe = Pipe()
        let errorPipe = Pipe()
        process.standardOutput = outputPipe
        process.standardError = errorPipe
        
        try process.run()
        process.waitUntilExit()
        
        let outputData = outputPipe.fileHandleForReading.readDataToEndOfFile()
        let errorData = errorPipe.fileHandleForReading.readDataToEndOfFile()
        
        return CommandResult(
            exitCode: Int(process.terminationStatus),
            output: String(data: outputData, encoding: .utf8) ?? "",
            error: String(data: errorData, encoding: .utf8) ?? ""
        )
    }
}

struct CommandResult {
    let exitCode: Int
    let output: String
    let error: String
}

enum GitError: Error, LocalizedError {
    case initFailed
    case remoteFailed
    case addFailed
    case commitFailed
    case pushFailed
    
    var errorDescription: String? {
        switch self {
        case .initFailed: return "Git init failed"
        case .remoteFailed: return "Failed to add remote"
        case .addFailed: return "Git add failed"
        case .commitFailed: return "Git commit failed"
        case .pushFailed: return "Git push failed"
        }
    }
}
