export interface IQuestion {
  question: string;
  correct_answer: string;
  student_answer: string;
  options?: string[];
}

export interface IEvaluation {
  score: number;
  strengths: string[];
  weak_areas: string[];
  level: string;
}

export interface IGeneratedContent {
  type: 'performance_analysis' | 'solution' | 'advanced_challenges';
  content: string;
}

export interface IRoadmap {
  title: string;
  content: string;
}

export interface IAnalysisResult {
  status: string;
  round: 1 | 2;
  evaluation?: IEvaluation;
  round_2_evaluation?: IEvaluation;
  generated_content: IGeneratedContent;
  roadmap: IRoadmap;
  questions?: IQuestion[];
  round_1_score?: number;
  can_proceed_to_round_2?: boolean;
}
