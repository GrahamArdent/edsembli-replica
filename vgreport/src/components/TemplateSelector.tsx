import * as React from "react"
import { Check, ChevronsUpDown, BookOpen } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { useAppStore } from "../store/useAppStore"
import { Template } from "../types"

interface TemplateSelectorProps {
  frameCanonicalId: string;
  sectionId: string;
  onSelect: (template: Template) => void;
}

export function TemplateSelector({ frameCanonicalId, sectionId, onSelect }: TemplateSelectorProps) {
  const [open, setOpen] = React.useState(false)
  const templates = useAppStore(state => state.templates)

  const filteredTemplates = templates.filter(t =>
    t.frame === frameCanonicalId && t.section === sectionId
  )

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full sm:w-[200px] justify-between text-xs h-8 border-dashed"
        >
          <div className="flex items-center gap-2 truncate">
            <BookOpen className="h-3.5 w-3.5 text-blue-600" />
            <span>Browse Templates ({filteredTemplates.length})</span>
          </div>
          <ChevronsUpDown className="ml-2 h-3 w-3 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[500px] p-0" align="start">
        <Command>
          <CommandInput placeholder="Search templates..." className="h-9" />
          <CommandList>
            <CommandEmpty>No templates found for this section.</CommandEmpty>
            <CommandGroup heading="Available Templates">
              {filteredTemplates.map((template) => (
                <CommandItem
                  key={template.id}
                  value={template.text} // Search against the text content
                  onSelect={() => {
                    onSelect(template);
                    setOpen(false);
                  }}
                  className="p-2 cursor-pointer"
                >
                  <div className="flex flex-col gap-1 w-full">
                    {/* Tiny ID label */}
                    <span className="text-[10px] text-gray-400 font-mono uppercase">
                      {template.id.split('.').pop()}
                    </span>
                    {/* Template Text */}
                    <span className="text-sm text-gray-700 leading-snug">
                      {template.text}
                    </span>
                  </div>
                  <Check
                    className={cn(
                      "ml-auto h-4 w-4",
                      "opacity-0"
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
