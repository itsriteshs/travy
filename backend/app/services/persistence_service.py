import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.core.config import settings

DB_FILE = "./travy.db"

class PersistenceService:
    @classmethod
    def get_connection(cls):
        db_path = settings.DATABASE_URL
        if db_path.startswith("sqlite:///"):
            path = db_path.replace("sqlite:///", "")
        else:
            path = DB_FILE
        # Ensure parent directory exists
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        
        # Check if table exists
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_call_logs'")
            row = cursor.fetchone()
            if not row:
                cls._create_tables(conn)
        finally:
            cursor.close()
            
        return conn

    @classmethod
    def _create_tables(cls, conn):
        cursor = conn.cursor()
        
        # 1. sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                budget_limit REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. planner_requests
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planner_requests (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                original_prompt TEXT,
                budget_mode TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. analysis_results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id TEXT PRIMARY KEY,
                request_id TEXT UNIQUE,
                security_json TEXT,
                intent_json TEXT,
                parsed_json TEXT,
                missing_fields_json TEXT,
                complexity_json TEXT,
                budget_json TEXT,
                context_json TEXT,
                route_decision_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. itinerary_results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itinerary_results (
                id TEXT PRIMARY KEY,
                request_id TEXT UNIQUE,
                result_json TEXT,
                validation_json TEXT,
                api_evidence_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 5. routing_traces
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routing_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT,
                step_number INTEGER,
                task TEXT,
                route TEXT,
                status TEXT,
                cost_usd REAL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 6. api_call_logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_call_logs (
                id TEXT PRIMARY KEY,
                request_id TEXT,
                provider TEXT,
                endpoint_name TEXT,
                status TEXT,
                latency_ms INTEGER,
                error_message TEXT,
                cost_usd REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 7. budget_ledger
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budget_ledger (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                request_id TEXT,
                provider TEXT,
                model_id TEXT,
                estimated_cost_usd REAL,
                actual_cost_usd REAL,
                usage_source TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 8. integration_health_checks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integration_health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                service_name TEXT,
                status TEXT,
                latency_ms INTEGER,
                details_json TEXT
            )
        """)
        
        conn.commit()

    @classmethod
    def init_db(cls):
        conn = cls.get_connection()
        conn.close()

    @classmethod
    def save_request(cls, request_id: str, session_id: str, prompt: str, budget_mode: str):
        conn = cls.get_connection()
        cursor = conn.cursor()
        # Ensure session exists
        cursor.execute("INSERT OR IGNORE INTO sessions (session_id, budget_limit) VALUES (?, 2.0)", (session_id,))
        cursor.execute("""
            INSERT OR REPLACE INTO planner_requests (id, session_id, original_prompt, budget_mode)
            VALUES (?, ?, ?, ?)
        """, (request_id, session_id, prompt, budget_mode))
        conn.commit()
        conn.close()

    @classmethod
    def save_analysis(cls, analysis_id: str, request_id: str, security: dict, intent: dict, parsed: dict, missing_fields: list, complexity: dict, budget: dict, context: dict, route_decision: dict):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO analysis_results 
            (id, request_id, security_json, intent_json, parsed_json, missing_fields_json, complexity_json, budget_json, context_json, route_decision_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_id,
            request_id,
            json.dumps(security),
            json.dumps(intent),
            json.dumps(parsed),
            json.dumps(missing_fields),
            json.dumps(complexity),
            json.dumps(budget),
            json.dumps(context),
            json.dumps(route_decision)
        ))
        conn.commit()
        conn.close()

    @classmethod
    def get_analysis(cls, request_id: str) -> Optional[Dict[str, Any]]:
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analysis_results WHERE request_id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row["id"],
            "request_id": row["request_id"],
            "security": json.loads(row["security_json"]),
            "intent": json.loads(row["intent_json"]),
            "parsed": json.loads(row["parsed_json"]),
            "missing_fields": json.loads(row["missing_fields_json"]),
            "complexity": json.loads(row["complexity_json"]),
            "budget": json.loads(row["budget_json"]),
            "context": json.loads(row["context_json"]),
            "route_decision": json.loads(row["route_decision_json"]),
            "created_at": row["created_at"]
        }

    @classmethod
    def save_itinerary(cls, result_id: str, request_id: str, result: dict, validation: dict, api_evidence: dict):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO itinerary_results (id, request_id, result_json, validation_json, api_evidence_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            result_id,
            request_id,
            json.dumps(result),
            json.dumps(validation),
            json.dumps(api_evidence)
        ))
        conn.commit()
        conn.close()

    @classmethod
    def get_itinerary(cls, request_id: str) -> Optional[Dict[str, Any]]:
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM itinerary_results WHERE request_id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row["id"],
            "request_id": row["request_id"],
            "result": json.loads(row["result_json"]),
            "validation": json.loads(row["validation_json"]),
            "api_evidence": json.loads(row["api_evidence_json"]),
            "created_at": row["created_at"]
        }

    @classmethod
    def save_trace(cls, request_id: str, step_number: int, task: str, route: str, status: str, cost_usd: float, reason: str):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO routing_traces (request_id, step_number, task, route, status, cost_usd, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (request_id, step_number, task, route, status, cost_usd, reason))
        conn.commit()
        conn.close()

    @classmethod
    def get_traces(cls, request_id: str) -> List[Dict[str, Any]]:
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM routing_traces WHERE request_id = ? ORDER BY step_number ASC", (request_id,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "step": r["step_number"],
                "task": r["task"],
                "route": r["route"],
                "status": r["status"],
                "cost_usd": r["cost_usd"],
                "reason": r["reason"]
            }
            for r in rows
        ]

    @classmethod
    def save_api_call_log(cls, log_id: str, request_id: str, provider: str, endpoint_name: str, status: str, latency_ms: int, error_message: str, cost_usd: float):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api_call_logs (id, request_id, provider, endpoint_name, status, latency_ms, error_message, cost_usd)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (log_id, request_id, provider, endpoint_name, status, latency_ms, error_message, cost_usd))
        conn.commit()
        conn.close()

    @classmethod
    def save_budget_ledger(cls, ledger_id: str, session_id: str, request_id: str, provider: str, model_id: str, estimated_cost_usd: float, actual_cost_usd: float, usage_source: str, input_tokens: int, output_tokens: int):
        conn = cls.get_connection()
        cursor = conn.cursor()
        # Ensure session exists
        cursor.execute("INSERT OR IGNORE INTO sessions (session_id, budget_limit) VALUES (?, 2.0)", (session_id,))
        cursor.execute("""
            INSERT INTO budget_ledger (id, session_id, request_id, provider, model_id, estimated_cost_usd, actual_cost_usd, usage_source, input_tokens, output_tokens)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ledger_id, session_id, request_id, provider, model_id, estimated_cost_usd, actual_cost_usd, usage_source, input_tokens, output_tokens))
        conn.commit()
        conn.close()

    @classmethod
    def get_api_calls(cls, request_id: str) -> List[Dict[str, Any]]:
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM api_call_logs WHERE request_id = ? ORDER BY created_at ASC", (request_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def get_budget_ledger_summary(cls, session_id: str) -> Dict[str, Any]:
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Get limit
        cursor.execute("SELECT budget_limit FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        budget_limit = row["budget_limit"] if row else 2.0
        
        # Sum actual costs
        cursor.execute("SELECT SUM(actual_cost_usd) as total_actual, SUM(estimated_cost_usd) as total_est FROM budget_ledger WHERE session_id = ?", (session_id,))
        cost_row = cursor.fetchone()
        
        actual_used = cost_row["total_actual"] if cost_row and cost_row["total_actual"] is not None else 0.0
        estimated_used = cost_row["total_est"] if cost_row and cost_row["total_est"] is not None else 0.0
        
        # Get last call
        cursor.execute("SELECT * FROM budget_ledger WHERE session_id = ? ORDER BY created_at DESC LIMIT 1", (session_id,))
        last_row = cursor.fetchone()
        
        conn.close()
        
        last_call = None
        if last_row:
            last_call = {
                "request_id": last_row["request_id"],
                "model_id": last_row["model_id"],
                "input_tokens": last_row["input_tokens"],
                "output_tokens": last_row["output_tokens"],
                "actual_cost_usd": last_row["actual_cost_usd"]
            }
            
        return {
            "total_budget_usd": budget_limit,
            "estimated_used_usd": round(estimated_used, 4),
            "actual_used_usd": round(actual_used, 4),
            "remaining_usd": round(budget_limit - actual_used, 4),
            "last_call": last_call
        }

    @classmethod
    def get_all_requests_and_results(cls, session_id: str) -> Dict[str, Any]:
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, original_prompt, budget_mode, created_at FROM planner_requests WHERE session_id = ? ORDER BY created_at DESC", (session_id,))
        requests = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute("""
            SELECT ir.id, ir.request_id, ir.result_json, ir.created_at 
            FROM itinerary_results ir
            JOIN planner_requests pr ON ir.request_id = pr.id
            WHERE pr.session_id = ?
            ORDER BY ir.created_at DESC
        """, (session_id,))
        results = []
        for r in cursor.fetchall():
            results.append({
                "id": r["id"],
                "request_id": r["request_id"],
                "result": json.loads(r["result_json"]),
                "created_at": r["created_at"]
            })
            
        conn.close()
        return {
            "requests": requests,
            "results": results
        }

    @classmethod
    def save_health_check(cls, service_name: str, status: str, latency_ms: int, details: dict):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO integration_health_checks (service_name, status, latency_ms, details_json)
            VALUES (?, ?, ?, ?)
        """, (service_name, status, latency_ms, json.dumps(details)))
        conn.commit()
        conn.close()

    @classmethod
    def reset_db(cls):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS sessions")
        cursor.execute("DROP TABLE IF EXISTS planner_requests")
        cursor.execute("DROP TABLE IF EXISTS analysis_results")
        cursor.execute("DROP TABLE IF EXISTS itinerary_results")
        cursor.execute("DROP TABLE IF EXISTS routing_traces")
        cursor.execute("DROP TABLE IF EXISTS api_call_logs")
        cursor.execute("DROP TABLE IF EXISTS budget_ledger")
        cursor.execute("DROP TABLE IF EXISTS integration_health_checks")
        conn.commit()
        conn.close()
        cls.init_db()
