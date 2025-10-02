import { Bell, Plus } from 'lucide-react'

export function AdminHeader() {
  return (
    <div className="flex items-center justify-between mb-8">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
          Admin Dashboard
        </h1>
        <p className="text-gray-600">
          Manage tips, monitor activity, and oversee the Linux Daily Tips platform
        </p>
      </div>

      <div className="flex items-center gap-3">
        <button className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors">
          <Bell className="w-4 h-4" />
          <span className="hidden sm:inline">Notifications</span>
          <span className="inline-flex items-center justify-center w-5 h-5 text-xs bg-red-500 text-white rounded-full">
            3
          </span>
        </button>
        <button className="inline-flex items-center gap-2 bg-black text-white px-4 py-2 rounded-xl hover:bg-gray-800 transition-colors">
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Create Tip</span>
        </button>
      </div>
    </div>
  )
}
