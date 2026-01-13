import { useEffect, useMemo, useRef, useState } from 'react';
import { CommentDraft, FrameId, SectionId, Student, Template } from '../types';
import { TemplateSelector } from './TemplateSelector';
import { sidecar } from '../services/sidecar';
import { useAppStore } from '../store/useAppStore';
import { Button } from './ui/button';
import { analyzeTier1 } from '../validation/tier1';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';

const EMPTY_SLOTS: Record<string, string> = {};
const EMPTY_COMMENT: CommentDraft = { slots: EMPTY_SLOTS };

const MODIFIER_PHRASES: string[] = [
  'independently',
  'with support',
  'with guidance',
  'with prompting',
  'with reminders',
  'with encouragement',
  'with peer support',
  'when provided with',
];

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
  const currentRole = useAppStore(s => s.currentRole);
  const setDraftStatus = useAppStore(s => s.setDraftStatus);
  const tier1Validation = useAppStore(s => s.tier1Validation);
  const roleLabels = useAppStore(s => s.roleLabels);

  const comment = useAppStore(s => {
    const draft = s.drafts[student.id];
    return (draft?.comments?.[frameId]?.[section.id] ?? EMPTY_COMMENT);
  });

  const author = comment?.author ?? 'teacher';
  const status = comment?.status ?? (author === 'teacher' ? 'approved' : 'draft');

  const selectedTemplate = useMemo(() => {
    if (!comment?.templateId) return undefined;
    return templates.find(t => t.id === comment.templateId);
  }, [comment?.templateId, templates]);

  const slots = comment?.slots ?? {};
  const slotKeys = selectedTemplate?.slots ?? [];

  const tier1Issues = useMemo(() => analyzeTier1(comment?.rendered ?? '', tier1Validation), [comment?.rendered, tier1Validation]);

  const repetitionCount = useAppStore(s => {
    const current = (s.drafts[student.id]?.comments?.[frameId]?.[section.id]?.rendered ?? '').trim();
    if (!current) return 0;
    let count = 0;
    for (const st of s.students) {
      const other = (s.drafts[st.id]?.comments?.[frameId]?.[section.id]?.rendered ?? '').trim();
      if (other && other === current) count++;
    }
    return count;
  });

  const [isRendering, setIsRendering] = useState(false);
  const [renderErr, setRenderErr] = useState<string | null>(null);
  const renderTimer = useRef<number | null>(null);

  const [openModifierFor, setOpenModifierFor] = useState<string | null>(null);
  const slotRefs = useRef<Record<string, HTMLTextAreaElement | null>>({});

  const insertModifier = (key: string, phrase: string) => {
    const current = String((slots as any)[key] ?? '');
    const el = slotRefs.current[key];
    const start = typeof el?.selectionStart === 'number' ? el.selectionStart : current.length;
    const end = typeof el?.selectionEnd === 'number' ? el.selectionEnd : current.length;

    const before = current.slice(0, start);
    const after = current.slice(end);

    const needsSpace = before.length > 0 && !/[\s\n]$/.test(before);
    const insertion = (needsSpace ? ' ' : '') + phrase;
    const next = before + insertion + after;

    setSlotValue(key, next);
    setOpenModifierFor(null);

    requestAnimationFrame(() => {
      const nextEl = slotRefs.current[key];
      if (!nextEl) return;
      nextEl.focus();
      const pos = start + insertion.length;
      try {
        nextEl.setSelectionRange(pos, pos);
      } catch {
        // ignore
      }
    });
  };

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
          slots: { ...(comment.slots || {}) },
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

        <div className="flex items-center gap-2">
          <span
            className={
              author === 'teacher'
                ? 'text-[11px] px-2 py-0.5 rounded border bg-blue-50 border-blue-200 text-blue-800'
                : 'text-[11px] px-2 py-0.5 rounded border bg-amber-50 border-amber-200 text-amber-800'
            }
            title="Draft author"
          >
            {author === 'teacher' ? roleLabels.teacher : roleLabels.ece}
          </span>
          <span
            className={
              status === 'approved'
                ? 'text-[11px] px-2 py-0.5 rounded border bg-green-50 border-green-200 text-green-800'
                : 'text-[11px] px-2 py-0.5 rounded border bg-gray-50 border-gray-200 text-gray-700'
            }
            title="Approval status"
          >
            {status === 'approved' ? 'Approved' : 'Draft'}
          </span>

          {currentRole === 'teacher' && author === 'ece' && (
            <Button
              variant={status === 'approved' ? 'outline' : 'default'}
              size="sm"
              onClick={() => setDraftStatus(student.id, frameId, section.id, status === 'approved' ? 'draft' : 'approved')}
              title={status === 'approved' ? 'Mark as unapproved' : 'Approve this box'}
            >
              {status === 'approved' ? 'Unapprove' : 'Approve'}
            </Button>
          )}

          <TemplateSelector
              frameCanonicalId={frameCanonicalId}
              sectionId={section.id}
              onSelect={handleTemplateSelect}
              selectedTemplateId={comment?.templateId}
              onClear={comment?.templateId ? handleClear : undefined}
          />
        </div>
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
              <div className="flex items-center justify-between gap-2">
                <label className="text-xs font-medium text-gray-700">
                  {key.replace(/_/g, ' ')}
                </label>

                <Popover
                  open={openModifierFor === key}
                  onOpenChange={(v) => setOpenModifierFor(v ? key : null)}
                >
                  <PopoverTrigger asChild>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="h-7 px-2 text-[11px]"
                      disabled={!selectedTemplate}
                      title="Insert a common modifier phrase"
                    >
                      Insert modifier
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-56 p-2" align="end">
                    <div className="text-[11px] text-muted-foreground mb-1">Common phrases</div>
                    <div className="flex flex-col">
                      {MODIFIER_PHRASES.map((phrase) => (
                        <Button
                          key={phrase}
                          type="button"
                          variant="ghost"
                          className="justify-start h-8 px-2 text-xs"
                          onClick={() => insertModifier(key, phrase)}
                        >
                          {phrase}
                        </Button>
                      ))}
                    </div>
                  </PopoverContent>
                </Popover>
              </div>
              <textarea
                value={String((slots as any)[key] ?? '')}
                onChange={(e) => setSlotValue(key, e.target.value)}
                ref={(el) => {
                  slotRefs.current[key] = el;
                }}
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

          {(tier1Issues.length > 0 || repetitionCount >= 2) && (
            <div className="border rounded-lg p-3 bg-white">
              <div className="flex items-center justify-between mb-2">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Box-fit (Tier 1)</div>
                <div className="text-[11px] text-muted-foreground">Heuristic • warn-only</div>
              </div>

              {repetitionCount >= 2 && (
                <div className="text-xs text-amber-700 mb-2">
                  Same output appears in {repetitionCount} students for this box.
                </div>
              )}

              {tier1Issues.length > 0 && (
                <ul className="text-xs list-disc pl-5 space-y-1">
                  {tier1Issues.map((iss) => (
                    <li
                      key={iss.code}
                      className={
                        iss.severity === 'error'
                          ? 'text-red-700'
                          : iss.severity === 'warning'
                            ? 'text-amber-700'
                            : 'text-gray-600'
                      }
                    >
                      {iss.message}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

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
