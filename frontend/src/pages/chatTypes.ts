
export type ListItem = {
  title: string;
  subtitle?: string | null;
  tags?: string[];
  details?: string | null;
};

export type ListAnswer = {
  type: "list";
  intro?: string | null;
  items: ListItem[];
};

export type CountAnswer = {
  type: "count";
  number: number;
  label: string;
  items: { title: string; subtitle?: string | null }[];
};

export type OverviewSection = {
  label: string;
  text: string;
};

export type OverviewAnswer = {
  type: "overview";
  summary: string;
  sections: OverviewSection[];
};

export type FactAnswer = {
  type: "fact";
  text: string;
};

export type StructuredAnswer =
  | ListAnswer
  | CountAnswer
  | OverviewAnswer
  | FactAnswer;

export type ChatResponse = {
  document_id: number;
  session_id?: number;
  answer: StructuredAnswer;
  sources: {
    chunk_id: number;
    chunk_index: number;
    distance: number;
  }[];
};

export type Message = {
  role: "user" | "assistant";
  content: string | StructuredAnswer;
};

export type ChatHistoryMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatHistoryResponse = {
  session_id: number;
  messages: ChatHistoryMessage[];
};

