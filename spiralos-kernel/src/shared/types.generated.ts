export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: {
      proposals: {
        Row: {
          id: string;
          title: string;
          body: string;
          proposer: string | null;
          category: string | null;
          impact_radius: number | null;
          amount: number | null;
          status: 'pending' | 'approved' | 'flagged' | 'rejected' | 'in_review';
          risk_score: number | null;
          risk_level: 'low' | 'medium' | 'high' | null;
          ssd_decision: 'approve' | 'reject' | 'needs_human_review' | null;
          findings: Json | null;
          created_at: string;
          reviewed_at: string | null;
        };
        Insert: Partial<Database['public']['Tables']['proposals']['Row']>;
        Update: Partial<Database['public']['Tables']['proposals']['Row']>;
      };
      proposal_events: {
        Row: {
          id: number;
          proposal_id: string;
          event_type: string;
          payload: Json;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['proposal_events']['Row'], 'id' | 'created_at'> & {
          created_at?: string;
        };
        Update: Partial<Database['public']['Tables']['proposal_events']['Row']>;
      };
      events: {
        Row: {
          id: string;
          type: string;
          severity: 'low' | 'medium' | 'high' | 'critical';
          description: string | null;
          metadata: Json | null;
          impact_score: number | null;
          occurred_at: string | null;
          created_at: string;
          witnessed_by: string | null;
        };
        Insert: Partial<Database['public']['Tables']['events']['Row']>;
        Update: Partial<Database['public']['Tables']['events']['Row']>;
      };
      scar_index_state: {
        Row: {
          id: number;
          score: number;
          trend: 'up' | 'down' | 'flat';
          sample_size: number;
          window_hours: number;
          updated_at: string;
        };
        Insert: Partial<Database['public']['Tables']['scar_index_state']['Row']>;
        Update: Partial<Database['public']['Tables']['scar_index_state']['Row']>;
      };
      ssd_errors: {
        Row: {
          id: number;
          proposal_id: string | null;
          error_message: string;
          stacktrace: string | null;
          context: Json | null;
          created_at: string;
        };
        Insert: Partial<Database['public']['Tables']['ssd_errors']['Row']>;
        Update: Partial<Database['public']['Tables']['ssd_errors']['Row']>;
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
    CompositeTypes: Record<string, never>;
  };
}
