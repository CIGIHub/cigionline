import React from 'react';
import ProgramThemeCol from './ProgramThemCol';

const themes = [
  'Data, Economy and Society',
  'AI and Transformative Technology',
  'Digitalization, Security and Democracy',
  'Global Cooperation and Governance',
];
const rowCategories = [3, 6, 10];
const ProgramThemeRow = (props) => {
  const { title, backgroundColour, fontColour, primaryTheme, secondaryTheme } =
    props.row;
  const { rowIndex, activeProgram, handleMouseEnter, handleMouseLeave } = props;

  let cellBgColour;
  const blankCellColour =
    rowIndex <= 3
      ? 'lightest-grey'
      : rowIndex <= 6
      ? 'light-grey'
      : rowIndex <= 10
      ? 'grey'
      : 'dark-grey';

  let cellBeforeBottomSize = '';
  let cellBeforeTopSize = '';
  let rowPaddingY = 'py-1';
  if (rowIndex === 3 || rowIndex === 6 || rowIndex === 10 || rowIndex === 14) {
    cellBeforeBottomSize = 'cell-before-bottom-none';
  }
  if (rowIndex === 0 || rowIndex === 4 || rowIndex === 7 || rowIndex === 11) {
    cellBeforeTopSize = 'cell-before-top-none';
  }
  if (rowIndex === 0) {
    rowPaddingY = 'py-0';
  }

  if (primaryTheme === 'Data, Economy and Society') {
    cellBgColour = ['lightest-grey', 'light-grey', 'grey', 'dark-grey'];
  }
  if (primaryTheme === 'AI and Transformative Technology') {
    cellBgColour = ['light-grey', 'light-grey', 'grey', 'dark-grey'];
  }
  if (primaryTheme === 'Digitalization, Security and Democracy') {
    cellBgColour = ['grey', 'grey', 'grey', 'dark-grey'];
  }
  if (primaryTheme === 'Global Cooperation and Governance') {
    cellBgColour = ['dark-grey', 'dark-grey', 'dark-grey', 'dark-grey'];
  }

  let rowStatus = '';
  if (activeProgram !== null) {
    if (activeProgram === rowIndex) {
      rowStatus = 'active';
    } else {
      rowStatus = 'inactive';
    }
  }

  return (
    <div
      className={`row ${rowPaddingY} program-row ${rowStatus}`}
      onMouseEnter={() => handleMouseEnter(rowIndex)}
      onMouseLeave={handleMouseLeave}
    >
      <div className="col-3 px-1 bg-line">
        <h3
          className={`cell cell-title program-title bg-${backgroundColour} fc-${fontColour}`}
        >
          {title}
        </h3>
      </div>
      <div className="col-1 px-1 bg-line">
        <div
          className={`cell cell-inter cell-blank bg-${blankCellColour} ${cellBeforeBottomSize} ${cellBeforeTopSize}`}
        />
      </div>
      {themes.map((theme, index) => (
        <ProgramThemeCol
          themeType={
            theme === primaryTheme
              ? 'primary'
              : secondaryTheme.includes(theme)
              ? 'secondary'
              : ''
          }
          key={`${theme}-${title}`}
          cellBgColour={cellBgColour[index]}
          rowIndex={rowIndex}
          colIndex={index}
        />
      ))}
    </div>
  );
};

export default ProgramThemeRow;
