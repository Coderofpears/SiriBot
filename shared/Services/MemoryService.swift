import Foundation
import SQLite3

class MemoryService {
    static let shared = MemoryService()
    
    private var db: OpaquePointer?
    private let dbPath: String
    
    private init() {
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        let siribotDir = appSupport.appendingPathComponent("SiriBot", isDirectory: true)
        try? FileManager.default.createDirectory(at: siribotDir, withIntermediateDirectories: true)
        dbPath = siribotDir.appendingPathComponent("memory.db").path
        
        initDatabase()
    }
    
    private func initDatabase() {
        if sqlite3_open(dbPath, &db) != SQLITE_OK {
            LogService.shared.log("Failed to open database", level: .error)
            return
        }
        
        let createTable = """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                created_at TEXT,
                accessed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                response TEXT,
                intent TEXT,
                timestamp TEXT
            );
        """
        
        var errMsg: UnsafeMutablePointer<CChar>?
        if sqlite3_exec(db, createTable, nil, nil, &errMsg) != SQLITE_OK {
            if let errMsg = errMsg {
                LogService.shared.log("DB error: \(String(cString: errMsg))", level: .error)
                sqlite3_free(errMsg)
            }
        }
    }
    
    func add(_ entry: MemoryEntry) {
        let stmt = "INSERT OR REPLACE INTO memories (key, value, created_at, accessed_at) VALUES (?, ?, ?, ?);"
        var statement: OpaquePointer?
        
        if sqlite3_prepare_v2(db, stmt, -1, &statement, nil) == SQLITE_OK {
            sqlite3_bind_text(statement, 1, (entry.key as NSString).utf8String, -1, SQLITE_TRANSIENT)
            sqlite3_bind_text(statement, 2, (entry.value as NSString).utf8String, -1, SQLITE_TRANSIENT)
            sqlite3_bind_text(statement, 3, (dateToString(entry.createdAt) as NSString).utf8String, -1, SQLITE_TRANSIENT)
            sqlite3_bind_text(statement, 4, (dateToString(entry.accessedAt) as NSString).utf8String, -1, SQLITE_TRANSIENT)
            sqlite3_step(statement)
        }
        sqlite3_finalize(statement)
    }
    
    func get(_ key: String) -> MemoryEntry? {
        let query = "SELECT * FROM memories WHERE key = ?;"
        var statement: OpaquePointer?
        
        if sqlite3_prepare_v2(db, query, -1, &statement, nil) == SQLITE_OK {
            sqlite3_bind_text(statement, 1, (key as NSString).utf8String, -1, SQLITE_TRANSIENT)
            
            if sqlite3_step(statement) == SQLITE_ROW {
                return entryFromStatement(statement)
            }
        }
        sqlite3_finalize(statement)
        return nil
    }
    
    func getAll() -> [MemoryEntry] {
        var entries: [MemoryEntry] = []
        let query = "SELECT * FROM memories ORDER BY accessed_at DESC LIMIT 100;"
        var statement: OpaquePointer?
        
        if sqlite3_prepare_v2(db, query, -1, &statement, nil) == SQLITE_OK {
            while sqlite3_step(statement) == SQLITE_ROW {
                if let entry = entryFromStatement(statement) {
                    entries.append(entry)
                }
            }
        }
        sqlite3_finalize(statement)
        return entries
    }
    
    func search(_ text: String) -> [MemoryEntry] {
        var entries: [MemoryEntry] = []
        let query = "SELECT * FROM memories WHERE key LIKE ? OR value LIKE ? ORDER BY accessed_at DESC;"
        var statement: OpaquePointer?
        
        let searchPattern = "%\(text)%"
        
        if sqlite3_prepare_v2(db, query, -1, &statement, nil) == SQLITE_OK {
            sqlite3_bind_text(statement, 1, (searchPattern as NSString).utf8String, -1, SQLITE_TRANSIENT)
            sqlite3_bind_text(statement, 2, (searchPattern as NSString).utf8String, -1, SQLITE_TRANSIENT)
            
            while sqlite3_step(statement) == SQLITE_ROW {
                if let entry = entryFromStatement(statement) {
                    entries.append(entry)
                }
            }
        }
        sqlite3_finalize(statement)
        return entries
    }
    
    func clearAll() {
        sqlite3_exec(db, "DELETE FROM memories;", nil, nil, nil)
        sqlite3_exec(db, "DELETE FROM interactions;", nil, nil, nil)
        LogService.shared.log("Memory cleared", level: .info)
    }
    
    private func entryFromStatement(_ stmt: OpaquePointer?) -> MemoryEntry? {
        guard let stmt = stmt else { return nil }
        
        guard let keyPtr = sqlite3_column_text(stmt, 1),
              let valuePtr = sqlite3_column_text(stmt, 2),
              let createdPtr = sqlite3_column_text(stmt, 3),
              let accessedPtr = sqlite3_column_text(stmt, 4) else {
            return nil
        }
        
        let key = String(cString: keyPtr)
        let value = String(cString: valuePtr)
        let created = String(cString: createdPtr)
        let accessed = String(cString: accessedPtr)
        
        return MemoryEntry(
            key: key,
            value: value,
            createdAt: stringToDate(created),
            accessedAt: stringToDate(accessed)
        )
    }
    
    private func dateToString(_ date: Date) -> String {
        let formatter = ISO8601DateFormatter()
        return formatter.string(from: date)
    }
    
    private func stringToDate(_ str: String) -> Date {
        let formatter = ISO8601DateFormatter()
        return formatter.date(from: str) ?? Date()
    }
}
