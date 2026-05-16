"use client";

import React, { useState } from "react";
import { File, Folder, ChevronRight, ChevronDown, Download, Code, Copy, Check } from "lucide-react";

interface FileObject {
  path: string;
  content: string;
}

interface CodeFilesViewProps {
  files: FileObject[];
  zipUrl?: string;
}

interface FileTreeItem {
  name: string;
  path: string;
  type: "file" | "folder";
  children?: FileTreeItem[];
  content?: string;
}

const CodeFilesView: React.FC<CodeFilesViewProps> = ({ files, zipUrl }) => {
  const [selectedFilePath, setSelectedFilePath] = useState<string | null>(
    files.length > 0 ? files[0].path : null
  );
  const [copied, setCopied] = useState(false);

  // Build file tree
  const buildFileTree = (files: FileObject[]): FileTreeItem[] => {
    const root: FileTreeItem[] = [];

    files.forEach((file) => {
      const parts = file.path.split("/");
      let currentLevel = root;

      parts.forEach((part, index) => {
        const isFile = index === parts.length - 1;
        const currentPath = parts.slice(0, index + 1).join("/");
        let existing = currentLevel.find((item) => item.name === part);

        if (!existing) {
          existing = {
            name: part,
            path: currentPath,
            type: isFile ? "file" : "folder",
            children: isFile ? undefined : [],
            content: isFile ? file.content : undefined,
          };
          currentLevel.push(existing);
          // Sort folders first, then files alphabetically
          currentLevel.sort((a, b) => {
            if (a.type !== b.type) return a.type === "folder" ? -1 : 1;
            return a.name.localeCompare(b.name);
          });
        }

        if (!isFile) {
          currentLevel = existing.children!;
        }
      });
    });

    return root;
  };

  const fileTree = buildFileTree(files);
  const selectedFile = files.find((f) => f.path === selectedFilePath);

  const copyToClipboard = () => {
    if (selectedFile) {
      navigator.clipboard.writeText(selectedFile.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const downloadFile = (file: FileObject) => {
    const blob = new Blob([file.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const fileName = file.path.split("/").pop() || "file.txt";
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const FileTreeItemComponent: React.FC<{ item: FileTreeItem; depth: number }> = ({ item, depth }) => {
    const [isOpen, setIsOpen] = useState(true);
    const isSelected = selectedFilePath === item.path;

    if (item.type === "folder") {
      return (
        <div>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center space-x-2 w-full text-left py-1 px-2 hover:bg-surface rounded text-sm text-muted-foreground transition-colors"
            style={{ paddingLeft: `${depth * 12 + 8}px` }}
          >
            {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            <Folder className="w-4 h-4 text-primary/70" />
            <span className="truncate">{item.name}</span>
          </button>
          {isOpen && item.children && (
            <div>
              {item.children.map((child) => (
                <FileTreeItemComponent key={child.path} item={child} depth={depth + 1} />
              ))}
            </div>
          )}
        </div>
      );
    }

    return (
      <button
        onClick={() => setSelectedFilePath(item.path)}
        className={`flex items-center space-x-2 w-full text-left py-1 px-2 rounded text-sm transition-all ${
          isSelected ? "bg-primary/20 text-primary font-bold" : "hover:bg-surface text-muted-foreground"
        }`}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
      >
        <File className={`w-4 h-4 ${isSelected ? "text-primary" : "text-muted-foreground/50"}`} />
        <span className="truncate">{item.name}</span>
      </button>
    );
  };

  return (
    <div className="flex flex-col h-[600px] border border-border rounded-lg overflow-hidden bg-background">
      {/* Toolbar */}
      <div className="bg-surface border-b border-border p-3 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Code className="w-5 h-5 text-warning" />
          <span className="font-bold text-sm">Generated Source Code</span>
        </div>
        {zipUrl && (
          <a
            href={zipUrl}
            download
            className="flex items-center space-x-2 text-xs bg-warning text-background px-3 py-1.5 rounded font-bold hover:bg-warning/90 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download All (ZIP)</span>
          </a>
        )}
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-64 border-r border-border overflow-y-auto bg-surface/30 p-2 custom-scrollbar">
          {fileTree.map((item) => (
            <FileTreeItemComponent key={item.path} item={item} depth={0} />
          ))}
        </div>

        {/* Editor Area */}
        <div className="flex-1 flex flex-col overflow-hidden bg-[#0d1117]">
          {selectedFile ? (
            <>
              <div className="bg-[#161b22] border-b border-[#30363d] px-4 py-2 flex items-center justify-between">
                <span className="text-xs font-mono text-muted-foreground truncate">{selectedFile.path}</span>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={copyToClipboard}
                    className="p-1.5 hover:bg-white/10 rounded transition-colors text-muted-foreground"
                    title="Copy code"
                  >
                    {copied ? <Check className="w-4 h-4 text-success" /> : <Copy className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => downloadFile(selectedFile)}
                    className="p-1.5 hover:bg-white/10 rounded transition-colors text-muted-foreground"
                    title="Download file"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="flex-1 overflow-auto p-4 custom-scrollbar">
                <pre className="text-sm font-mono text-[#e6edf3] leading-relaxed">
                  <code>{selectedFile.content}</code>
                </pre>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              <p>Select a file to view content</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CodeFilesView;
