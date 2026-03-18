/* jshint esversion: 6 */
(function () {
  'use strict';

  var cfg = window.MEDIAVALET_CONFIG || {};
  var MEDIAVALET_ORIGIN = 'https://assetpicker.mediavalet.com';
  var PICKER_URL =
    cfg.pickerUrl ||
    'https://assetpicker.mediavalet.com?allowedAssetTypes=Image&allowedFeatures=cdnLink&redirectType=popup';
  var IMPORT_URL = cfg.importUrl || '/admin/mediavalet/import/';
  var IMAGE_DATA_URL = cfg.imageDataUrl || '/admin/mediavalet/image-data/';

  /* ------------------------------------------------------------------ */
  /* State                                                                */
  /* ------------------------------------------------------------------ */
  var activeInputId = null;
  var modal = null;
  var modalIframe = null;

  /* ------------------------------------------------------------------ */
  /* Helpers                                                              */
  /* ------------------------------------------------------------------ */
  function getCsrfToken() {
    var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  /* ------------------------------------------------------------------ */
  /* Modal                                                                */
  /* ------------------------------------------------------------------ */
  function buildModal() {
    var dlg = document.createElement('dialog');
    dlg.id = 'mediavalet-chooser-modal';
    dlg.style.cssText = [
      'padding:0',
      'border:none',
      'border-radius:6px',
      'width:90vw',
      'max-width:1200px',
      'height:85vh',
      'flex-direction:column',
      'overflow:hidden',
      'box-shadow:0 8px 32px rgba(0,0,0,.4)',
    ].join(';');

    /* Header */
    var header = document.createElement('div');
    header.style.cssText =
      'display:flex;justify-content:space-between;align-items:center;padding:.625rem 1rem;background:#1a1a1a;color:#fff;flex-shrink:0;';
    header.innerHTML =
      '<span style="font-weight:600;font-size:.95rem;">Choose from MediaValet</span>';

    var closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.textContent = '✕';
    closeBtn.style.cssText =
      'background:none;border:none;color:#fff;font-size:1.2rem;cursor:pointer;padding:0 .25rem;line-height:1;';
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);

    /* Iframe – src is set lazily on first open to avoid an unnecessary load */
    var iframe = document.createElement('iframe');
    iframe.id = 'mediavalet-chooser-iframe';
    iframe.title = 'MediaValet Asset Picker';
    iframe.style.cssText = 'width:100%;flex:1;border:none;';
    iframe.setAttribute(
      'sandbox',
      'allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-forms allow-downloads',
    );
    iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');

    dlg.appendChild(header);
    dlg.appendChild(iframe);

    /* Close on backdrop click */
    dlg.addEventListener('click', function (e) {
      if (e.target === dlg) closeModal();
    });

    document.body.appendChild(dlg);
    modalIframe = iframe;
    return dlg;
  }

  function openModal(inputId) {
    activeInputId = inputId;
    if (!modal) modal = buildModal();

    /* Load iframe src only once so auth state is preserved between opens */
    if (!modalIframe.src || modalIframe.src === 'about:blank') {
      modalIframe.src = PICKER_URL;
    }

    modal.style.display = 'flex';
    modal.showModal();
  }

  function closeModal() {
    if (modal) {
      modal.close();
      modal.style.display = 'none';
    }
    activeInputId = null;
  }

  /* ------------------------------------------------------------------ */
  /* Chooser widget update                                                */
  /* ------------------------------------------------------------------ */
  function updateChooserWidget(inputId, data) {
    // In Wagtail 7 the chooser container is always rendered as {inputId}-chooser
    var containerId = inputId + '-chooser';

    /*
     * Strategy 1 – Telepath / window.chooserWidgets (Wagtail 6 / 7).
     * The widget is registered under the container element ID, not the input ID.
     */
    if (window.chooserWidgets) {
      var widget =
        window.chooserWidgets[containerId] ||
        window.chooserWidgets[inputId] ||
        window.chooserWidgets[inputId.replace(/^id_/, '')];
      if (widget && typeof widget.setState === 'function') {
        widget.setState(data);
        return;
      }
    }

    /*
     * Strategy 2 – Direct DOM manipulation.
     * Covers any Wagtail version by manipulating the rendered widget HTML.
     */
    var container = document.getElementById(containerId);
    if (!container) {
      // Fallback: find container by traversal from the hidden input
      var input = document.getElementById(inputId);
      if (input) container = input.closest('.chooser') || input.parentElement;
    }
    if (!container) return;

    // Update the hidden input value
    var hiddenInput =
      container.querySelector('input[type="hidden"]') || document.getElementById(inputId);
    if (hiddenInput) hiddenInput.value = data.id;

    // Update title
    container.querySelectorAll('[data-chooser-title], .chooser__title').forEach(function (el) {
      el.textContent = data.string || data.title || '';
    });

    // Update edit link
    if (data.edit_link) {
      container.querySelectorAll('a.button--edit, a[href*="/edit/"]').forEach(function (el) {
        el.setAttribute('href', data.edit_link);
      });
    }

    // Update preview image (Wagtail uses data-chooser-image on the <img>)
    if (data.preview) {
      container.querySelectorAll('[data-chooser-image]').forEach(function (img) {
        img.setAttribute('src', data.preview.url);
        if (data.preview.width) img.setAttribute('width', data.preview.width);
        if (data.preview.height) img.setAttribute('height', data.preview.height);
      });
    }

    // Switch from blank → chosen state
    container.classList.remove('blank');

    // Notify any listeners (e.g. Stimulus)
    var target = hiddenInput || container;
    target.dispatchEvent(new Event('change', { bubbles: true }));
  }

  /* ------------------------------------------------------------------ */
  /* Asset handling                                                       */
  /* ------------------------------------------------------------------ */
  function handleAssets(assets) {
    if (!assets.length || !activeInputId) return;

    var inputId = activeInputId;
    var assetItem = assets[0]; // chooser panels accept one image
    var asset = assetItem.asset || {};
    var file = asset.file || {};
    var media = asset.media || {};

    var fileUrl = assetItem.cdnLink || assetItem.link || media.download || '';
    var fileName =
      file.fileName ||
      (fileUrl && fileUrl.split('/').pop().split('?')[0]) ||
      'mediavalet-image.jpg';
    var title = asset.title || file.title || fileName;

    if (!fileUrl) {
      closeModal();
      alert('MediaValet: could not find a download URL for the selected asset.');
      return;
    }

    closeModal();

    fetch(IMPORT_URL, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ file_url: fileUrl, file_name: fileName, title: title }),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (importData) {
        if (!importData.success) {
          alert('MediaValet import failed: ' + (importData.error || 'unknown error'));
          return null;
        }
        return fetch(IMAGE_DATA_URL + importData.image_id + '/', {
          credentials: 'same-origin',
        });
      })
      .then(function (r) {
        return r ? r.json() : null;
      })
      .then(function (chooserData) {
        if (chooserData) updateChooserWidget(inputId, chooserData);
      })
      .catch(function (err) {
        alert('MediaValet error: ' + err);
      });
  }

  /* ------------------------------------------------------------------ */
  /* postMessage listener                                                 */
  /* ------------------------------------------------------------------ */
  window.addEventListener('message', function (event) {
    if (event.origin !== MEDIAVALET_ORIGIN) return;
    if (!event.data || event.data.type !== 'insertedAssets') return;
    var assets = (event.data.payload && event.data.payload.assets) || [];
    handleAssets(assets);
  });

  /* ------------------------------------------------------------------ */
  /* Button initialisation (handles dynamic panels via MutationObserver) */
  /* ------------------------------------------------------------------ */
  function initButtons() {
    document.querySelectorAll('.mediavalet-choose-btn:not([data-mv-init])').forEach(function (btn) {
      btn.setAttribute('data-mv-init', '1');
      btn.addEventListener('click', function () {
        openModal(btn.getAttribute('data-mediavalet-input-id'));
      });
    });
  }

  document.addEventListener('DOMContentLoaded', initButtons);

  if (window.MutationObserver) {
    var observer = new MutationObserver(function (mutations) {
      for (var i = 0; i < mutations.length; i++) {
        if (mutations[i].addedNodes.length) {
          initButtons();
          break;
        }
      }
    });
    document.addEventListener('DOMContentLoaded', function () {
      observer.observe(document.body, { childList: true, subtree: true });
    });
  }
})();
