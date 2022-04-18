export function getLanguage() {
  const locationUrl = window.location.href;
  const splitUrl = locationUrl.split('/');
  return splitUrl.filter((slug) => ['en', 'fr'].indexOf(slug) > -1)[0];
}

export function getCurrentSlug() {
  const locationUrl = window.location.href;
  const splitUrl = locationUrl.split('/');
  return splitUrl.slice(splitUrl.indexOf(getLanguage()) + 1, splitUrl.length)[0];
}

export function getSiteUrl() {
  const locationUrl = window.location.href;
  const splitUrl = locationUrl.split('/');
  return splitUrl.slice(0, splitUrl.indexOf(getLanguage())).join('/');
}

export function getLocationUrl() {
  return window.location.href;
}
