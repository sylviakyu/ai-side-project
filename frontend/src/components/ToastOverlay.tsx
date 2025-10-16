import { memo } from "react";
import type { ReactNode } from "react";

export interface ToastMessage {
  id: string;
  title?: string;
  message: ReactNode;
}

interface ToastOverlayProps {
  toasts: ToastMessage[];
}

function ToastOverlay({ toasts }: ToastOverlayProps) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div className="toast-overlay">
      {toasts.map((toast) => (
        <div key={toast.id} className="toast">
          {toast.title && <div className="toast-title">{toast.title}</div>}
          <div className="toast-body">{toast.message}</div>
        </div>
      ))}
    </div>
  );
}

export default memo(ToastOverlay);
