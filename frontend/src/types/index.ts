export interface Project {
    title: string;
    description: string;
    target_users: string[];
    goals: string[];
}

export interface ProjectInitResponse {
    status: string;
    proposed_objectives: string[];
}

export interface ObjectiveApproval {
    objectives: string[];
    modifications?: string[];
}

export interface Feature {
    name: string;
    description: string;
    requirements: string[];
    dependencies: string[];
    priority: 'high' | 'medium' | 'low';
    status: 'draft' | 'validated' | 'refined';
    feedback?: string;
}

export interface ProjectProgress {
    status: string;
    features: Feature[];
    validation_results?: ValidationResult[];
}

export interface ValidationResult {
    rule: string;
    score: number;
    feedback: string;
} 