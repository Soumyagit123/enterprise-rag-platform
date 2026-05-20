"use client";

import { useState, useRef, useEffect } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [tenantId, setTenantId] = useState("tenant-demo-1");
  
  const [query, setQuery] = useState("");
  const [chatLog, setChatLog] = useState<{ role: string; content: string }[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat when messages update or typing state changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatLog, isTyping]);

  const rawApiUrl = process.env.NEXT_PUBLIC_API_URL;
  const API_URL = (rawApiUrl && rawApiUrl !== "undefined" && rawApiUrl !== "") 
    ? rawApiUrl 
    : "http://localhost:8000";

  // Quick Prompt Suggestion click handler
  const handleQuickPrompt = (prompt: string) => {
    setQuery(prompt);
  };

  // Handle Document Ingestion / Upload
  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setUploadStatus("Processing files & triggering pipeline queues...");
    
    const formData = new FormData();
    formData.append("file", file);
    formData.append("tenant_id", tenantId);

    try {
      const res = await fetch(`${API_URL}/api/ingest`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setUploadStatus("Ingestion queue active. Chunks are processing in background worker!");
        setFile(null);
      } else {
        setUploadStatus(`Upload Failed: ${data.detail || "Verification error"}`);
      }
    } catch (err) {
      setUploadStatus("Network gateway offline. Please verify API health.");
    } finally {
      setIsUploading(false);
    }
  };

  // Handle Conversational RAG Streaming Chat
  const handleChat = async (e?: React.FormEvent, promptOverride?: string) => {
    if (e) e.preventDefault();
    const activeQuery = promptOverride || query;
    if (!activeQuery.trim()) return;

    const newChat = [...chatLog, { role: "user", content: activeQuery }];
    setChatLog(newChat);
    if (!promptOverride) setQuery("");
    
    // Set loading state to true instantly so the loading indicator lights up!
    setIsTyping(true);

    const placeholderIndex = newChat.length;
    // Inject empty message to host RAG response stream
    setChatLog([...newChat, { role: "agent", content: "" }]);

    try {
      const res = await fetch(`${API_URL}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: activeQuery, tenant_id: tenantId }),
      });

      if (!res.ok) {
        const data = await res.json();
        setChatLog([
          ...newChat,
          { role: "agent", content: `System Exception: ${data.detail || "RAG engine timeout."}` },
        ]);
        setIsTyping(false);
        return;
      }

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) {
        throw new Error("Telemetry channel closed on active stream");
      }

      let accumulatedResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunkText = decoder.decode(value);
        const lines = chunkText.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const jsonData = JSON.parse(line.slice(6));
              if (jsonData.chunk) {
                // Disable loading pulse the exact microsecond the first token flows in!
                setIsTyping(false);
                accumulatedResponse += jsonData.chunk;
                setChatLog((prev) => {
                  const updated = [...prev];
                  updated[placeholderIndex] = { role: "agent", content: accumulatedResponse };
                  return updated;
                });
              }
            } catch (err) {
              // Gracefully bypass formatting fragments
            }
          }
        }
      }
    } catch (err) {
      setChatLog([
        ...newChat,
        { role: "agent", content: "Network error. Failed to establish connection with the streaming pipeline." },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 font-sans selection:bg-indigo-500/30 selection:text-indigo-200 overflow-hidden relative">
      
      {/* Decorative Worldclass Ambient Background Glows */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-[150px] pointer-events-none" />
      
      {/* Modern High-End Top Navigation bar */}
      <header className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md px-8 py-5 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <svg className="w-5 h-5 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
              APEX <span className="text-sm font-semibold tracking-widest px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">RAG PRO</span>
            </h1>
            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">Enterprise AI Telemetry Dashboard</p>
          </div>
        </div>

        {/* Tenant Configuration Selector Card */}
        <div className="flex items-center gap-4 bg-slate-900/60 border border-slate-800/80 rounded-2xl px-5 py-2.5 shadow-inner">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Namespace</span>
          </div>
          <div className="h-4 w-px bg-slate-800" />
          <input
            type="text"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            className="bg-transparent text-sm focus:outline-none text-cyan-300 font-mono font-bold w-36 transition-all"
            placeholder="tenant-id"
          />
        </div>
      </header>

      {/* Main Corporate Panel split */}
      <main className="flex h-[calc(100vh-81px)] overflow-hidden">
        
        {/* LEFT SIDEBAR: Pipeline, ingestion & local status (width: 30%) */}
        <section className="w-[30%] border-r border-slate-800/80 bg-slate-950/40 backdrop-blur-sm p-6 flex flex-col justify-between overflow-y-auto">
          
          <div className="space-y-6">
            {/* Title */}
            <div>
              <h2 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-1 flex items-center gap-2">
                <span className="w-1.5 h-3 rounded bg-indigo-500" /> Knowledge Ingestion Hub
              </h2>
              <p className="text-[11px] text-slate-500 font-medium">Asynchronous processing queue for enterprise resources.</p>
            </div>

            {/* Premium Document Upload Area */}
            <div className="space-y-4">
              <div 
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-300 ${
                  file 
                    ? "border-indigo-500/80 bg-indigo-500/[0.03] shadow-inner shadow-indigo-500/5" 
                    : "border-slate-800 hover:border-slate-700 bg-slate-900/20 hover:bg-slate-900/40"
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="hidden"
                  accept=".pdf,.txt,.docx"
                />
                
                {file ? (
                  <div className="space-y-3">
                    <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto text-indigo-400">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-200 truncate px-2">{file.name}</p>
                      <p className="text-[10px] text-slate-500 font-mono mt-0.5">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                    </div>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                        setUploadStatus("");
                      }}
                      className="text-[10px] font-bold text-red-400 hover:text-red-300 transition-colors uppercase tracking-wider"
                    >
                      Remove File
                    </button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="w-12 h-12 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-center mx-auto text-slate-400 group-hover:text-slate-200">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-300">Choose file or drag & drop</p>
                      <p className="text-[10px] text-slate-500 font-medium mt-1">Supports PDF, DOCX, TXT up to 25MB</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Upload Action Trigger Button */}
              <button
                onClick={handleUpload}
                disabled={!file || isUploading}
                className="w-full relative overflow-hidden bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:opacity-95 disabled:opacity-30 disabled:cursor-not-allowed text-white font-bold text-xs uppercase tracking-widest py-3.5 px-4 rounded-2xl shadow-lg shadow-indigo-500/10 transition-all active:scale-[0.99] flex items-center justify-center gap-2"
              >
                {isUploading ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Ingesting data...
                  </>
                ) : (
                  <>Trigger Pipeline Ingestion</>
                )}
              </button>

              {/* Upload Status Card */}
              {uploadStatus && (
                <div className={`p-4 rounded-2xl text-xs font-medium border animate-fadeIn flex gap-2.5 items-start ${
                  uploadStatus.includes('Failed') || uploadStatus.includes('error')
                    ? 'bg-red-950/20 border-red-500/20 text-red-300' 
                    : uploadStatus.includes('active') 
                      ? 'bg-emerald-950/20 border-emerald-500/20 text-emerald-300' 
                      : 'bg-indigo-950/20 border-indigo-500/20 text-indigo-300'
                }`}>
                  <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                    uploadStatus.includes('Failed') || uploadStatus.includes('error') ? 'bg-red-500' : 'bg-emerald-400'
                  }`} />
                  <div>
                    <span className="font-bold block uppercase text-[10px] tracking-wider mb-0.5">Pipeline Status</span>
                    {uploadStatus}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* TELEMETRY REGISTRY (Bottom) */}
          <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 shadow-inner space-y-4">
             <div>
               <h3 className="text-[10px] font-black uppercase tracking-widest text-slate-500">Infrastructure Telemetry</h3>
               <p className="text-[9px] text-slate-600 font-medium">Real-time indicators across active cluster layers.</p>
             </div>
             
             <div className="grid grid-cols-2 gap-3 text-[11px] font-mono">
               <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/50 flex items-center gap-2">
                 <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400" />
                 <div>
                   <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Gateway</p>
                   <p className="text-[10px] text-emerald-400 font-black mt-0.5">ONLINE</p>
                 </div>
               </div>
               
               <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/50 flex items-center gap-2">
                 <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400" />
                 <div>
                   <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Task Broker</p>
                   <p className="text-[10px] text-emerald-400 font-black mt-0.5">CONNECTED</p>
                 </div>
               </div>

               <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/50 flex items-center gap-2">
                 <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse shadow-sm shadow-indigo-400" />
                 <div>
                   <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">L2 Cache</p>
                   <p className="text-[10px] text-indigo-400 font-black mt-0.5">ACTIVE</p>
                 </div>
               </div>

               <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/50 flex items-center gap-2">
                 <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse shadow-sm shadow-cyan-400" />
                 <div>
                   <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Vector DB</p>
                   <p className="text-[10px] text-cyan-400 font-black mt-0.5">PINECONE</p>
                 </div>
               </div>
             </div>
          </div>
        </section>

        {/* RIGHT CHAT AREA: Interactive Chat Room (width: 70%) */}
        <section className="w-[70%] flex flex-col bg-slate-950/20 relative">
          
          {/* Scrollable Chat History Panel */}
          <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-800">
            {chatLog.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-6 max-w-xl mx-auto">
                <div className="w-16 h-16 rounded-2xl bg-indigo-500/5 border border-indigo-500/10 flex items-center justify-center text-indigo-400 shadow-xl shadow-indigo-500/5">
                  <svg className="w-7 h-7 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <div className="text-center space-y-2">
                  <p className="text-base font-black text-slate-200 uppercase tracking-wider">Apex Conversational Engine</p>
                  <p className="text-xs text-slate-400 leading-relaxed font-medium">
                    The cognitive pipeline is warm. Type a question or click a quick-prompt template below to explore context-expanded, hybrid vector answers.
                  </p>
                </div>

                {/* Quick-Prompt template grid */}
                <div className="grid grid-cols-2 gap-3 w-full mt-4">
                  <button 
                    onClick={() => handleChat(undefined, "What is the medical leave policy in India?")}
                    className="p-3.5 text-left rounded-xl bg-slate-900/40 border border-slate-800/80 hover:border-indigo-500/50 hover:bg-slate-900/60 transition-all text-xs font-medium text-slate-300 group flex items-start gap-2.5"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1 flex-shrink-0" />
                    <span>What is the medical leave policy in India?</span>
                  </button>
                  <button 
                    onClick={() => handleChat(undefined, "Can I carry forward my leaves next year?")}
                    className="p-3.5 text-left rounded-xl bg-slate-900/40 border border-slate-800/80 hover:border-indigo-500/50 hover:bg-slate-900/60 transition-all text-xs font-medium text-slate-300 group flex items-start gap-2.5"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1 flex-shrink-0" />
                    <span>Can I carry forward my leaves next year?</span>
                  </button>
                </div>
              </div>
            ) : (
              chatLog.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fadeIn`}>
                  <div className={`max-w-[75%] rounded-3xl px-6 py-4.5 shadow-sm relative ${
                    msg.role === "user" 
                      ? "bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 text-white rounded-br-none" 
                      : "bg-[#111726]/80 backdrop-blur-sm text-slate-200 rounded-bl-none border border-slate-800/80"
                  }`}>
                    
                    {/* Render elegant avatar badge for AI Agent */}
                    {msg.role === "agent" && (
                      <div className="flex items-center gap-2 mb-2.5 border-b border-slate-800/60 pb-2">
                        <span className="w-5 h-5 rounded-md bg-gradient-to-tr from-cyan-400 to-indigo-500 flex items-center justify-center shadow-md shadow-indigo-500/10">
                          <span className="w-1.5 h-1.5 bg-white rounded-full" />
                        </span>
                        <span className="text-[9px] font-black uppercase tracking-wider text-slate-400">APEX ENGINE</span>
                        <span className="text-[9px] font-medium text-slate-500 font-mono ml-auto">Gemini 2.5 Flash</span>
                      </div>
                    )}

                    {/* Chat Bubble Content with FIXED Thinking State Loader! */}
                    {msg.role === "agent" && msg.content === "" ? (
                      <div className="flex items-center gap-3 py-1 text-slate-300">
                        {/* Glowing ring spinner */}
                        <div className="w-4 h-4 rounded-full border-2 border-indigo-500/20 border-t-indigo-400 animate-spin" />
                        <span className="text-xs font-semibold tracking-wide text-indigo-400 animate-pulse">
                          RAG Pipeline searching vector shards & generating stream...
                        </span>
                      </div>
                    ) : (
                      <p className="whitespace-pre-wrap leading-relaxed text-sm font-medium">{msg.content}</p>
                    )}
                  </div>
                </div>
              ))
            )}

            {/* Bouncing Dots Loader at bottom for initial API handshakes */}
            {isTyping && (
              <div className="flex justify-start animate-fadeIn">
                <div className="bg-[#111726]/80 backdrop-blur-sm rounded-3xl rounded-bl-none px-6 py-4.5 border border-slate-800/80 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Interactive Chat Input Area */}
          <div className="p-6 bg-slate-950/60 backdrop-blur-md border-t border-slate-900 relative">
            <form onSubmit={handleChat} className="relative max-w-4xl mx-auto">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Query your enterprise data namespace..."
                className="w-full bg-[#0d121f] border border-slate-800/80 text-white text-sm rounded-2xl pl-6 pr-16 py-4 focus:outline-none focus:ring-2 focus:ring-indigo-500/80 focus:border-transparent transition-all shadow-inner placeholder-slate-500 font-medium"
              />
              <button
                type="submit"
                disabled={!query.trim() || isTyping}
                className="absolute right-2.5 top-2.5 bottom-2.5 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:opacity-95 disabled:bg-slate-900 disabled:opacity-40 disabled:cursor-not-allowed text-white px-4 rounded-xl flex items-center justify-center transition-all shadow-lg active:scale-95"
              >
                <svg className="w-4 h-4 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </form>
          </div>

        </section>
      </main>
    </div>
  );
}
