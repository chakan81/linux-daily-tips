import {
  Clock,
  CheckCircle,
  Users,
  Settings,
  AlertCircle
} from 'lucide-react'
import { Activity } from '@/lib/types/common'

interface ActivityItemProps {
  activity: Activity
}

function ActivityItem({ activity }: ActivityItemProps) {
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

interface RecentActivityFeedProps {
  activities: Activity[]
}

export function RecentActivityFeed({ activities }: RecentActivityFeedProps) {
  return (
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
          {activities.map((activity) => (
            <ActivityItem key={activity.id} activity={activity} />
          ))}
        </div>
      </div>
    </div>
  )
}
