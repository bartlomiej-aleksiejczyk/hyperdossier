<script>
  import { onMount } from "svelte";
  import { noteStoreService } from "../services/noteStoreService.svelte.js";
  import { selectedNote } from "../noteStore.svelte.js";

  const { saveNoteContent } = noteStoreService();

  let debounceTimer = null;
  let textareaEl;

  function autoResize() {
    if (!textareaEl) return;
    textareaEl.style.height = "auto";
    textareaEl.style.height = textareaEl.scrollHeight + "px";
  }

  function debounceSave() {
    selectedNote.isSaving = true;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(saveNoteContent, 1000);
  }

  function handleInput() {
    autoResize();
    debounceSave();
  }

  onMount(() => {
    autoResize();
  });
</script>

<div class="notes-display__content">
  <textarea
    bind:this={textareaEl}
    bind:value={selectedNote.content}
    class="notes-display__textarea"
    on:input={handleInput}
  ></textarea>
</div>

<style>
  .notes-display__content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-self: stretch;
  }

  .notes-display__textarea {
    /* let JS control height */
    width: 100%;
    box-sizing: border-box;
    resize: none;
    overflow: hidden; /* important for clean autoresize */
    margin-bottom: 2rem;
    min-height: 3rem; /* optional: base height */
    flex: 0 0 auto; /* don't stretch, grow with content instead */
  }

  .notes-display__textarea:focus {
    outline-color: transparent;
  }

  @media (max-width: 992px) {
    .notes-display__textarea {
      margin-bottom: 0;
    }
  }
</style>
