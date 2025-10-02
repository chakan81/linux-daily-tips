interface PendingTip {
  id: number
  title: string
  category: string
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced'
  createdAt: string
  author: string
}

interface PendingTipsTableProps {
  tips: PendingTip[]
}

export function PendingTipsTable({ tips }: PendingTipsTableProps) {
  return (
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
          {tips.map((tip) => (
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
  )
}
