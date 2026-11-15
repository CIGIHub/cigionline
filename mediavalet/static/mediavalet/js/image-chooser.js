/* jshint esversion: 6 */
(function () {
  'use strict';

  var cfg = window.MEDIAVALET_CONFIG || {};
  var PICKER_URL =
    cfg.pickerUrl ||
    'https://assetpicker.mediavalet.com?allowedAssetTypes=Image&allowedFeatures=cdnLink&redirectType=popup';
  var MEDIAVALET_ORIGIN = new URL(PICKER_URL, window.location.href).origin;
  var IMPORT_URL = cfg.importUrl || '/admin/mediavalet/import/';
  var IMAGE_DATA_URL = cfg.imageDataUrl || '/admin/mediavalet/image-data/';

  var activeInputId = null;
  var modal = null;
  var modalIframe = null;

  function getCsrfToken() {
    var match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function buildModal() {
    var dialog = document.createElement('dialog');
    dialog.id = 'mediavalet-chooser-modal';
    dialog.style.cssText = [
      'padding:0',
      'border:none',
      'border-radius:6px',
      'width:90vw',
      'max-width:2000px',
      'height:85vh',
      'flex-direction:column',
      'overflow:hidden',
      'box-shadow:0 8px 32px rgba(0,0,0,.4)',
    ].join(';');

    var header = document.createElement('div');
    header.style.cssText =
      'display:flex;justify-content:space-between;align-items:center;padding:.625rem 1rem;background:#1a1a1a;color:#fff;flex-shrink:0;';
    header.innerHTML =
      '<span style="font-weight:600;font-size:.95rem;">Choose from MediaValet</span>';

    var closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.setAttribute('aria-label', 'Close');
    closeButton.textContent = '✕';
    closeButton.style.cssText =
      'background:none;border:none;color:#fff;font-size:1.2rem;cursor:pointer;padding:0 .25rem;line-height:1;';
    closeButton.addEventListener('click', closeModal);
    header.appendChild(closeButton);

    var iframe = document.createElement('iframe');
    iframe.id = 'mediavalet-chooser-iframe';
    iframe.title = 'MediaValet Asset Picker';
    iframe.style.cssText = 'width:100%;flex:1;border:none;';
    iframe.setAttribute(
      'sandbox',
      'allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-forms allow-downloads',
    );
    iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');

    dialog.appendChild(header);
    dialog.appendChild(iframe);
    dialog.addEventListener('click', function (event) {
      if (event.target === dialog) closeModal();
    });

    document.body.appendChild(dialog);
    modalIframe = iframe;
    return dialog;
  }

  function openModal(inputId) {
    activeInputId = inputId;
    if (!modal) modal = buildModal();
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

  function updateChooserWidget(inputId, data) {
    var containerId = inputId + '-chooser';
    var container = document.getElementById(containerId);

    if (container && container.widget && typeof container.widget.setState === 'function') {
      container.widget.setState(data);
      return;
    }

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

    if (!container) {
      var input = document.getElementById(inputId);
      if (input) container = input.closest('.chooser') || input.parentElement;
    }
    if (!container) return;

    var hiddenInput =
      container.querySelector('input[type="hidden"]') || document.getElementById(inputId);
    if (hiddenInput) hiddenInput.value = data.id;

    container.querySelectorAll('[data-chooser-title], .chooser__title').forEach(function (element) {
      element.textContent = data.string || data.title || '';
    });

    if (data.edit_link) {
      container
        .querySelectorAll('[data-chooser-edit-link], a.button--edit, a[href*="/edit/"]')
        .forEach(function (element) {
          element.setAttribute('href', data.edit_link);
          element.hidden = false;
        });
    }

    if (data.preview) {
      container.querySelectorAll('[data-chooser-image]').forEach(function (image) {
        image.setAttribute('src', data.preview.url);
        if (data.preview.width) image.setAttribute('width', data.preview.width);
        if (data.preview.height) image.setAttribute('height', data.preview.height);
        image.setAttribute('data-default-alt-text', data.default_alt_text || '');
      });
    }

    container.classList.remove('blank');
    var target = hiddenInput || container;
    target.dispatchEvent(new window.Event('change', { bubbles: true }));
  }

  function handleAssets(assets) {
    if (!assets.length || !activeInputId) return;

    var inputId = activeInputId;
    var assetItem = assets[0];
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
      window.alert('MediaValet: could not find a download URL for the selected asset.');
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
      .then(function (response) {
        return response.json();
      })
      .then(function (importData) {
        if (!importData.success) {
          window.alert('MediaValet import failed: ' + (importData.error || 'unknown error'));
          return null;
        }
        return fetch(IMAGE_DATA_URL + importData.image_id + '/', {
          credentials: 'same-origin',
        });
      })
      .then(function (response) {
        return response ? response.json() : null;
      })
      .then(function (chooserData) {
        if (chooserData) updateChooserWidget(inputId, chooserData);
      })
      .catch(function (error) {
        window.alert('MediaValet error: ' + error);
      });
  }

  window.addEventListener('message', function (event) {
    if (event.origin !== MEDIAVALET_ORIGIN) return;
    if (!modalIframe || event.source !== modalIframe.contentWindow) return;
    if (!event.data || event.data.type !== 'insertedAssets') return;
    var assets = (event.data.payload && event.data.payload.assets) || [];
    handleAssets(assets);
  });

  function initButtons() {
    document
      .querySelectorAll('.mediavalet-choose-btn:not([data-mv-init])')
      .forEach(function (button) {
        button.setAttribute('data-mv-init', '1');
        button.addEventListener('click', function () {
          openModal(button.getAttribute('data-mediavalet-input-id'));
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
