import { useEffect, useMemo, useRef, useState } from 'react';
import { FrameId, SectionId, Student, Template } from '../types';
import { TemplateSelector } from './TemplateSelector';
import { sidecar } from '../services/sidecar';
import { useAppStore } from '../store/useAppStore';

interface SectionEditorProps {
  section: { id: SectionId; label: string };
  frameId: FrameId;
  frameCanonicalId: string;
  student: Student;
}

export function SectionEditor({ section, frameId, frameCanonicalId, student }: SectionEditorProps) {
  const updateComment = useAppStore(s => s.updateComment);
  const currentPeriod = useAppStore(s => s.currentPeriod);
  const templates = useAppStore(s => s.templates);

  const comment = useAppStore(s => {
    const draft = s.drafts[student.id];
    return (draft?.comments?.[frameId]?.[section.id] ?? { slots: {} });
  });

  const selectedTemplate = useMemo(() => {
    if (!comment?.templateId) return undefined;
    return templates.find(t => t.id === comment.templateId);
  }, [comment?.templateId, templates]);

  const slots = comment?.slots ?? {};
  const slotKeys = selectedTemplate?.slots ?? [];

  const [isRendering, setIsRendering] = useState(false);
  const [renderErr, setRenderErr] = useState<string | null>(null);
  const renderTimer = useRef<number | null>(null);

  const handleTemplateSelect = (template: Template) => {
    const nextSlots: Record<string, string> = { ...(slots as any) };
    for (const key of template.slots || []) {
      if (typeof nextSlots[key] !== 'string') nextSlots[key] = '';
    }
    updateComment(student.id, frameId, section.id, {
      templateId: template.id,
      slots: nextSlots,
      rendered: comment?.rendered,
      validation: comment?.validation
    });
  };

  const handleClear = () => {
    updateComment(student.id, frameId, section.id, {
      templateId: undefined,
      slots: {},
      rendered: undefined,
      validation: undefined,
    });
  };

  const setSlotValue = (key: string, value: string) => {
    updateComment(student.id, frameId, section.id, {
      templateId: comment?.templateId,
      slots: { ...(slots as any), [key]: value },
      rendered: comment?.rendered,
      validation: comment?.validation,
    });
  };

  useEffect(() => {
    if (!comment?.templateId) return;
    if (renderTimer.current) window.clearTimeout(renderTimer.current);

    renderTimer.current = window.setTimeout(async () => {
      try {
        setIsRendering(true);
        setRenderErr(null);
        const result = await sidecar.call('render_comment', {
          template_id: comment.templateId,
          slots: comment.slots || {}
        });

        updateComment(student.id, frameId, section.id, {
          templateId: comment.templateId,
          slots: comment.slots || {},
          rendered: result?.text ?? '',
          validation: result?.validation,
        });
      } catch (e: any) {
        setRenderErr(e?.message || JSON.stringify(e));
      } finally {
        setIsRendering(false);
      }
    }, 350);

    return () => {
      if (renderTimer.current) window.clearTimeout(renderTimer.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [comment?.templateId, JSON.stringify(comment?.slots), student.id, frameId, section.id, currentPeriod]);

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
            selectedTemplateId={comment?.templateId}
            onClear={comment?.templateId ? handleClear : undefined}
        />
      </div>

      {!selectedTemplate && (
        <div className="text-sm text-gray-500 border border-dashed border-gray-300 rounded-lg p-4 bg-gray-50">
          Select a template to generate slot questions.
        </div>
      )}

      {selectedTemplate && (
        <div className="space-y-3">
          <div className="text-xs text-gray-500">
            Template preview: <span className="font-mono">{selectedTemplate.id}</span>
          </div>

          {slotKeys.length === 0 && (
            <div className="text-sm text-gray-500 border border-gray-200 rounded-lg p-4 bg-white">
              This template has no slots.
            </div>
          )}

          {slotKeys.map((key) => (
            <div key={key} className="space-y-1">
              <label className="text-xs font-medium text-gray-700">
                {key.replace(/_/g, ' ')}
              </label>
              <textarea
                value={String((slots as any)[key] ?? '')}
                onChange={(e) => setSlotValue(key, e.target.value)}
                className="w-full h-20 p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none font-sans text-gray-800 leading-relaxed"
                placeholder={`Enter ${key.replace(/_/g, ' ')}...`}
              />
            </div>
          ))}

          <div className="flex items-center justify-between text-xs">
            <div className="text-gray-500">
              {isRendering ? 'Rendering…' : 'Rendered'}
              {renderErr ? <span className="text-red-600"> — {renderErr}</span> : null}
            </div>
            <div className="text-gray-400">
              {comment?.rendered ? `${comment.rendered.length} chars` : '0 chars'}
            </div>
          </div>

          <div className="border border-gray-200 rounded-lg p-3 bg-white">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Output</div>
            <div className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
              {comment?.rendered || <span className="text-gray-400 italic">(no output yet)</span>}
            </div>
          </div>

          {comment?.validation && (
            <div className="border rounded-lg p-3 bg-white">
              <div className="flex items-center justify-between mb-2">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Validation</div>
                <div className={comment.validation.valid ? "text-xs text-green-700" : "text-xs text-red-700"}>
                  {comment.validation.valid ? "Valid" : "Needs revision"}
                </div>
              </div>

              {Array.isArray(comment.validation.errors) && comment.validation.errors.length > 0 && (
                <div className="mb-2">
                  <div className="text-xs font-medium text-red-700 mb-1">Errors</div>
                  <ul className="text-xs text-red-700 list-disc pl-5 space-y-1">
                    {comment.validation.errors.map((e, idx) => (
                      <li key={idx}>{e}</li>
                    ))}
                  </ul>
                </div>
              )}

              {Array.isArray(comment.validation.warnings) && comment.validation.warnings.length > 0 && (
                <div>
                  <div className="text-xs font-medium text-amber-700 mb-1">Warnings</div>
                  <ul className="text-xs text-amber-700 list-disc pl-5 space-y-1">
                    {comment.validation.warnings.map((w, idx) => (
                      <li key={idx}>{w}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
