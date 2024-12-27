import create from 'zustand';
import { Project, Feature, ProjectProgress } from '../types';

interface ProjectStore {
    project: Project | null;
    progress: ProjectProgress | null;
    setProject: (project: Project) => void;
    setProgress: (progress: ProjectProgress) => void;
    updateFeature: (feature: Feature) => void;
}

export const useProjectStore = create<ProjectStore>((set) => ({
    project: null,
    progress: null,
    setProject: (project) => set({ project }),
    setProgress: (progress) => set({ progress }),
    updateFeature: (feature) => set((state) => ({
        progress: state.progress ? {
            ...state.progress,
            features: state.progress.features.map(f => 
                f.name === feature.name ? feature : f
            )
        } : null
    })),
})); 