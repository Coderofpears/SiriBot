import AppKit
import SwiftUI

class AppDelegate: NSObject, NSApplicationDelegate {
    private var statusItem: NSStatusItem!
    private var mainWindow: NSWindow?
    private var setupWindow: NSWindow?
    private var handoffWindow: NSWindow?
    private let backgroundService = BackgroundService.shared
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        setupStatusItem()
        
        if shouldRunSetup() {
            showSetupWindow()
        } else {
            showMainWindow()
            backgroundService.start()
        }
    }
    
    func applicationWillTerminate(_ notification: Notification) {
        backgroundService.stop()
    }
    
    private func shouldRunSetup() -> Bool {
        return !UserDefaults.standard.bool(forKey: "SetupCompleted")
    }
    
    private func setupStatusItem() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        
        if let button = statusItem.button {
            button.image = NSImage(systemSymbolName: "wave.3.right", accessibilityDescription: "SiriBot")
            button.action = #selector(statusItemClicked)
            button.target = self
        }
        
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "Open SiriBot Studio", action: #selector(showMainWindow), keyEquivalent: "o"))
        menu.addItem(NSMenuItem(title: "Handoff Mode", action: #selector(enableHandoffMode), keyEquivalent: "h"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Listening", action: #selector(toggleListening), keyEquivalent: "l"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Settings", action: #selector(showSettings), keyEquivalent: ","))
        menu.addItem(NSMenuItem(title: "Skills", action: #selector(showSkills), keyEquivalent: "s"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit SiriBot", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        
        statusItem.menu = menu
    }
    
    @objc private func statusItemClicked() {
        showMainWindow()
    }
    
    func showSetupWindow() {
        if setupWindow != nil { return }
        
        let setupView = SetupView { [weak self] in
            UserDefaults.standard.set(true, forKey: "SetupCompleted")
            self?.setupWindow?.close()
            self?.setupWindow = nil
            self?.showMainWindow()
            self?.backgroundService.start()
        }
        
        setupWindow = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 600, height: 700),
            styleMask: [.titled, .closable],
            backing: .buffered,
            defer: false
        )
        setupWindow?.title = "SiriBot Setup"
        setupWindow?.contentView = NSHostingView(rootView: setupView)
        setupWindow?.center()
        setupWindow?.makeKeyAndOrderFront(nil)
    }
    
    @objc func showMainWindow() {
        if mainWindow == nil {
            mainWindow = NSWindow(
                contentRect: NSRect(x: 0, y: 0, width: 900, height: 600),
                styleMask: [.titled, .closable, .resizable, .miniaturizable],
                backing: .buffered,
                defer: false
            )
            mainWindow?.title = "SiriBot Studio"
            mainWindow?.contentView = NSHostingView(rootView: StudioMainView())
            mainWindow?.minSize = NSSize(width: 700, height: 500)
        }
        mainWindow?.center()
        mainWindow?.makeKeyAndOrderFront(nil)
    }
    
    @objc private func enableHandoffMode() {
        HandoffService.shared.startHandoff(task: "User requested handoff mode") { [weak self] in
            self?.showHandoffWindow()
        }
    }
    
    private func showHandoffWindow() {
        handoffWindow = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 400, height: 300),
            styleMask: [.titled, .closable],
            backing: .buffered,
            defer: false
        )
        handoffWindow?.title = "SiriBot Handoff"
        handoffWindow?.contentView = NSHostingView(rootView: HandoffStatusView())
        handoffWindow?.center()
        handoffWindow?.makeKeyAndOrderFront(nil)
    }
    
    @objc private func toggleListening() {
        if backgroundService.isListening {
            backgroundService.stop()
        } else {
            backgroundService.start()
        }
    }
    
    @objc private func showSettings() {
        let settingsView = SettingsView()
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 500, height: 400),
            styleMask: [.titled, .closable],
            backing: .buffered,
            defer: false
        )
        window.title = "Settings"
        window.contentView = NSHostingView(rootView: settingsView)
        window.center()
        window.makeKeyAndOrderFront(nil)
    }
    
    @objc private func showSkills() {
        let skillsView = SkillsView()
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 600, height: 500),
            styleMask: [.titled, .closable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Skills"
        window.contentView = NSHostingView(rootView: skillsView)
        window.center()
        window.makeKeyAndOrderFront(nil)
    }
}
