'use client';

import {
  BarChart3,
  CheckCircle,
  Plus,
  Settings,
} from 'lucide-react'
import { AdminHeader } from './components/AdminHeader'
import { AdminStatsGrid } from './components/AdminStatsGrid'
import { PendingTipsTable } from './components/PendingTipsTable'
import { RecentActivityFeed } from './components/RecentActivityFeed'
import { useAdminStats, usePendingTips, useRecentActivity } from '@/lib/hooks/useAdmin'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'

export default function AdminPage() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useAdminStats();
  const { data: pendingTips, isLoading: tipsLoading, error: tipsError } = usePendingTips();
  const { data: activities, isLoading: activityLoading, error: activityError } = useRecentActivity();

  const isLoading = statsLoading || tipsLoading || activityLoading;
  const error = statsError || tipsError || activityError;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 page-enter">
        <div className="container-awwwards py-8">
          <AdminHeader />
          <LoadingSpinner size="xl" text="Loading admin dashboard..." />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 page-enter">
        <div className="container-awwwards py-8">
          <AdminHeader />
          <ErrorMessage
            type="error"
            title="Failed to load dashboard"
            message="Could not load admin dashboard data. Please refresh the page or try again later."
          />
        </div>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-gray-50 page-enter">
      <div className="container-awwwards py-8">
        <AdminHeader />

        {stats && <AdminStatsGrid stats={stats} />}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {pendingTips && <PendingTipsTable tips={pendingTips} />}
          {activities && <RecentActivityFeed activities={activities} />}
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
