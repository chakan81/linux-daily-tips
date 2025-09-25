import { Metadata } from 'next'
import {
  BarChart3,
  Users,
  FileText,
  Calendar,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Plus,
  Settings,
  Bell
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Admin Dashboard',
  description: 'Linux Daily Tips administration panel for content management.',
}

// Mock data for demonstration
const dashboardStats = {
  totalTips: 365,
  pendingApproval: 7,
  activeUsers: 12500,
  completionRate: 87,
}

const recentActivity = [
  {
    id: 1,
    type: 'tip_created',
    message: 'New tip "Advanced Git Commands" created',
    time: '2 minutes ago',
    status: 'pending'
  },
  {
    id: 2,
    type: 'tip_approved',
    message: 'Tip "SSH Key Management" approved',
    time: '15 minutes ago',
    status: 'approved'
  },
  {
    id: 3,
    type: 'user_activity',
    message: '50 new users completed today\'s tip',
    time: '1 hour ago',
    status: 'info'
  },
  {
    id: 4,
    type: 'system',
    message: 'Daily tip generation completed',
    time: '2 hours ago',
    status: 'success'
  },
]

const pendingTips = [
  {
    id: 1,
    title: "Advanced Process Management with systemctl",
    category: "System Administration",
    difficulty: "Advanced",
    createdAt: "2024-01-15",
    author: "AI Generator"
  },
  {
    id: 2,
    title: "Network Troubleshooting with ss command",
    category: "Networking",
    difficulty: "Intermediate",
    createdAt: "2024-01-15",
    author: "AI Generator"
  },
  {
    id: 3,
    title: "File Compression with tar and gzip",
    category: "File Management",
    difficulty: "Beginner",
    createdAt: "2024-01-14",
    author: "AI Generator"
  },
]

function StatsCard({ title, value, icon: Icon, change, changeType }: {
  title: string
  value: string | number
  icon: any
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
}) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-card">
      <div className="flex items-center justify-between mb-4">
        <div className="inline-flex items-center justify-center w-12 h-12 bg-gray-100 rounded-xl">
          <Icon className="w-6 h-6 text-gray-600" />
        </div>
        {change && (
          <div className={`flex items-center text-sm font-medium ${
            changeType === 'positive' ? 'text-green-600' :
            changeType === 'negative' ? 'text-red-600' :
            'text-gray-600'
          }`}>
            <TrendingUp className="w-4 h-4 mr-1" />
            {change}
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-gray-900 mb-1">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      <div className="text-sm text-gray-600">{title}</div>
    </div>
  )
}

function ActivityItem({ activity }: { activity: any }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'approved': return 'bg-green-100 text-green-800'
      case 'success': return 'bg-green-100 text-green-800'
      case 'info': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'tip_created': return Clock
      case 'tip_approved': return CheckCircle
      case 'user_activity': return Users
      case 'system': return Settings
      default: return AlertCircle
    }
  }

  const Icon = getIcon(activity.type)

  return (
    <div className="flex items-start gap-3 p-4 hover:bg-gray-50 rounded-lg transition-colors">
      <div className="inline-flex items-center justify-center w-8 h-8 bg-gray-100 rounded-full flex-shrink-0">
        <Icon className="w-4 h-4 text-gray-600" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900 mb-1">{activity.message}</p>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">{activity.time}</span>
          <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(activity.status)}`}>
            {activity.status}
          </span>
        </div>
      </div>
    </div>
  )
}

export default function AdminPage() {
  return (
    <div className="min-h-screen bg-gray-50 page-enter">
      <div className="container-awwwards py-8">
        {/* Header */}
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

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Tips Published"
            value={dashboardStats.totalTips}
            icon={FileText}
            change="+12 this week"
            changeType="positive"
          />
          <StatsCard
            title="Pending Approval"
            value={dashboardStats.pendingApproval}
            icon={Clock}
            change="2 urgent"
            changeType="negative"
          />
          <StatsCard
            title="Active Users"
            value={dashboardStats.activeUsers}
            icon={Users}
            change="+8% this month"
            changeType="positive"
          />
          <StatsCard
            title="Completion Rate"
            value={`${dashboardStats.completionRate}%`}
            icon={BarChart3}
            change="+2.3%"
            changeType="positive"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Pending Tips */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-card">
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  Tips Pending Approval
                </h2>
                <button className="text-sm text-accent-600 hover:text-accent-700 font-medium">
                  View All
                </button>
              </div>

              <div className="divide-y divide-gray-200">
                {pendingTips.map((tip) => (
                  <div key={tip.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-sm font-semibold text-gray-900 mb-2">
                        {tip.title}
                      </h3>
                      <div className="flex items-center gap-2 ml-4">
                        <button className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full hover:bg-green-200 transition-colors">
                          Approve
                        </button>
                        <button className="text-xs bg-red-100 text-red-700 px-3 py-1 rounded-full hover:bg-red-200 transition-colors">
                          Reject
                        </button>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
                      <span>{tip.category}</span>
                      <span>•</span>
                      <span className={`px-2 py-1 rounded-full ${
                        tip.difficulty === 'Beginner' ? 'bg-green-100 text-green-700' :
                        tip.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {tip.difficulty}
                      </span>
                      <span>•</span>
                      <span>{tip.createdAt}</span>
                      <span>•</span>
                      <span>{tip.author}</span>
                    </div>

                    <div className="flex items-center gap-3">
                      <button className="text-sm text-accent-600 hover:text-accent-700 font-medium">
                        Review Content
                      </button>
                      <button className="text-sm text-gray-600 hover:text-gray-700">
                        Test Terminal
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div>
            <div className="bg-white rounded-xl shadow-card">
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  Recent Activity
                </h2>
                <button className="text-sm text-accent-600 hover:text-accent-700 font-medium">
                  View All
                </button>
              </div>

              <div className="max-h-96 overflow-y-auto">
                {recentActivity.map((activity) => (
                  <ActivityItem key={activity.id} activity={activity} />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="bg-white p-4 rounded-xl shadow-card hover:shadow-card-hover transition-all duration-200 interactive text-left">
              <div className="inline-flex items-center justify-center w-10 h-10 bg-blue-100 rounded-xl mb-3">
                <Plus className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Generate Week Tips</h3>
              <p className="text-sm text-gray-600">Create 7 new tips using AI</p>
            </button>

            <button className="bg-white p-4 rounded-xl shadow-card hover:shadow-card-hover transition-all duration-200 interactive text-left">
              <div className="inline-flex items-center justify-center w-10 h-10 bg-green-100 rounded-xl mb-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Bulk Approve</h3>
              <p className="text-sm text-gray-600">Review and approve multiple tips</p>
            </button>

            <button className="bg-white p-4 rounded-xl shadow-card hover:shadow-card-hover transition-all duration-200 interactive text-left">
              <div className="inline-flex items-center justify-center w-10 h-10 bg-purple-100 rounded-xl mb-3">
                <BarChart3 className="w-5 h-5 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Analytics</h3>
              <p className="text-sm text-gray-600">View detailed usage statistics</p>
            </button>

            <button className="bg-white p-4 rounded-xl shadow-card hover:shadow-card-hover transition-all duration-200 interactive text-left">
              <div className="inline-flex items-center justify-center w-10 h-10 bg-gray-100 rounded-xl mb-3">
                <Settings className="w-5 h-5 text-gray-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Settings</h3>
              <p className="text-sm text-gray-600">Configure platform settings</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}