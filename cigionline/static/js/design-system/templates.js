// =============================================================================
// Design System — template cloning helpers
// Clone hidden <template> fragments rendered server-side in
// includes/ds_js_templates.html, so HTML/SVG stays in templates (not in .js).
// =============================================================================

// Returns a cloned DocumentFragment for the given <template> selector (empty
// fragment if missing, so callers stay safe).
export function cloneTemplate(selector) {
  const tpl = document.querySelector(selector);
  return tpl ? tpl.content.cloneNode(true) : document.createDocumentFragment();
}

// Clone a named DS icon (`[data-ds-icon="<name>"]`). The <svg> is class-less;
// the caller adds its context class.
export function icon(name) {
  return cloneTemplate(`[data-ds-icon="${name}"]`);
}
