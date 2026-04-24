import Foundation

class SkillsService {
    static let shared = SkillsService()
    
    private var skills: [Skill] = []
    private let storageKey = "SiriBot_Skills"
    
    private init() {
        loadSkills()
    }
    
    func getAllSkills() -> [Skill] {
        return skills
    }
    
    func getEnabledSkills() -> [Skill] {
        return skills.filter { $0.enabled }
    }
    
    func addSkill(_ skill: Skill) {
        skills.append(skill)
        saveSkills()
    }
    
    func removeSkill(_ skill: Skill) {
        skills.removeAll { $0.id == skill.id }
        saveSkills()
    }
    
    func setEnabled(_ skill: Skill, enabled: Bool) {
        if let index = skills.firstIndex(where: { $0.id == skill.id }) {
            skills[index].enabled = enabled
            saveSkills()
        }
    }
    
    func executeSkill(_ skill: Skill, context: [String: Any]) async -> String {
        guard skill.enabled else { return "Skill not enabled" }
        
        // Execute skill code in context
        let result = await executeCode(skill.code, context: context)
        return result
    }
    
    func matchSkill(for prompt: String) -> Skill? {
        for skill in skills where skill.enabled {
            for trigger in skill.prompts {
                if prompt.localizedCaseInsensitiveContains(trigger) {
                    return skill
                }
            }
        }
        return nil
    }
    
    private func loadSkills() {
        if let data = UserDefaults.standard.data(forKey: storageKey),
           let decoded = try? JSONDecoder().decode([Skill].self, from: data) {
            skills = decoded
        } else {
            // Default skills
            skills = [
                Skill(
                    name: "Code Helper",
                    description: "Helps write and debug code",
                    icon: "chevron.left.forwardslash.chevron.right",
                    prompts: ["write code", "debug", "help with", "implement"]
                ),
                Skill(
                    name: "File Organizer",
                    description: "Organizes files on your Mac",
                    icon: "folder",
                    prompts: ["organize files", "sort files", "cleanup"]
                ),
                Skill(
                    name: "Research",
                    description: "Research topics and summarize",
                    icon: "magnifyingglass",
                    prompts: ["research", "find information", "look up"]
                ),
                Skill(
                    name: "Writer",
                    description: "Helps write documents and emails",
                    icon: "doc.text",
                    prompts: ["write", "draft", "compose", "email"]
                )
            ]
            saveSkills()
        }
    }
    
    private func saveSkills() {
        if let encoded = try? JSONEncoder().encode(skills) {
            UserDefaults.standard.set(encoded, forKey: storageKey)
        }
    }
    
    private func executeCode(_ code: String, context: [String: Any]) async -> String {
        // Skill code execution would go here
        // For safety, this would sandbox the execution
        return "Skill executed"
    }
}
