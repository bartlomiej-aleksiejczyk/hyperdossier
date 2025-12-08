import { selectedNote } from "../noteStore.svelte.js";

export function noteStoreService() {
  function loadDefaultNote() {
    selectedNote.content = localStorage.getItem("localNote") || "";
  }

  function loadNoteContent() {
    if (!selectedNote.selectedNoteId) return;

    fetch(selectedNote.ajaxNoteEndpoint, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status !== "ok") {
          console.error("Error fetching note:", data);
        } else {
          selectedNote.title = data.result.note_title;
          selectedNote.content = data.result.note_content;
          selectedNote.type = data.result.note_type;
          selectedNote.attachments = data.result.note_attachments || [];
        }
      })
      .catch((err) => console.error("Ajax error:", err));
  }

  function saveNoteContent() {
    if (selectedNote.title === "local~note") {
      localStorage.setItem("localNote", selectedNote.content);
    }

    if (!selectedNote.selectedNoteId) return;
    selectedNote.isSaving = true;
    fetch(selectedNote.ajaxNoteEndpoint, {
      method: "POST",
      headers: {
        "X-CSRFToken": selectedNote.csrfToken,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content: selectedNote.content }),
    })
      .then((response) => response.json())
      .then((data) => {
        selectedNote.isSaving = false;
        if (data.status !== "ok") {
          console.error("Error updating note:", data);
        }
      })
      .catch((err) => {
        console.error("Ajax error:", err);
        selectedNote.isSaving = false;
      });
  }

  return {
    loadDefaultNote,
    loadNoteContent,
    saveNoteContent,
  };
}
