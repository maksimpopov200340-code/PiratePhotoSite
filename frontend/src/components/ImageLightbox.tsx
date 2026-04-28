import { useEffect } from "react";


interface ImageLightboxProps {
  imageUrl: string | null;
  onClose: () => void;
}


export function ImageLightbox({ imageUrl, onClose }: ImageLightboxProps) {
  useEffect(() => {
    if (!imageUrl) {
      return;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [imageUrl, onClose]);

  if (!imageUrl) {
    return null;
  }

  return (
    <div
      className="lightbox"
      aria-modal="true"
      role="dialog"
      onClick={onClose}
    >
      <button className="lightbox__close" type="button" onClick={onClose}>
        Закрыть
      </button>
      <img
        className="lightbox__image"
        src={imageUrl}
        alt="Opened post visual"
        onClick={(event) => event.stopPropagation()}
      />
    </div>
  );
}
