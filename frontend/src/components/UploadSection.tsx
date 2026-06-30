"use client";

/**
 * Upload Section Component
 *
 * Provides drag-and-drop file upload interface for contracts.
 */

import { useState } from "react";

interface UploadSectionProps {
  onUpload?: (file: File) => void;
}

export default function UploadSection({ onUpload }: UploadSectionProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
        setFileName(file.name);
        onUpload?.(file);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files.length > 0) {
      const file = files[0];
      setFileName(file.name);
      onUpload?.(file);
    }
  };

  return (
    <div className="rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-8 sm:p-12 transition-colors"
         onDragOver={handleDragOver}
         onDragLeave={handleDragLeave}
         onDrop={handleDrop}
         style={{
           borderColor: isDragging ? "#3b82f6" : undefined,
           backgroundColor: isDragging ? "#eff6ff" : undefined,
         }}>
      <div className="flex flex-col items-center justify-center gap-4">
        {/* Icon */}
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
          <svg
            className="h-8 w-8 text-blue-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3v-6"
            />
          </svg>
        </div>

        {/* Text */}
        <div className="text-center">
          <p className="text-lg font-semibold text-gray-900">
            {fileName ? (
              <span className="text-green-600">✓ {fileName}</span>
            ) : (
              <>Drag and drop your contract here</>
            )}
          </p>
          <p className="text-sm text-gray-600">
            or{" "}
            <label className="cursor-pointer font-semibold text-blue-600 hover:underline">
              browse your computer
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="hidden"
              />
            </label>
          </p>
          <p className="mt-1 text-xs text-gray-500">PDF files up to 10MB</p>
        </div>

        {/* Supported formats */}
        <div className="mt-4 flex gap-2 text-xs text-gray-600">
          <span className="rounded-full bg-white px-3 py-1">PDF</span>
        </div>
      </div>
    </div>
  );
}
