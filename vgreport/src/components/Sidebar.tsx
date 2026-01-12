import { useAppStore } from '../store/useAppStore';
import { Circle } from 'lucide-react';
import { cn } from '../lib/utils'; // Assuming this exists from shadcn init

export function Sidebar() {
  const { students, selectedStudentId, setSelectedStudentId } = useAppStore();

  return (
    <div className="w-64 border-r border-gray-200 bg-gray-50 h-screen flex flex-col">
      <div className="p-4 border-b border-gray-200 bg-white">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <span className="bg-blue-600 text-white p-1 rounded">VG</span> Report
        </h1>
        <p className="text-xs text-gray-500 mt-1">Kindergarten CoL Writer</p>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-2 py-2">
          Classroom ({students.length})
        </div>

        {students.map((student) => {
          const isSelected = selectedStudentId === student.id;
          return (
            <button
              key={student.id}
              onClick={() => setSelectedStudentId(student.id)}
              className={cn(
                "w-full text-left px-3 py-2 rounded-md flex items-center gap-3 transition-colors",
                isSelected
                  ? "bg-blue-100 text-blue-900 ring-1 ring-blue-200"
                  : "hover:bg-gray-200 text-gray-700"
              )}
            >
              <div className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
                isSelected ? "bg-blue-600 text-white" : "bg-gray-300 text-gray-600"
              )}>
                {student.firstName[0]}{student.lastName[0]}
              </div>

              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">
                  {student.firstName} {student.lastName}
                </div>
                <div className="text-xs text-gray-500 truncate flex items-center gap-1">
                  {/* Mock progress indicator */}
                  <Circle className="w-3 h-3 text-gray-300" />
                  <span>0/4 Frames</span>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      <div className="p-4 border-t border-gray-200 bg-white">
        <button className="w-full py-2 px-4 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800 transition-colors">
          Add Student
        </button>
      </div>
    </div>
  );
}
