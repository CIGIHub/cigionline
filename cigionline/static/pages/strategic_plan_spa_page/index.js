import './css/strategic_plan_spa_page.scss';
import React from 'react';
import { createRoot } from 'react-dom/client';
import StrategicPlanSPA from '../../js/components/strategic_plan/StrategicPlanSPA';

const normalizeBasePath = (path) => {
  const url = new URL(path, window.location.origin);
  return url.pathname.replace(/\/$/, '');
};

const strategicPlanSPA = document.getElementById('strategic-plan-spa');
const strategicPlanSPAId = strategicPlanSPA.dataset.strategicPlanId;
const BASE_PATH = strategicPlanSPA.dataset.basePath.replace(/\/$/, '');
const basePath = normalizeBasePath(BASE_PATH);

const root = createRoot(strategicPlanSPA);
root.render(
  <StrategicPlanSPA
    strategicPlanSPAId={strategicPlanSPAId}
    basePath={basePath}
  />,
);
