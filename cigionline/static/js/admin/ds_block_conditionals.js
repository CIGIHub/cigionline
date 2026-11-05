/* Design System admin — conditional fields for module blocks.
 *
 * Telepath counterpart of streams.blocks.ConditionalFieldsMixin: a StructBlock
 * whose meta carries `conditionalFields` ({controller: {value: [fields]}})
 * shows only the fields the controller's current value reveals. Presentation
 * only — hidden fields still submit and keep their values, so switching the
 * toggle back loses nothing. Controllers are selects (ChoiceBlock) or
 * checkboxes (BooleanBlock → 'true'/'false' keys).
 */
(function () {
  'use strict';

  function fieldWrapper(container, name) {
    return container.querySelector('[data-contentpath="' + name + '"]');
  }

  function initConditionals(container, map) {
    Object.keys(map).forEach(function (controller) {
      var wrapper = fieldWrapper(container, controller);
      if (!wrapper) return;
      var input = wrapper.querySelector('select, input[type="checkbox"], input, textarea');
      if (!input) return;

      var valueMap = map[controller];
      var controlled = [];
      Object.keys(valueMap).forEach(function (value) {
        valueMap[value].forEach(function (name) {
          if (controlled.indexOf(name) === -1) controlled.push(name);
        });
      });

      function currentValue() {
        return input.type === 'checkbox' ? String(input.checked) : input.value;
      }

      function sync() {
        var shown = valueMap[currentValue()] || [];
        controlled.forEach(function (name) {
          var el = fieldWrapper(container, name);
          if (el) el.hidden = shown.indexOf(name) === -1;
        });
      }

      input.addEventListener('change', sync);
      sync();
    });
  }

  /* Faceted Listing's facet picker (BugHerd #442): the `facets` multi-select
   * lists every group in the vocabulary, but each card type can only BUILD
   * some of them. Narrow the options to the selected card type's set, from the
   * server's FACETS_BY_CARD_TYPE. Presentation only, like the field toggles
   * above: a hidden option that is already selected still submits, so an older
   * placement keeps its stored value and the server drops what it can't build.
   */
  function initFacetPicker(container, support) {
    var typeWrapper = fieldWrapper(container, 'card_type');
    var facetsWrapper = fieldWrapper(container, 'facets');
    if (!typeWrapper || !facetsWrapper) return;
    var cardType = typeWrapper.querySelector('select');
    var picker = facetsWrapper.querySelector('select');
    if (!cardType || !picker) return;
    var options = Array.prototype.slice.call(picker.options);

    function sync() {
      var allowed = support[cardType.value] || [];
      options.forEach(function (option) {
        option.hidden = allowed.indexOf(option.value) === -1;
      });
    }

    cardType.addEventListener('change', sync);
    sync();
  }

  var StructBlockDefinition = window.wagtailStreamField.blocks.StructBlockDefinition;

  class ConditionalStructBlockDefinition extends StructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
      var block = super.render(placeholder, prefix, initialState, initialError);
      var map = (this.meta && this.meta.conditionalFields) || {};
      if (Object.keys(map).length) {
        // block.container is a jQuery object in Wagtail's StructBlock widget.
        var container = block.container && block.container[0] ? block.container[0] : block.container;
        if (container) initConditionals(container, map);
      }
      return block;
    }
  }

  window.telepath.register('cigionline.blocks.ConditionalStructBlock', ConditionalStructBlockDefinition);

  class FacetedListingStructBlockDefinition extends ConditionalStructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
      var block = super.render(placeholder, prefix, initialState, initialError);
      var support = (this.meta && this.meta.facetSupport) || {};
      var container = block.container && block.container[0] ? block.container[0] : block.container;
      if (container && Object.keys(support).length) initFacetPicker(container, support);
      return block;
    }
  }

  window.telepath.register('cigionline.blocks.FacetedListingStructBlock', FacetedListingStructBlockDefinition);
})();
