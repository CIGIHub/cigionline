import React from 'react';

const ProgramThemeCol = (props) => {
  const { themeType, cellBgColour, rowIndex, colIndex } = props;
  let cellBeforeBottomSize = '';
  let cellBeforeTopSize = '';
  let cellBeforeRightSize = '';
  if (
    (rowIndex === 3 && colIndex === 0) ||
    (rowIndex === 6 && colIndex < 2) ||
    (rowIndex === 10 && colIndex < 3) ||
    rowIndex === 14
  ) {
    cellBeforeBottomSize = 'cell-before-bottom-none';
  }
  if (
    (rowIndex === 4 && colIndex === 0) ||
    (rowIndex === 7 && colIndex < 2) ||
    (rowIndex === 11 && colIndex < 3)
  ) {
    cellBeforeTopSize = 'cell-before-top-none';
  }
  if (rowIndex === 0) {
    cellBeforeTopSize = 'cell-before-top-extra';
  }
  if (
    (rowIndex === 3 && colIndex > 0) ||
    (rowIndex === 6 && colIndex > 1) ||
    (rowIndex === 10 && colIndex > 2)
  ) {
    cellBeforeBottomSize = 'cell-before-bottom-extra';
  }
  if (
    (rowIndex >= 4 && rowIndex <= 6 && colIndex === 0) ||
    (rowIndex >= 7 && rowIndex <= 10 && colIndex < 2) ||
    (rowIndex >= 11 && colIndex < 3)
  ) {
    cellBeforeRightSize = 'cell-before-right-extra';
  }

  return (
    <div className="col-2 px-1 bg-line">
      <div
        className={`cell cell-inter bg-${cellBgColour} ${cellBeforeBottomSize} ${cellBeforeTopSize} ${cellBeforeRightSize}`}
      >
        <span className={themeType} />
      </div>
    </div>
  );
};

export default ProgramThemeCol;
