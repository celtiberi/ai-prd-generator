from typing import Dict, Any

PROJECT_SUMMARY_SCHEMA = {
    "title": "string",
    "description": "string",
    "target_users": ["string"],
    "goals": ["string"],
    "key_features": ["string"]
}

FEATURE_ANALYSIS_SCHEMA = {
    "core_features": [{
        "name": "string",
        "description": "string",
        "requirements": ["string"],
        "priority": "high|medium|low",
        "dependencies": ["string"]
    }],
    "technical_requirements": [{
        "category": "string",
        "requirements": ["string"]
    }],
    "integration_points": ["string"],
    "constraints": ["string"],
    "success_metrics": ["string"]
}

def validate_project_summary(summary: Dict[str, Any]) -> bool:
    """Validate that a project summary matches the required schema"""
    try:
        assert isinstance(summary["title"], str)
        assert isinstance(summary["description"], str)
        assert isinstance(summary["target_users"], list)
        assert isinstance(summary["goals"], list)
        assert isinstance(summary["key_features"], list)
        assert all(isinstance(x, str) for x in summary["target_users"])
        assert all(isinstance(x, str) for x in summary["goals"])
        assert all(isinstance(x, str) for x in summary["key_features"])
        return True
    except (KeyError, AssertionError):
        return False 