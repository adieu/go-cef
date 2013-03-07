package main

import (
    "os"
    "cef"
)

func Runner(result chan bool, work func()) {
    defer func() {
        if err := recover(); err != nil {
            result<-false
        }
    }()
    work()
    result<-true
}

func Work() {
    args := cef.NewCefMainArgs(os.Args)
    app := cef.NewCefRefPtrCefApp()
    cef.CefExecuteProcess(args, app)
    settings := cef.NewCefStructBaseCefSettingsTraits()
    cef.CefInitialize(args, settings, app)
    cef.Initialize_objc()
    cef.Create_browser("cefdemo", "http://www.google.com", 1024, 768)
    cef.CefRunMessageLoop()
    cef.CefShutdown()
}


func main() {
    result := make(chan bool)
    go Runner(result, Work)
    <-result
}


