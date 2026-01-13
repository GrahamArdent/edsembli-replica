use rusqlite::{params, Connection, OptionalExtension};
use serde::{Deserialize, Serialize};
use tauri::Manager;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct Student {
    id: String,
    first_name: String,
    last_name: String,
    preferred_name: Option<String>,
    pronouns: Pronouns,
    needs: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Pronouns {
    subject: String,
    object: String,
    possessive: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct DraftRow {
    student_id: String,
    report_period_id: String,
    frame: String,
    section: String,
    template_id: Option<String>,
    slot_values: serde_json::Value,
    rendered_text: Option<String>,
    author: Option<String>,
    status: Option<String>,
}

fn db_path(app: &tauri::AppHandle) -> Result<std::path::PathBuf, String> {
    let dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("failed to resolve app data dir: {e}"))?;
    std::fs::create_dir_all(&dir).map_err(|e| format!("failed to create app data dir: {e}"))?;
    Ok(dir.join("vgreport.db"))
}

fn open_db(app: &tauri::AppHandle) -> Result<Connection, String> {
    let path = db_path(app)?;
    Connection::open(path).map_err(|e| format!("failed to open db: {e}"))
}

fn init_schema(conn: &Connection) -> Result<(), String> {
    conn.execute_batch(
        r#"
CREATE TABLE IF NOT EXISTS students (
  id TEXT PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  preferred_name TEXT,
  pronouns_subject TEXT,
  pronouns_object TEXT,
  pronouns_possessive TEXT,
  needs_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS report_periods (
  id TEXT PRIMARY KEY,
  name TEXT,
  board_id TEXT,
  is_active INTEGER,
  locked_at TEXT
);

CREATE TABLE IF NOT EXISTS drafts (
  id TEXT PRIMARY KEY,
  student_id TEXT NOT NULL,
  report_period_id TEXT NOT NULL,
  frame TEXT NOT NULL,
  section TEXT NOT NULL,
  template_id TEXT,
  slot_values_json TEXT NOT NULL DEFAULT '{}',
  rendered_text TEXT,
  updated_at TEXT DEFAULT (datetime('now')),
  UNIQUE(student_id, report_period_id, frame, section)
);

CREATE TABLE IF NOT EXISTS evidence_snippets (
  id TEXT PRIMARY KEY,
  student_id TEXT NOT NULL,
  text TEXT NOT NULL,
  tags_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS app_settings (
  key TEXT PRIMARY KEY,
  value_json TEXT NOT NULL,
  updated_at TEXT DEFAULT (datetime('now'))
);
"#,
    )
    .map_err(|e| format!("failed to init schema: {e}"))?;

    ensure_drafts_columns(conn)?;
    Ok(())
}

fn ensure_drafts_columns(conn: &Connection) -> Result<(), String> {
    // Phase B migration: add author/status to drafts.
    // NOTE: SQLite supports ADD COLUMN, but not IF NOT EXISTS; we must probe first.
    ensure_column(
        conn,
        "drafts",
        "author",
        "ALTER TABLE drafts ADD COLUMN author TEXT NOT NULL DEFAULT 'teacher'",
    )?;
    ensure_column(
        conn,
        "drafts",
        "status",
        "ALTER TABLE drafts ADD COLUMN status TEXT NOT NULL DEFAULT 'approved'",
    )?;
    Ok(())
}

fn ensure_column(conn: &Connection, table: &str, column: &str, ddl: &str) -> Result<(), String> {
    if column_exists(conn, table, column)? {
        return Ok(());
    }
    conn.execute(ddl, [])
        .map_err(|e| format!("failed to migrate {table}.{column}: {e}"))?;
    Ok(())
}

fn column_exists(conn: &Connection, table: &str, column: &str) -> Result<bool, String> {
    let mut stmt = conn
        .prepare(&format!("PRAGMA table_info({table})"))
        .map_err(|e| format!("failed to read schema for {table}: {e}"))?;

    let mut rows = stmt
        .query([])
        .map_err(|e| format!("failed to query table info for {table}: {e}"))?;

    while let Some(row) = rows
        .next()
        .map_err(|e| format!("failed to iterate table info for {table}: {e}"))?
    {
        let name: String = row.get(1).map_err(|e| format!("failed to read column name: {e}"))?;
        if name == column {
            return Ok(true);
        }
    }
    Ok(false)
}

#[tauri::command]
fn db_get_setting(app: tauri::AppHandle, key: String) -> Result<Option<serde_json::Value>, String> {
    let conn = open_db(&app)?;
    init_schema(&conn)?;

    let mut stmt = conn
        .prepare("SELECT value_json FROM app_settings WHERE key=?1")
        .map_err(|e| format!("failed to prepare statement: {e}"))?;

    let value_json: Option<String> = stmt
        .query_row(params![key], |row| row.get(0))
        .optional()
        .map_err(|e| format!("failed to query setting: {e}"))?;

    match value_json {
        None => Ok(None),
        Some(s) => {
            let v = serde_json::from_str::<serde_json::Value>(&s)
                .map_err(|e| format!("failed to parse setting json: {e}"))?;
            Ok(Some(v))
        }
    }
}

#[tauri::command]
fn db_set_setting(
    app: tauri::AppHandle,
    key: String,
    value: serde_json::Value,
) -> Result<(), String> {
    let conn = open_db(&app)?;
    init_schema(&conn)?;

    let value_json = serde_json::to_string(&value).map_err(|e| format!("failed to serialize json: {e}"))?;
    conn.execute(
        "INSERT INTO app_settings (key, value_json, updated_at) VALUES (?1, ?2, datetime('now')) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json, updated_at=datetime('now')",
        params![key, value_json],
    )
    .map_err(|e| format!("failed to upsert setting: {e}"))?;
    Ok(())
}

#[tauri::command]
fn db_init(app: tauri::AppHandle) -> Result<String, String> {
    let conn = open_db(&app)?;
    init_schema(&conn)?;
    Ok(db_path(&app)?.to_string_lossy().to_string())
}

#[tauri::command]
fn db_list_students(app: tauri::AppHandle) -> Result<Vec<Student>, String> {
    let conn = open_db(&app)?;
    init_schema(&conn)?;

    let mut stmt = conn
        .prepare(
            "SELECT id, first_name, last_name, preferred_name, pronouns_subject, pronouns_object, pronouns_possessive, needs_json FROM students ORDER BY last_name, first_name",
        )
        .map_err(|e| format!("failed to prepare statement: {e}"))?;

    let rows = stmt
        .query_map([], |row| {
            let needs_json: String = row.get(7)?;
            let needs: Vec<String> = serde_json::from_str(&needs_json).unwrap_or_default();

            Ok(Student {
                id: row.get(0)?,
                first_name: row.get(1)?,
                last_name: row.get(2)?,
                preferred_name: row.get(3)?,
                pronouns: Pronouns {
                    subject: row.get::<_, Option<String>>(4)?.unwrap_or_else(|| "they".to_string()),
                    object: row.get::<_, Option<String>>(5)?.unwrap_or_else(|| "them".to_string()),
                    possessive: row.get::<_, Option<String>>(6)?.unwrap_or_else(|| "their".to_string()),
                },
                needs,
            })
        })
        .map_err(|e| format!("failed to query students: {e}"))?;

    let mut out = Vec::new();
    for r in rows {
        out.push(r.map_err(|e| format!("failed to read row: {e}"))?);
    }
    Ok(out)
}

#[tauri::command]
fn db_upsert_student(app: tauri::AppHandle, student: Student) -> Result<(), String> {
    let conn = open_db(&app)?;
    init_schema(&conn)?;

    let needs_json = serde_json::to_string(&student.needs).unwrap_or_else(|_| "[]".to_string());

    conn.execute(
        r#"
INSERT INTO students (
  id, first_name, last_name, preferred_name,
  pronouns_subject, pronouns_object, pronouns_possessive,
  needs_json, created_at, updated_at
)
VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, datetime('now'), datetime('now'))
ON CONFLICT(id) DO UPDATE SET
  first_name=excluded.first_name,
  last_name=excluded.last_name,
  preferred_name=excluded.preferred_name,
  pronouns_subject=excluded.pronouns_subject,
  pronouns_object=excluded.pronouns_object,
  pronouns_possessive=excluded.pronouns_possessive,
  needs_json=excluded.needs_json,
  updated_at=datetime('now');
"#,
        params![
            student.id,
            student.first_name,
            student.last_name,
            student.preferred_name,
            student.pronouns.subject,
            student.pronouns.object,
            student.pronouns.possessive,
            needs_json,
        ],
    )
    .map_err(|e| format!("failed to upsert student: {e}"))?;

    Ok(())
}

#[tauri::command]
fn db_delete_student(app: tauri::AppHandle, student_id: String) -> Result<(), String> {
    let conn = open_db(&app)?;
    init_schema(&conn)?;

    conn.execute("DELETE FROM drafts WHERE student_id=?1", params![student_id.clone()])
        .map_err(|e| format!("failed to delete drafts: {e}"))?;
    conn.execute("DELETE FROM students WHERE id=?1", params![student_id])
        .map_err(|e| format!("failed to delete student: {e}"))?;
    Ok(())
}

#[tauri::command]
fn db_list_drafts(app: tauri::AppHandle, report_period_id: String) -> Result<Vec<DraftRow>, String> {
    let conn = open_db(&app)?;
    init_schema(&conn)?;

    let mut stmt = conn
        .prepare(
            "SELECT student_id, report_period_id, frame, section, template_id, slot_values_json, rendered_text, author, status FROM drafts WHERE report_period_id=?1",
        )
        .map_err(|e| format!("failed to prepare statement: {e}"))?;

    let rows = stmt
        .query_map(params![report_period_id], |row| {
            let slot_values_json: String = row.get(5)?;
            let slot_values: serde_json::Value =
                serde_json::from_str(&slot_values_json).unwrap_or_else(|_| serde_json::json!({}));
            Ok(DraftRow {
                student_id: row.get(0)?,
                report_period_id: row.get(1)?,
                frame: row.get(2)?,
                section: row.get(3)?,
                template_id: row.get(4)?,
                slot_values,
                rendered_text: row.get(6)?,
                author: row.get(7)?,
                status: row.get(8)?,
            })
        })
        .map_err(|e| format!("failed to query drafts: {e}"))?;

    let mut out = Vec::new();
    for r in rows {
        out.push(r.map_err(|e| format!("failed to read row: {e}"))?);
    }
    Ok(out)
}

#[tauri::command]
fn db_upsert_draft(app: tauri::AppHandle, draft: DraftRow) -> Result<(), String> {
    let conn = open_db(&app)?;
    init_schema(&conn)?;

    let id = format!(
        "{}:{}:{}:{}",
        draft.student_id, draft.report_period_id, draft.frame, draft.section
    );
    let slot_values_json = serde_json::to_string(&draft.slot_values)
        .unwrap_or_else(|_| "{}".to_string());

    let author = draft.author.unwrap_or_else(|| "teacher".to_string());
    let status = draft.status.unwrap_or_else(|| "approved".to_string());

    conn.execute(
        r#"
INSERT INTO drafts (
    id, student_id, report_period_id, frame, section, template_id,
    slot_values_json, rendered_text, author, status, updated_at
)
VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, datetime('now'))
ON CONFLICT(student_id, report_period_id, frame, section) DO UPDATE SET
  template_id=excluded.template_id,
  slot_values_json=excluded.slot_values_json,
  rendered_text=excluded.rendered_text,
    author=excluded.author,
    status=excluded.status,
  updated_at=datetime('now');
"#,
        params![
            id,
            draft.student_id,
            draft.report_period_id,
            draft.frame,
            draft.section,
            draft.template_id,
            slot_values_json,
            draft.rendered_text,
                        author,
                        status,
        ],
    )
    .map_err(|e| format!("failed to upsert draft: {e}"))?;
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            db_init,
            db_get_setting,
            db_set_setting,
            db_list_students,
            db_upsert_student,
            db_delete_student,
            db_list_drafts,
            db_upsert_draft
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
