// =============================================================================
// Design System — init orchestration
//
// One entry point that runs every DS behaviour scoped to a `root`. Called once on
// document ready, and again (scoped to a panel) when a composable tab panel is
// first shown — so modules inserted lazily, or carousels that were measured while
// hidden, initialise / re-measure correctly. Every init is idempotent
// (dataset.dsInit guards), so re-running over already-wired DOM is a no-op.
// =============================================================================

import initAccordions from './accordion';
import initTabs from './tabs';
import initVideoFacades from './video-facade';
import initGalleries from './gallery';
import initMultistepForms from './multistep-form';
import initFormErrors from './form-errors';
import initRegistrationForms from './registration-form';
import initSubscribeForms from './subscribe-form';
import initProgramSpotlights from './program-spotlight';
import initExpertGrids from './expert-grid';
import initRouters from './router';
import initRouterCalendars from './router-calendar';
import initScrollReveal from './scroll-reveal';
import initAudioPlayers from './audio-player';
import initCountdowns from './countdown';
import initReadingProgress from './reading-progress';
import initReadingRails from './reading-rail';
import initHeroPinbars from './hero-pinbar';
import initChapterSeek from './chapter-seek';

// Re-measure any already-initialised Swiper carousels within `root` (a tab panel
// that just became visible). New carousels are handled by initGalleries; this
// catches ones that were built while hidden. observer:true covers most cases —
// this is the explicit belt-and-braces on activation.
function updateCarousels(root) {
  root.querySelectorAll('[data-ds-gallery] .swiper, [data-ds-carousel] .swiper').forEach((el) => {
    if (el.swiper) el.swiper.update();
  });
}

export default function initAll(root = document) {
  initAccordions(root);
  initTabs(root);
  initVideoFacades(root);
  initGalleries(root);
  initMultistepForms(root);
  initFormErrors(root);
  initRegistrationForms(root);
  initSubscribeForms(root);
  initProgramSpotlights(root);
  initExpertGrids(root);
  initRouters(root);
  initRouterCalendars(root);
  initScrollReveal(root);
  initAudioPlayers(root);
  initCountdowns(root);
  initReadingProgress(root);
  initReadingRails(root);
  initHeroPinbars(root);
  initChapterSeek(root);
  if (root !== document) updateCarousels(root);
}
