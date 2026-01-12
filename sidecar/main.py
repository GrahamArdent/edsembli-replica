import io
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from embedded_templates import EMBEDDED_TEMPLATES

from lib.assembly import fill_slots

# Configure logging - strictly to stderr so stdout remains clean for IPC
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("vgreport.engine")

# Determine PROJECT_ROOT based on whether we are running as a script or frozen exe
_meipass = getattr(sys, "_MEIPASS", None)
if os.environ.get("VGREPORT_DEBUG") == "1":
    logger.info("=== STARTUP DEBUG ===")
    logger.info(f"sys.frozen = {getattr(sys, 'frozen', False)}")
    logger.info(f"sys.executable = {sys.executable}")
    logger.info(f"sys._MEIPASS exists = {_meipass is not None}")
    if _meipass is not None:
        logger.info(f"sys._MEIPASS = {_meipass}")

if getattr(sys, "frozen", False) and _meipass is not None:
    # Running as PyInstaller executable
    PROJECT_ROOT = Path(_meipass)
    logger.info(f"Running in FROZEN mode. Root: {PROJECT_ROOT}")

    # DEBUG: List directory contents to verify bundling
    if os.environ.get("VGREPORT_DEBUG") == "1":
        try:
            logger.info(f"Checking directory contents of: {PROJECT_ROOT}")
            for item in PROJECT_ROOT.iterdir():
                if item.is_dir():
                    logger.info(f" [DIR]  {item.name}")
                    if item.name == "templates":
                        for t in item.iterdir():
                            logger.info(f"   -> {t.name}")
                else:
                    logger.info(f" [FILE] {item.name}")
        except Exception as e:
            logger.error(f"Failed to list directory contents: {e}")

else:
    # Running as python script (dev mode)
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    logger.info(f"Running in DEV mode. Root: {PROJECT_ROOT}")

sys.path.insert(0, str(PROJECT_ROOT))

# Force UTF-8 for stdin/stdout (critical for Windows)
# In --windowed mode, stdin/stdout may be None, so we must check first
if sys.platform == "win32":
    if sys.stdin is not None:
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
    if sys.stdout is not None:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class TemplateManager:
    def __init__(self):
        self.templates: dict[str, Any] = {}
        self._load_templates()

    def _load_templates(self):
        """Load templates from embedded Python data."""
        try:
            logger.info("Loading embedded templates...")
            for item in EMBEDDED_TEMPLATES:
                if "id" in item:
                    self.templates[item["id"]] = item
            logger.info(f"Loaded {len(self.templates)} templates from embedded data")
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")

    def get_template(self, template_id: str) -> dict[str, Any] | None:
        return self.templates.get(template_id)

    def list_templates(self, filters: dict[str, str]) -> list[dict[str, Any]]:
        result = []
        for t in self.templates.values():
            # Apply filters (basic exact match)
            match = True
            for key, value in filters.items():
                if t.get(key) != value:
                    match = False
                    break
            if match:
                result.append(t)
        return result


# Global singleton placeholder
template_manager = None


def send_response(request_id: str, result: Any = None, error: dict[str, Any] | None = None):
    """Send a strictly formatted JSON response to stdout."""

    response = {
        "id": request_id,
        "result": result,
        "error": error,
    }
    try:
        json_str = json.dumps(response, ensure_ascii=False)
        sys.stdout.write(json_str + "\n")
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"Failed to serialize response: {e}")
        # Last ditch effort to send error
        error_response = {"id": request_id, "result": None, "error": {"code": "SERIALIZATION_ERROR", "message": str(e)}}
        sys.stdout.write(json.dumps(error_response) + "\n")
        sys.stdout.flush()


def _require_template_manager() -> "TemplateManager":
    if template_manager is None:
        raise RuntimeError("Template manager not initialized")
    return template_manager


def handle_health(params: dict[str, Any]) -> dict[str, Any]:
    return {"status": "ok", "version": "0.1.0"}


def handle_list_templates(params: dict[str, Any]) -> dict[str, Any]:
    templates = _require_template_manager().list_templates(params)
    return {"templates": templates}


def handle_debug_info(params: dict[str, Any]) -> dict[str, Any]:
    meipass = getattr(sys, "_MEIPASS", None)
    frozen = bool(getattr(sys, "frozen", False))
    try:
        embedded_len = len(EMBEDDED_TEMPLATES)
    except Exception:
        embedded_len = -1

    tm = template_manager
    loaded_len = -1
    if tm is not None:
        try:
            loaded_len = len(tm.templates)
        except Exception:
            loaded_len = -1

    return {
        "frozen": frozen,
        "executable": sys.executable,
        "meipass": str(meipass) if meipass is not None else None,
        "project_root": str(PROJECT_ROOT),
        "cwd": os.getcwd(),
        "argv": list(sys.argv),
        "embedded_templates_len": embedded_len,
        "loaded_templates_len": loaded_len,
    }


def handle_render_comment(params: dict[str, Any]) -> dict[str, Any]:
    template_id = params.get("template_id")
    slots = params.get("slots", {})

    if not template_id:
        raise ValueError("Missing 'template_id'")

    template = _require_template_manager().get_template(template_id)
    if not template:
        raise ValueError(f"Template not found: {template_id}")

    # Use lib.assembly to fill slots
    result = fill_slots(template, slots)

    if not result.success:
        # Return validation errors in the error structure?
        # Or as a successful response with validation flags?
        # The spec says: { text, char_count, validation }
        # So we proceed even if validation fails, if possible, or return empty text
        pass

    text = result.filled_text or ""

    return {
        "text": text,
        "char_count": len(text),
        "validation": {"valid": result.success, "errors": result.errors, "warnings": result.warnings},
    }


def main():
    global template_manager
    logger.info(f"VGReport Engine starting. Root: {PROJECT_ROOT}")

    # Initialize components
    logger.info("Initializing TemplateManager...")
    template_manager = TemplateManager()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            line = line.strip()
            if not line:
                continue

            try:
                message = json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                continue

            request_id = message.get("id")
            method = message.get("method")
            params = message.get("params", {})

            if not request_id or not method:
                logger.error("Message missing id or method")
                continue

            logger.debug(f"Received request: {method} ({request_id})")

            try:
                if method == "health":
                    result = handle_health(params)
                elif method == "list_templates":
                    result = handle_list_templates(params)
                elif method == "debug_info":
                    result = handle_debug_info(params)
                elif method == "render_comment":
                    result = handle_render_comment(params)
                else:
                    raise ValueError(f"Unknown method: {method}")

                send_response(request_id, result=result)

            except Exception as e:
                logger.error(f"Error handling {method}: {e}", exc_info=True)
                send_response(request_id, error={"code": "INTERNAL_ERROR", "message": str(e)})

        except KeyboardInterrupt:
            logger.info("Stopping engine via KeyboardInterrupt")
            break
        except Exception as e:
            logger.critical(f"Fatal engine error: {e}", exc_info=True)
            break


if __name__ == "__main__":
    main()
