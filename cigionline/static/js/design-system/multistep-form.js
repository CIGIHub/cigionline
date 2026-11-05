// =============================================================================
// Design System — Multi-step form (client-side stepper)
//
// Progressive enhancement for [data-ds-form] forms containing step-break
// markers (see includes/venue_rental_form.html). Fields are grouped into
// steps at each marker; the user pages through them with prev/next, each step
// validated via the constraint API before advancing. One atomic POST at the
// end. Without JS all fields render on one page (server still validates).
// =============================================================================

import { icon } from './templates';

function getCookie(name) {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function makeButton(label, iconName, iconFirst) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'ds-button ds-button--outline ds-button--on-light';
  const labelSpan = document.createElement('span');
  labelSpan.className = 'ds-button__label';
  labelSpan.textContent = label;
  const glyph = icon(iconName);
  const svg = glyph.querySelector('svg');
  if (svg) svg.classList.add('ds-button__icon');
  if (iconFirst) btn.append(glyph, labelSpan);
  else btn.append(labelSpan, glyph);
  return btn;
}

function groupSteps(fields) {
  const steps = [];
  let current = [];
  fields.forEach((f) => {
    if (f.classList.contains('ds-form__field--step-break')) {
      if (current.length) steps.push(current);
      current = [f]; // the break (step heading) opens its step
    } else {
      current.push(f);
    }
  });
  if (current.length) steps.push(current);
  return steps;
}

function firstInvalid(step) {
  for (const f of step) {
    for (const input of f.querySelectorAll('input, select, textarea')) {
      if (!input.checkValidity()) return input;
    }
  }
  return null;
}

function initForm(wrap) {
  if (wrap.dataset.dsInit) return;
  wrap.dataset.dsInit = '1';

  const form = wrap.querySelector('form');
  if (!form) return;

  // The article body is rendered inside a {% cache %} fragment, so the baked-in
  // CSRF token belongs to whoever first warmed the cache — a stale/cross-visitor
  // POST would 403. Overwrite it with the current visitor's cookie token; if
  // the visitor has no cookie yet (pages no longer mint it site-wide — CDN
  // cacheability), fetch the /csrf/ mint endpoint first. Cookie-based CSRF only.
  const refreshToken = () => {
    const cookieToken = getCookie('csrftoken');
    if (cookieToken) {
      form.querySelectorAll('input[name="csrfmiddlewaretoken"]').forEach((input) => {
        input.value = cookieToken;
      });
    }
    return cookieToken;
  };
  if (!refreshToken()) {
    fetch('/csrf/', { credentials: 'same-origin' }).then(refreshToken);
  }

  const fields = [...form.querySelectorAll('[data-ds-field]')];
  const steps = groupSteps(fields);
  if (steps.length < 2) return; // single-step form — CSRF refreshed above; no stepper

  const actions = form.querySelector('[data-ds-form-actions]');
  const submitBtn = actions.querySelector('[type="submit"]');

  // Progress bar: one segment per step (filled up to the current), "Step x of y".
  const progress = document.createElement('div');
  progress.className = 'ds-form__progress';
  const track = document.createElement('div');
  track.className = 'ds-form__progress-track';
  const segs = steps.map(() => {
    const s = document.createElement('span');
    s.className = 'ds-form__progress-seg';
    track.append(s);
    return s;
  });
  const indicator = document.createElement('span');
  indicator.className = 'ds-form__step-indicator';
  indicator.setAttribute('aria-live', 'polite');
  progress.append(track, indicator);
  actions.parentNode.insertBefore(progress, actions);

  const prevBtn = makeButton('Back', 'chevron-left', true);
  const nextBtn = makeButton('Next', 'chevron-right', false);
  actions.prepend(nextBtn);
  actions.prepend(prevBtn);

  let idx = 0;
  function show(i) {
    idx = i;
    steps.forEach((step, si) => step.forEach((f) => { f.hidden = si !== i; }));
    segs.forEach((s, si) => s.classList.toggle('ds-form__progress-seg--filled', si <= i));
    prevBtn.hidden = i === 0;
    nextBtn.hidden = i === steps.length - 1;
    submitBtn.hidden = i !== steps.length - 1;
    indicator.textContent = `Step ${i + 1} of ${steps.length}`;
  }

  nextBtn.addEventListener('click', () => {
    const invalid = firstInvalid(steps[idx]);
    if (invalid) { invalid.reportValidity(); return; }
    show(idx + 1);
    steps[idx][0].scrollIntoView({ block: 'nearest' });
  });
  prevBtn.addEventListener('click', () => show(idx - 1));

  // The form is `novalidate`, so enforce all steps at submit: jump back to the
  // first step containing an invalid field instead of posting.
  form.addEventListener('submit', (event) => {
    for (let i = 0; i < steps.length; i += 1) {
      const invalid = firstInvalid(steps[i]);
      if (invalid) {
        event.preventDefault();
        show(i);
        invalid.reportValidity();
        return;
      }
    }
  });

  // A server-side error re-render (invalid POST) may carry errors on any step;
  // opening step 0 regardless would hide them. Open the first erroring step.
  const errorStep = steps.findIndex((step) =>
    step.some((f) => f.classList.contains('ds-form__field--error') || f.querySelector('.ds-form__field--error')));
  show(errorStep === -1 ? 0 : errorStep);
}

export default function initMultistepForms(root = document) {
  root.querySelectorAll('[data-ds-form]').forEach(initForm);
}
