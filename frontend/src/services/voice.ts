import { api } from './api';

export interface TranscriptionResponse {
  success: boolean;
  transcript: string;
}

export const voiceService = {
  async transcribe(audioBlob: Blob): Promise<TranscriptionResponse> {
    const formData = new FormData();
    const extension = audioBlob.type.includes('webm') ? 'webm' : 'wav';
    formData.append('audio', audioBlob, `recording.${extension}`);

    const response = await api.post('/api/mcp/transcribe/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
  },
};
