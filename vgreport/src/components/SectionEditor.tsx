import { useState } from 'react';
import { SectionId, Student, Template } from '../types';
import { TemplateSelector } from './TemplateSelector';

interface SectionEditorProps {
  section: { id: SectionId; label: string };
  frameCanonicalId: string;
  student: Student;
}

export function SectionEditor({ section, frameCanonicalId, student }: SectionEditorProps) {
  const [text, setText] = useState('');

  const handleTemplateSelect = (template: Template) => {
    // Basic insertion for now. In Phase 2.4, this will trigger the Slot Input generation.
    setText(prev => (prev ? prev + '\n' + template.text : template.text));
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-bold text-gray-700 uppercase tracking-wide">
          {section.label}
        </label>
        <TemplateSelector
            frameCanonicalId={frameCanonicalId}
            sectionId={section.id}
            onSelect={handleTemplateSelect}
        />
      </div>

      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full h-32 p-4 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none font-sans text-gray-800 leading-relaxed"
          placeholder={`Write about ${student.firstName}'s ${section.label.toLowerCase()}...`}
        />
      </div>
    </div>
  );
}
