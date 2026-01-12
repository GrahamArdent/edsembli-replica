import { useAppStore } from '../store/useAppStore';
import { FRAMES } from '../constants';

export function Preview() {
  const selectedStudentId = useAppStore(state => state.selectedStudentId);
  const student = useAppStore(state => state.students.find(s => s.id === selectedStudentId));
  const selectedFrameId = useAppStore(state => state.selectedFrameId);

  if (!student) return null;

  const currentFrameLabel = FRAMES.find(f => f.id === selectedFrameId)?.label;

  return (
    <div className="w-80 border-l border-gray-200 bg-gray-50 flex flex-col h-screen hidden lg:flex">
      <div className="p-4 border-b border-gray-200 bg-white">
        <h3 className="text-sm font-bold text-gray-900 uppercase">Live Preview</h3>
        <p className="text-xs text-gray-500 mt-1">
          {currentFrameLabel}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="bg-white border border-gray-200 shadow-sm p-4 rounded-md min-h-[500px]">
          <div className="prose prose-sm font-serif">
            <h4 className="text-blue-900 border-b border-blue-100 pb-1 mb-2">
              {currentFrameLabel}
            </h4>

            <p className="text-gray-800 leading-relaxed mb-4">
              <span className="text-gray-400 italic">[Key Learning will appear here]</span>
            </p>

            <p className="text-gray-800 leading-relaxed mb-4">
              <span className="text-gray-400 italic">[Growth will appear here]</span>
            </p>

            <p className="text-gray-800 leading-relaxed">
              <span className="text-gray-400 italic">[Next Steps will appear here]</span>
            </p>
          </div>
        </div>

        <div className="text-xs text-gray-400 text-center">
          Character Count: 0 / 1500
        </div>
      </div>
    </div>
  );
}
