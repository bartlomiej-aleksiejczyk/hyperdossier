import "../node_modules/markup-refine-lib/dist/markup-refine-lib-interactive-components";
import "./main.css";

import "./components/note-display/NoteDisplay.svelte";
import "./components/searchable-select/SearchableSelect.svelte";
import { GlobalPopover } from "./library/GlobalPopover/GlobalPopover";

document.addEventListener("DOMContentLoaded", () => new GlobalPopover());