'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { Terminal as TerminalIcon, Info, Settings, PlayCircle, StopCircle, AlertCircle } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { createTerminalSession, deleteTerminalSession, TerminalSessionResponse } from '@/lib/api';
import { LoadingSpinner } from '@/components/common';

// TerminalEmulator를 동적 import로 불러오기 (SSR 비활성화)
const TerminalEmulator = dynamic(
  () => import('@/components/terminal').then((mod) => ({ default: mod.TerminalEmulator })),
  {
    ssr: false,
    loading: () => <LoadingSpinner size="lg" />
  }
);

// Extend TerminalSessionResponse with client-side ws_url
type TerminalSession = TerminalSessionResponse & { ws_url: string };

export default function TerminalPage() {
  const [session, setSession] = useState<TerminalSession | null>(null);

  // Create session mutation
  const createSessionMutation = useMutation({
    mutationFn: () => createTerminalSession(),
    onSuccess: (data) => {
      // Generate WebSocket URL on client-side
      // Use localhost:8000 which is exposed by Docker Compose
      // This works for both browser and Playwright E2E tests
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//localhost:8000/api/v1/terminal/ws/${data.session_id}`;

      setSession({ ...data, ws_url: wsUrl });
    },
    onError: (error: Error) => {
      console.error('Failed to create terminal session:', error);
    },
  });

  // Delete session mutation
  const deleteSessionMutation = useMutation({
    mutationFn: () => {
      if (!session) throw new Error('No session to delete');
      return deleteTerminalSession(session.session_id);
    },
    onSuccess: () => {
      setSession(null);
    },
    onError: (error: Error) => {
      console.error('Failed to delete terminal session:', error);
    },
  });

  const handleStartTerminal = () => {
    createSessionMutation.mutate();
  };

  const handleStopTerminal = () => {
    deleteSessionMutation.mutate();
  };

  const handleSessionEnd = () => {
    setSession(null);
  };

  const isLoading = createSessionMutation.isPending || deleteSessionMutation.isPending;
  const error = createSessionMutation.error || deleteSessionMutation.error;

  return (
    <div className="min-h-screen bg-gray-50 page-enter">
      <div className="container-awwwards py-8">
        {/* Header */}
        <div className="max-w-6xl mx-auto mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-black rounded-2xl">
                <TerminalIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
                  Interactive Terminal
                </h1>
                <p className="text-gray-600">
                  Practice Linux commands in a safe sandbox environment
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                disabled
                className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-xl border border-gray-200 text-gray-400 cursor-not-allowed"
              >
                <Settings className="w-4 h-4" />
                Settings
              </button>
              <button
                disabled
                className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-xl border border-gray-200 text-gray-400 cursor-not-allowed"
              >
                <Info className="w-4 h-4" />
                Help
              </button>
            </div>
          </div>

          {/* Quick Tips */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-8">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900 mb-2">Getting Started</h3>
                <p className="text-blue-700 text-sm">
                  Click "Start Terminal" to launch a safe sandbox environment. Try basic commands like{' '}
                  <code className="bg-blue-100 px-1 rounded">ls</code>,
                  <code className="bg-blue-100 px-1 rounded ml-1">pwd</code>, or
                  <code className="bg-blue-100 px-1 rounded ml-1">whoami</code> to get started.
                </p>
              </div>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-8">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900 mb-1">Error</h3>
                  <p className="text-red-700 text-sm">
                    {error.message || 'Failed to manage terminal session. Please try again.'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Terminal Container */}
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-2xl shadow-card overflow-hidden">
            {/* Terminal Header */}
            <div className="bg-gray-100 border-b border-gray-200 px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  </div>
                  <span className="text-sm font-medium text-gray-600">Terminal</span>
                  {session && (
                    <span className="text-xs text-gray-500 font-mono">
                      Session: {session.session_id.slice(-8)}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  {!session ? (
                    <button
                      onClick={handleStartTerminal}
                      disabled={isLoading}
                      className="inline-flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? (
                        <>
                          <LoadingSpinner size="sm" />
                          Starting...
                        </>
                      ) : (
                        <>
                          <PlayCircle className="w-4 h-4" />
                          Start Terminal
                        </>
                      )}
                    </button>
                  ) : (
                    <button
                      onClick={handleStopTerminal}
                      disabled={isLoading}
                      className="inline-flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? (
                        <>
                          <LoadingSpinner size="sm" />
                          Stopping...
                        </>
                      ) : (
                        <>
                          <StopCircle className="w-4 h-4" />
                          Stop Terminal
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Terminal Content */}
            <div className="bg-gray-900 text-green-400 font-mono text-sm overflow-hidden">
              {session ? (
                // Active terminal session
                <div className="min-h-[500px]">
                  <TerminalEmulator
                    sessionId={session.session_id}
                    wsUrl={session.ws_url}
                    onSessionEnd={handleSessionEnd}
                  />
                </div>
              ) : (
                // Terminal not started
                <div className="p-6 min-h-[500px] flex items-center justify-center">
                  <div className="text-center text-gray-400">
                    <TerminalIcon className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg mb-2">Terminal Not Started</p>
                    <p className="text-sm">
                      Click "Start Terminal" above to launch your interactive session
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Terminal Footer */}
            <div className="bg-gray-100 border-t border-gray-200 px-6 py-4">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <div className="flex items-center gap-4">
                  <span>{session ? 'Connected' : 'Disconnected'}</span>
                  <span>•</span>
                  <span>Ubuntu 22.04 LTS</span>
                  <span>•</span>
                  <span>Bash 5.1.16</span>
                </div>
                {session && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs">Container: {session.container_id.slice(0, 12)}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Command Reference */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Commands</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">ls</code>
                  <span className="text-sm text-gray-600">List directory contents</span>
                </div>
                <div className="flex items-center justify-between">
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">pwd</code>
                  <span className="text-sm text-gray-600">Print working directory</span>
                </div>
                <div className="flex items-center justify-between">
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">cd</code>
                  <span className="text-sm text-gray-600">Change directory</span>
                </div>
                <div className="flex items-center justify-between">
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">mkdir</code>
                  <span className="text-sm text-gray-600">Create directory</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">File Operations</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">cat</code>
                  <span className="text-sm text-gray-600">Display file contents</span>
                </div>
                <div className="flex items-center justify-between">
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">cp</code>
                  <span className="text-sm text-gray-600">Copy files</span>
                </div>
                <div className="flex items-center justify-between">
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">mv</code>
                  <span className="text-sm text-gray-600">Move/rename files</span>
                </div>
                <div className="flex items-center justify-between">
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">rm</code>
                  <span className="text-sm text-gray-600">Remove files</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
