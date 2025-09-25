import { Metadata } from 'next'
import { Terminal as TerminalIcon, Info, Settings, PlayCircle } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Interactive Terminal',
  description: 'Practice Linux commands in a safe, interactive terminal environment.',
}

export default function TerminalPage() {
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
              <button className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors">
                <Settings className="w-4 h-4" />
                Settings
              </button>
              <button className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors">
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
                  This is a safe sandbox environment. Try basic commands like <code className="bg-blue-100 px-1 rounded">ls</code>,
                  <code className="bg-blue-100 px-1 rounded ml-1">pwd</code>, or
                  <code className="bg-blue-100 px-1 rounded ml-1">whoami</code> to get started.
                </p>
              </div>
            </div>
          </div>
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
                </div>

                <div className="flex items-center gap-2">
                  <button className="inline-flex items-center gap-2 bg-green-100 text-green-700 px-3 py-1 rounded-lg text-sm font-medium hover:bg-green-200 transition-colors">
                    <PlayCircle className="w-4 h-4" />
                    Running
                  </button>
                </div>
              </div>
            </div>

            {/* Terminal Content */}
            <div className="bg-gray-900 text-green-400 font-mono text-sm overflow-hidden">
              <div className="p-6 min-h-[500px]">
                <div className="mb-4">
                  <div className="text-gray-400">Linux Daily Tips Terminal v1.0</div>
                  <div className="text-gray-400">Type 'help' for available commands</div>
                  <div className="text-gray-400 mb-4">─────────────────────────────────────</div>
                </div>

                {/* Terminal Session */}
                <div className="space-y-2">
                  <div className="flex items-center">
                    <span className="text-blue-400">user@linux-tips</span>
                    <span className="text-gray-400">:</span>
                    <span className="text-green-400">~</span>
                    <span className="text-gray-400">$ </span>
                    <span className="text-white terminal-cursor">pwd</span>
                  </div>
                  <div className="text-gray-300 ml-4">/home/user</div>

                  <div className="flex items-center">
                    <span className="text-blue-400">user@linux-tips</span>
                    <span className="text-gray-400">:</span>
                    <span className="text-green-400">~</span>
                    <span className="text-gray-400">$ </span>
                    <span className="text-white">ls -la</span>
                  </div>
                  <div className="text-gray-300 ml-4 space-y-1">
                    <div>total 8</div>
                    <div>drwxr-xr-x 3 user user 4096 Dec 15 10:30 .</div>
                    <div>drwxr-xr-x 3 root root 4096 Dec 15 10:29 ..</div>
                    <div>-rw-r--r-- 1 user user  220 Dec 15 10:29 .bash_logout</div>
                    <div>-rw-r--r-- 1 user user 3771 Dec 15 10:29 .bashrc</div>
                    <div>-rw-r--r-- 1 user user  807 Dec 15 10:29 .profile</div>
                    <div>drwxr-xr-x 2 user user 4096 Dec 15 10:30 documents</div>
                  </div>

                  <div className="flex items-center">
                    <span className="text-blue-400">user@linux-tips</span>
                    <span className="text-gray-400">:</span>
                    <span className="text-green-400">~</span>
                    <span className="text-gray-400">$ </span>
                    <span className="text-white terminal-cursor"></span>
                  </div>
                </div>

                {/* Input Area - This would be replaced with actual terminal functionality */}
                <div className="mt-8">
                  <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                    <div className="text-center text-gray-400">
                      <TerminalIcon className="w-8 h-8 mx-auto mb-2" />
                      <p className="text-sm">Interactive Terminal Coming Soon</p>
                      <p className="text-xs mt-1">This will connect to a real terminal environment</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Terminal Footer */}
            <div className="bg-gray-100 border-t border-gray-200 px-6 py-4">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <div className="flex items-center gap-4">
                  <span>Connected</span>
                  <span>•</span>
                  <span>Ubuntu 22.04 LTS</span>
                  <span>•</span>
                  <span>Bash 5.1.16</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs">Session: 00:05:32</span>
                </div>
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
  )
}