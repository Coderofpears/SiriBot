import Foundation
import AppKit
import ApplicationServices

class DesktopControlService {
    static let shared = DesktopControlService()
    
    private var isEnabled = false
    
    private init() {}
    
    func enable() {
        let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true] as CFDictionary
        isEnabled = AXIsProcessTrustedWithOptions(options)
        
        if isEnabled {
            LogService.shared.log("Desktop control enabled", level: .success)
        } else {
            LogService.shared.log("Desktop control permission denied", level: .warning)
        }
    }
    
    func isAccessibilityEnabled() -> Bool {
        return AXIsProcessTrusted()
    }
    
    // MARK: - Mouse Control
    
    func moveMouse(to point: CGPoint) {
        CGEvent(postAt: .nextAppEvent, at: CGEvent(locations: [point])?.tap(-.cghidEventTap))?.post(tap: .cghidEventTap)
    }
    
    func leftClick(at point: CGPoint) {
        let downEvent = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left)
        let upEvent = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left)
        downEvent?.post(tap: .cghidEventTap)
        upEvent?.post(tap: .cghidEventTap)
    }
    
    func rightClick(at point: CGPoint) {
        let downEvent = CGEvent(mouseEventSource: nil, mouseType: .rightMouseDown, mouseCursorPosition: point, mouseButton: .right)
        let upEvent = CGEvent(mouseEventSource: nil, mouseType: .rightMouseUp, mouseCursorPosition: point, mouseButton: .right)
        downEvent?.post(tap: .cghidEventTap)
        upEvent?.post(tap: .cghidEventTap)
    }
    
    func doubleClick(at point: CGPoint) {
        leftClick(at: point)
        leftClick(at: point)
    }
    
    func scroll(delta: CGFloat, at point: CGPoint) {
        let event = CGEvent(scrollWheelEvent2Source: nil, units: .pixelDelta, wheelCount: 1, wheel1: Int32(delta), wheel2: 0, wheel3: 0)
        event?.post(tap: .cghidEventTap)
    }
    
    // MARK: - Keyboard Control
    
    func pressKey(_ keyCode: CGKeyCode, modifiers: CGEventFlags = []) {
        let downEvent = CGEvent(keyboardEventSource: nil, virtualKey: keyCode, keyDown: true)
        let upEvent = CGEvent(keyboardEventSource: nil, virtualKey: keyCode, keyDown: false)
        downEvent?.flags = modifiers
        upEvent?.flags = modifiers
        downEvent?.post(tap: .cghidEventTap)
        upEvent?.post(tap: .cghidEventTap)
    }
    
    func typeText(_ text: String) {
        for char in text.unicodeScalars {
            let keyCode = keyCodeForCharacter(char)
            pressKey(keyCode)
        }
    }
    
    private func keyCodeForCharacter(_ char: Unicode.Scalar) -> CGKeyCode {
        // Simplified - would need proper implementation
        return CGKeyCode(0)
    }
    
    // MARK: - UI Element Control
    
    func getFocusedElement() -> AXUIElement? {
        let app = AXUIElementCreateApplication(NSWorkspace.shared.frontmostApplication?.processIdentifier ?? 0)
        var focused: CFTypeRef?
        AXUIElementCopyAttributeValue(app, kAXFocusedUIElementAttribute as CFString, &focused)
        return (focused as! AXUIElement?)
    }
    
    func getElementAt(point: CGPoint) -> AXUIElement? {
        var element: AXUIElement?
        let systemWide = AXUIElementCreateSystemWide()
        AXUIElementCopyElementAtPosition(systemWide, Float(point.x), Float(point.y), &element)
        return element
    }
    
    func getElementAttribute(_ element: AXUIElement, attribute: String) -> Any? {
        var value: CFTypeRef?
        AXUIElementCopyAttributeValue(element, attribute as CFString, &value)
        return value
    }
    
    func setElementValue(_ element: AXUIElement, value: Any) {
        AXUIElementSetAttributeValue(element, kAXValueAttribute as CFString, value as CFTypeRef)
    }
    
    func performAction(_ element: AXUIElement, action: String) {
        AXUIElementPerformAction(element, action as CFString)
    }
    
    // MARK: - Window Control
    
    func getWindows(for app: NSRunningApplication) -> [AXUIElement] {
        var windows: CFTypeRef?
        let appElement = AXUIElementCreateApplication(app.processIdentifier)
        AXUIElementCopyAttributeValue(appElement, kAXWindowsAttribute as CFString, &windows)
        
        if let windowArray = windows as? [AXUIElement] {
            return windowArray
        }
        return []
    }
    
    func moveWindow(_ window: AXUIElement, to point: CGPoint) {
        AXUIElementSetAttributeValue(window, kAXPositionAttribute as CFString, CGPointToAXValue(point)! as CFTypeRef)
    }
    
    func resizeWindow(_ window: AXUIElement, to size: CGSize) {
        AXUIElementSetAttributeValue(window, kAXSizeAttribute as CFString, CGSizeToAXValue(size)! as CFTypeRef)
    }
    
    private func CGPointToAXValue(_ point: CGPoint) -> CFTypeRef? {
        return AXValueCreate(.cgPoint, &point)
    }
    
    private func CGSizeToAXValue(_ size: CGSize) -> CFTypeRef? {
        return AXValueCreate(.cgSize, &size)
    }
}
