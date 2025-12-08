<script>
  import { selectedNote } from "../noteStore.svelte.js";
  const { children } = $props();
</script>

<div class="notes-display">
  {#if selectedNote.title && selectedNote.selectedNoteId}
    <details class="note-meta">
      <summary>
        <span class="note-meta__title">{selectedNote.title}</span>

        <svg
          xmlns="http://www.w3.org/2000/svg"
          height="20"
          viewBox="0 -960 960 960"
          width="20"
          class="note-meta__chevron"
        >
          <path d="M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z" />
        </svg>
      </summary>

      <div class="note-meta__content">
        {#if selectedNote.attachments?.length}
          <h4>Attachments</h4>
          <ul>
            {#each selectedNote.attachments as att}
              <li><a href={att.url} target="_blank">{att.name}</a></li>
            {/each}
          </ul>
        {/if}

        {#if selectedNote.note_updated_at}
          <p class="note-meta__timestamp">
            Updated: {selectedNote.note_updated_at}
          </p>
        {/if}
      </div>
    </details>

    {@render children()}
  {:else}
    <div class="notes-display__no-content">
      <h3>Select a note to see details.</h3>
    </div>
  {/if}
</div>

<style>
  .notes-display {
    max-width: 100%;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    flex-grow: 1;
    align-self: stretch;
  }

  /* Collapsible container */
  .note-meta {
    background: var(--color-main-text-area);
    color: var(--color-main-text);
    border: none;
    padding: 0.25rem 0;
    margin: 0;
    width: 100%;
  }

  /* Summary layout */
  .note-meta summary {
    padding: 0 0 0 0.25rem;
    font-size: 1.3rem;

    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;

    cursor: pointer;
    list-style: none;
  }

  /* Remove default marker */
  .note-meta summary::-webkit-details-marker {
    display: none;
  }

  /* Title text */
  .note-meta__title {
    flex: 1;
  }

  /* Chevron behavior */
  .note-meta__chevron {
    transition: transform 0.25s ease;
    opacity: 0.7;
  }

  /* Rotate chevron when details is open */
  .note-meta[open] .note-meta__chevron {
    transform: rotate(180deg);
  }

  .note-meta__content {
    h4 {
      margin: 0 0.25rem;
    }
    ul {
      margin: 0;
      overflow: auto;
    }
  }

  .note-meta__timestamp {
    opacity: 0.7;
    font-size: 0.85rem;
  }

  .notes-display__no-content {
    justify-content: center;
    display: flex;
    align-items: center;
    flex: 1;
    align-self: stretch;
    text-align: center;
  }
</style>
