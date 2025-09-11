/* eslint react/prop-types: 0 */
/* eslint no-alert: 0 */
const React = window.React;
const RichUtils = window.DraftJS.RichUtils;

/**
 * A React component that renders nothing.
 * We actually create the entities directly in the componentDidMount lifecycle hook.
 */
// Warning: This code uses ES2015+ syntax, it will not work in IE11.
class AnchorSource extends React.Component {
  componentDidMount() {
    const { editorState, entityType, onComplete } = this.props;

    const content = editorState.getCurrentContent();

    // This is very basic – we do not even support editing existing anchors.
    const fragment = window.prompt('Fragment identifier:');

    // Uses the Draft.js API to create a new entity with the right data.
    const contentWithEntity = content.createEntity(
      entityType.type,
      'MUTABLE',
      {
        fragment,
      },
    );
    const entityKey = contentWithEntity.getLastCreatedEntityKey();
    const selection = editorState.getSelection();
    const nextState = RichUtils.toggleLink(
      editorState,
      selection,
      entityKey,
    );

    onComplete(nextState);
  }

  render() {
    return null;
  }
}

function Anchor(props) {
  const { entityKey, children, contentState } = props;
  const data = contentState.getEntity(entityKey).getData();

  return React.createElement(
    'a',
    {
      role: 'button',
      name: data.fragment,
      onMouseUp: () => {
        window.alert(data.fragment);
      },
    },
    children,
  );
}

window.draftail.registerPlugin({
  type: 'ANCHOR',
  source: AnchorSource,
  decorator: Anchor,
});
