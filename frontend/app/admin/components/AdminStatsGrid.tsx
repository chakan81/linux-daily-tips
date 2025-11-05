import {
  BarChart3,
  Users,
  FileText,
  Clock,
  TrendingUp,
} from 'lucide-react'
import { IconComponent } from '@/lib/types/common'

interface StatsCardProps {
  title: string
  value: string | number
  icon: IconComponent
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
}

function StatsCard({ title, value, icon: Icon, change, changeType }: StatsCardProps) {
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

interface StatsData {
  totalTips: number
  pendingApproval: number
  activeUsers: number
  completionRate: number
}

interface AdminStatsGridProps {
  stats: StatsData
}

export function AdminStatsGrid({ stats }: AdminStatsGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatsCard
        title="Total Tips Published"
        value={stats.totalTips}
        icon={FileText}
        change="+12 this week"
        changeType="positive"
      />
      <StatsCard
        title="Pending Approval"
        value={stats.pendingApproval}
        icon={Clock}
        change="2 urgent"
        changeType="negative"
      />
      <StatsCard
        title="Active Users"
        value={stats.activeUsers}
        icon={Users}
        change="+8% this month"
        changeType="positive"
      />
      <StatsCard
        title="Completion Rate"
        value={`${stats.completionRate}%`}
        icon={BarChart3}
        change="+2.3%"
        changeType="positive"
      />
    </div>
  )
}
