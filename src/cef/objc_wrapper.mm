#include <Cocoa/Cocoa.h>
#include "include/cef_client.h"
#include "include/cef_app.h"
#include "include/cef_application_mac.h"
#include "include/cef_browser.h"
#include "include/cef_frame.h"
#include "include/cef_runnable.h"

class GoCefHandler : public CefClient {

public:
  GoCefHandler() { }
  ~GoCefHandler() { }

  // Note that any of the IMPLEMENT_WHATEVER
  // macros that come with CEF can (and do) set
  // access modifiers, so you'll want them after
  // everything else in your class or you may be
  // in for a surprise when the access of a member
  // isn't what you expect it to be!
  IMPLEMENT_REFCOUNTING(GoCefHandler);
};

void initialize_objc() {
    [NSAutoreleasePool new];
    [NSApplication sharedApplication];
    [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
    return;
}

void create_browser(char*title, char* url, int width, int height) {
    id menubar = [[NSMenu new] autorelease];
    id appMenuItem = [[NSMenuItem new] autorelease];
    [menubar addItem:appMenuItem];
    [NSApp setMainMenu:menubar];
    id appMenu = [[NSMenu new] autorelease];
    id appName = [[NSProcessInfo processInfo] processName];
    id quitTitle = [@"Quit " stringByAppendingString:appName];
    id quitMenuItem = [[[NSMenuItem alloc] initWithTitle:quitTitle
        action:@selector(terminate:) keyEquivalent:@"q"] autorelease];
    [appMenu addItem:quitMenuItem];
    [appMenuItem setSubmenu:appMenu];
    NSRect screen_rect = [[NSScreen mainScreen] visibleFrame];
    NSRect window_rect = { {0, screen_rect.size.height - height},
        {width, height} };
    NSWindow* mainWnd = [[UnderlayOpenGLHostingWindow alloc]
        initWithContentRect:window_rect
        styleMask:(NSTitledWindowMask |
                NSClosableWindowMask |
                NSMiniaturizableWindowMask |
                NSResizableWindowMask )
        backing:NSBackingStoreBuffered
        defer:NO];
    NSString* mainTitle = [NSString stringWithCString:title encoding:NSUTF8StringEncoding];
    [mainWnd setTitle:mainTitle];
    // Rely on the window delegate to clean us up rather than immediately
    // releasing when the window gets closed. We use the delegate to do
    // everything from the autorelease pool so the window isn't on the stack
    // during cleanup (ie, a window close from javascript).
    [mainWnd setReleasedWhenClosed:NO];

    CefRefPtr<GoCefHandler> g_handler;
    g_handler = new GoCefHandler();

    NSView* contentView = [mainWnd contentView];
    
    // Create the browser view.
    CefWindowInfo window_info;
    CefBrowserSettings settings;
    window_info.SetAsChild(contentView, 0, 0, width, height);
    CefBrowserHost::CreateBrowser(window_info, g_handler.get(), url, settings);

    [mainWnd makeKeyAndOrderFront: nil];
    
    [NSApp activateIgnoringOtherApps:YES];
    return;
}
