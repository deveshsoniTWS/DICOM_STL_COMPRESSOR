const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CompressionStats {
  format?: string;
  mode?: string;
  originalSizeKB?: string;
  compressedSizeKB?: string;
  decompressedSizeKB?: string;
  compressionRatio?: string;
  frames?: string;
  triangles?: string;
}

export function formatFileSize(kb: string | number): string {
  const sizeInKB = typeof kb === 'string' ? parseFloat(kb) : kb;
  if (sizeInKB >= 1024) {
    return `${(sizeInKB / 1024).toFixed(2)} MB`;
  }
  return `${sizeInKB.toFixed(2)} KB`;
}

export async function compressFile(
  file: File,
  mode: 'lossless' | 'lossy'
): Promise<{ blob: Blob; stats: CompressionStats; filename: string }> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('mode', mode);

  const response = await fetch(`${API_BASE_URL}/compress`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Compression failed');
  }

  const stats: CompressionStats = {
    format: response.headers.get('X-Format') || undefined,
    mode: response.headers.get('X-Mode') || undefined,
    originalSizeKB: response.headers.get('X-Original-Size-KB') || undefined,
    compressedSizeKB: response.headers.get('X-Compressed-Size-KB') || undefined,
    compressionRatio: response.headers.get('X-Compression-Ratio') || undefined,
    frames: response.headers.get('X-Frames') || undefined,
    triangles: response.headers.get('X-Triangles') || undefined,
  };

  const blob = await response.blob();
  const contentDisposition = response.headers.get('Content-Disposition');
  const filename = contentDisposition?.split('filename=')[1] || 'compressed.medzip';

  return { blob, stats, filename };
}

export async function decompressFile(
  file: File
): Promise<{ blob: Blob; stats: CompressionStats; filename: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/decompress`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Decompression failed');
  }

  const stats: CompressionStats = {
    format: response.headers.get('X-Format') || undefined,
    mode: response.headers.get('X-Mode') || undefined,
    compressedSizeKB: response.headers.get('X-Compressed-Size-KB') || undefined,
    decompressedSizeKB: response.headers.get('X-Decompressed-Size-KB') || undefined,
    frames: response.headers.get('X-Frames') || undefined,
    triangles: response.headers.get('X-Triangles') || undefined,
  };

  const blob = await response.blob();
  const contentDisposition = response.headers.get('Content-Disposition');
  const filename = contentDisposition?.split('filename=')[1] || 'decompressed.dcm';

  return { blob, stats, filename };
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
