export const selectedNote = $state({
  content: "",
  title: undefined,
  type: undefined,
  attachments: [],
  ajaxNoteEndpoint: undefined,
  selectedNoteId: undefined,
  csrfToken: undefined,
  isSaving: false,
});
