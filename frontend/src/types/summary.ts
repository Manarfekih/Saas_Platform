
export interface SummaryItem {
  name: string;
  description?: string;
}

export interface SummarySection {
  title: string;
  items: SummaryItem[];
}

export interface KeyInformation {
  people: string[];
  organizations: string[];
  dates: string[];
  amounts: string[];
}

export interface Statistics {
  total_items: number;
  total_pages: number;
  word_count: number;
  character_count: number;
  paragraph_count: number;
  generated_at: string;
}

export interface DocumentSummary {
  title: string;
  document_type: string;
  overview: string;
  key_information: KeyInformation;
  sections: SummarySection[];
  statistics: Statistics;
}

export interface DocumentSummaryResponse {
  document_id: number;
  document_type: string;
  summary: DocumentSummary;
  summary_file_name: string | null;
  total_chunks: number;
  page_count: number;
}
