// Board configuration types and loader
import ncdsb from './boards/ncdsb.json';
import tcdsb from './boards/tcdsb.json';

export interface BoardConfig {
  id: string;
  board_name: string;
  board_abbrev: string;
  char_limits: {
    per_section_min: number;
    per_section_max: number;
    total_min: number;
    total_max: number;
  };
  export_settings: {
    csv_delimiter: string;
    csv_encoding: string;
    include_metadata: boolean;
    include_french: boolean;
  };
  terminology: {
    kindergarten: string;
    col: string;
    teacher: string;
  };
}

const BOARD_CONFIGS: Record<string, BoardConfig> = {
  ncdsb,
  tcdsb,
};

export function loadBoardConfig(boardId: string): BoardConfig | null {
  return BOARD_CONFIGS[boardId] || null;
}

export function getAvailableBoardIds(): string[] {
  return Object.keys(BOARD_CONFIGS);
}
