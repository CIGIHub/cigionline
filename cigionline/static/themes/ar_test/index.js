import './css/ar_test.scss';
import * as AFRAME from 'aframe';

require('@ar-js-org/ar.js');

function activateScene() {
  const video = document.getElementById('arjs-video');
  const imgHiro = document.getElementById('img-hiro');
  const aScene = document.getElementById('a-scene');
  video.style.opacity = '1';
  imgHiro.style.display = 'none';
  aScene.style.zIndex = '500';
  aScene.style.opacity = '1';
  console.log('fired');
}

AFRAME.registerComponent('log', {
  schema: { type: 'string' },

  init() {
    const stringToLog = this.data;
    console.log('logged', stringToLog);
    document.getElementById('test-ar').addEventListener('click', activateScene);
  },
});
